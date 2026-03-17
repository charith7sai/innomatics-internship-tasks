from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from math import ceil

app = FastAPI()

# --- Initial Data ---
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"},
]

orders = []

# --- Pydantic Model for Orders (To populate data) ---
class OrderCreate(BaseModel):
    customer_name: str
    product_name: str
    total_price: int

# --- SEARCH & SORT ENDPOINTS (Placed ABOVE /{product_id}) ---

@app.get("/products/search")
def search_products(keyword: str = Query(..., min_length=1)):
    results = [p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message": f"No products found for: {keyword}"}
    return {"keyword": keyword, "total_found": len(results), "products": results}

@app.get("/products/sort")
def sort_products(
    sort_by: str = Query("price", pattern="^(price|name)$"),
    order: str = Query("asc", pattern="^(asc|desc)$")
):
    is_reverse = (order == "desc")
    # Validation for sort_by is handled by the 'pattern' in Query
    result = sorted(products, key=lambda p: p[sort_by], reverse=is_reverse)
    return {"sort_by": sort_by, "order": order, "products": result}

@app.get("/products/page")
def get_products_paged(
    page: int = Query(1, ge=1),
    limit: int = Query(2, ge=1, le=10)
):
    start = (page - 1) * limit
    total = len(products)
    paged_data = products[start : start + limit]
    return {
        "page": page,
        "limit": limit,
        "total_pages": ceil(total / limit),
        "products": paged_data
    }

# --- Q4: Search Orders ---
@app.get("/orders/search")
def search_orders(customer_name: str = Query(..., min_length=1)):
    results = [o for o in orders if customer_name.lower() in o["customer_name"].lower()]
    if not results:
        return {"message": f"No orders found for: {customer_name}"}
    return {"customer_name": customer_name, "total_found": len(results), "orders": results}

# --- Q5: Advanced Sort (Category + Price) ---
@app.get("/products/sort-by-category")
def sort_by_category():
    # Sorts by category A-Z, then price Low-High within that category
    result = sorted(products, key=lambda p: (p['category'], p['price']))
    return {"message": "Sorted by category then price", "products": result}

# --- Q6: Master Browse Endpoint ---
@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = Query(None),
    sort_by: str = Query("price", pattern="^(price|name)$"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=20)
):
    # 1. Filter
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]
    
    # 2. Sort
    result = sorted(result, key=lambda p: p[sort_by], reverse=(order == "desc"))
    
    # 3. Paginate
    total = len(result)
    start = (page - 1) * limit
    paged_result = result[start : start + limit]
    
    return {
        "metadata": {
            "keyword": keyword, "sort_by": sort_by, "order": order,
            "page": page, "limit": limit, "total_found": total,
            "total_pages": ceil(total / limit) if total > 0 else 0
        },
        "products": paged_result
    }

# --- Bonus: Paginate Orders ---
@app.get("/orders/page")
def get_orders_paged(page: int = Query(1, ge=1), limit: int = Query(3, ge=1)):
    start = (page - 1) * limit
    return {
        "page": page, "limit": limit, "total_orders": len(orders),
        "total_pages": ceil(len(orders) / limit),
        "orders": orders[start : start + limit]
    }

# --- Standard Endpoints ---

@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.post("/orders")
def create_order(order: OrderCreate):
    new_order = order.dict()
    new_order["order_id"] = len(orders) + 1
    orders.append(new_order)
    return {"message": "Order created", "order": new_order}
