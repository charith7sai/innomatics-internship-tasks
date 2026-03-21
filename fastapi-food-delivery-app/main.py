from fastapi import FastAPI, HTTPException, Query, status, Response
from pydantic import BaseModel, Field
from typing import Optional, List
import math

app = FastAPI()

# --- DATA STORAGE (Day 1 & 5) ---
menu = [
    {"id": 1, "name": "Margherita Pizza", "price": 299, "category": "Pizza", "is_available": True},
    {"id": 2, "name": "Veg Burger", "price": 149, "category": "Burger", "is_available": True},
    {"id": 3, "name": "Iced Coffee", "price": 99, "category": "Drink", "is_available": True},
    {"id": 4, "name": "Chocolate Brownie", "price": 129, "category": "Dessert", "is_available": False},
    {"id": 5, "name": "Pasta Alfredo", "price": 349, "category": "Pasta", "is_available": True},
    {"id": 6, "name": "Coke", "price": 49, "category": "Drink", "is_available": True},
]
orders = []
cart = []
order_counter = 1

# --- PYDANTIC MODELS (Day 2, 4 & 5) ---
class OrderRequest(BaseModel): # Q6
    customer_name: str = Field(..., min_length=2)
    item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=20)
    delivery_address: str = Field(..., min_length=10)
    order_type: str = "delivery" # Q9

class NewMenuItem(BaseModel): # Q11
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    is_available: bool = True

class CheckoutRequest(BaseModel): # Q15
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

# --- HELPER FUNCTIONS (Day 3) ---
def find_menu_item(item_id: int): # Q7
    return next((item for item in menu if item["id"] == item_id), None)

def calculate_bill(price: int, quantity: int, order_type: str): # Q7
    total = price * quantity
    if order_type == "delivery": # Q9
        total += 30 
    return total

def filter_menu_logic(category: str, max_price: int, is_available: bool): # Q10
    filtered = menu
    if category is not None:
        filtered = [i for i in filtered if i["category"].lower() == category.lower()]
    if max_price is not None:
        filtered = [i for i in filtered if i["price"] <= max_price]
    if is_available is not None:
        filtered = [i for i in filtered if i["is_available"] == is_available]
    return filtered

# --- DAY 1-6 ENDPOINTS ---

@app.get("/") # Q1
async def home():
    return {"message": "Welcome to QuickBite Food Delivery"}

@app.get("/menu/summary") # Q5
async def get_menu_summary():
    return {
        "total_items": len(menu),
        "available": len([i for i in menu if i["is_available"]]),
        "unavailable": len([i for i in menu if not i["is_available"]]),
        "categories": list(set(i["category"] for i in menu))
    }

@app.get("/menu/filter") # Q10
async def filter_menu(category: Optional[str] = None, max_price: Optional[int] = None, is_available: Optional[bool] = None):
    results = filter_menu_logic(category, max_price, is_available)
    return {"results": results, "count": len(results)}

@app.get("/menu/search") # Q16
async def search_menu(keyword: str):
    results = [i for i in menu if keyword.lower() in i["name"].lower() or keyword.lower() in i["category"].lower()]
    if not results: return {"message": "No items found"}
    return {"results": results, "total_found": len(results)}

@app.get("/menu/sort") # Q17
async def sort_menu(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name", "category"]:
        raise HTTPException(status_code=400, detail="Invalid sort field")
    reverse = (order == "desc")
    sorted_list = sorted(menu, key=lambda x: x[sort_by], reverse=reverse)
    return {"sorted_menu": sorted_list, "applied": f"{sort_by} {order}"}

@app.get("/menu/page") # Q18
async def paginate_menu(page: int = Query(1, ge=1), limit: int = Query(3, ge=1, le=10)):
    start = (page - 1) * limit
    paginated_items = menu[start : start + limit]
    return {
        "page": page, "limit": limit, "total": len(menu),
        "total_pages": math.ceil(len(menu) / limit),
        "items": paginated_items
    }

@app.get("/menu/browse") # Q20
async def browse_menu(keyword: Optional[str] = None, sort_by: str = "price", order: str = "asc", page: int = 1, limit: int = 4):
    filtered = [i for i in menu if keyword.lower() in i["name"].lower()] if keyword else menu
    sorted_list = sorted(filtered, key=lambda x: x[sort_by], reverse=(order == "desc"))
    start = (page - 1) * limit
    return {"items": sorted_list[start : start + limit], "metadata": {"page": page, "total": len(sorted_list)}}

@app.get("/orders/search") # Q19
async def search_orders(customer_name: str):
    results = [o for o in orders if customer_name.lower() in o["customer"].lower()]
    return {"results": results}

@app.get("/orders/sort") # Q19
async def sort_orders(order: str = "asc"):
    reverse = (order == "desc")
    return sorted(orders, key=lambda x: x["total"], reverse=reverse)

@app.get("/cart") # Q14
async def view_cart():
    return {"cart": cart, "grand_total": sum(i["subtotal"] for i in cart)}

@app.get("/menu") # Q2
async def get_all_menu():
    return {"menu": menu, "total": len(menu)}

@app.get("/menu/{item_id}") # Q3
async def get_item_by_id(item_id: int):
    item = find_menu_item(item_id)
    return item if item else {"error": "Item not found"}

@app.get("/orders") # Q4
async def get_all_orders():
    return {"orders": orders, "total_orders": len(orders)}

@app.post("/orders") # Q8
async def create_order(request: OrderRequest):
    global order_counter
    item = find_menu_item(request.item_id)
    if not item or not item["is_available"]:
        raise HTTPException(status_code=400, detail="Item unavailable")
    bill = calculate_bill(item["price"], request.quantity, request.order_type)
    new_order = {"order_id": order_counter, "customer": request.customer_name, "total": bill}
    orders.append(new_order)
    order_counter += 1
    return new_order

@app.post("/menu", status_code=201) # Q11
async def add_item(item: NewMenuItem, response: Response):
    if any(i["name"].lower() == item.name.lower() for i in menu):
        raise HTTPException(status_code=400, detail="Duplicate name")
    new_id = max(i["id"] for i in menu) + 1
    new_obj = {"id": new_id, **item.dict()}
    menu.append(new_obj)
    return new_obj

@app.put("/menu/{item_id}") # Q12
async def update_item(item_id: int, price: Optional[int] = None, is_available: Optional[bool] = None):
    item = find_menu_item(item_id)
    if not item: raise HTTPException(status_code=404)
    if price is not None: item["price"] = price
    if is_available is not None: item["is_available"] = is_available
    return item

@app.delete("/menu/{item_id}") # Q13
async def delete_item(item_id: int):
    item = find_menu_item(item_id)
    if not item: raise HTTPException(status_code=404)
    menu.remove(item)
    return {"message": f"Deleted {item['name']}"}

@app.post("/cart/add") # Q14
async def add_to_cart(item_id: int, quantity: int = 1):
    item = find_menu_item(item_id)
    if not item or not item["is_available"]: raise HTTPException(status_code=400)
    for c in cart:
        if c["id"] == item_id:
            c["quantity"] += quantity
            c["subtotal"] = c["quantity"] * item["price"]
            return {"message": "Updated cart"}
    cart.append({"id": item_id, "name": item["name"], "quantity": quantity, "subtotal": item["price"] * quantity})
    return {"message": "Added to cart"}

@app.delete("/cart/{item_id}") # Q15
async def remove_from_cart(item_id: int):
    global cart
    cart = [i for i in cart if i["id"] != item_id]
    return {"message": "Item removed"}

@app.post("/cart/checkout", status_code=201) # Q15
async def checkout(req: CheckoutRequest):
    global order_counter
    if not cart: raise HTTPException(status_code=400, detail="Empty cart")
    placed = []
    for i in cart:
        order = {"order_id": order_counter, "customer": req.customer_name, "item": i["name"], "total": i["subtotal"]}
        orders.append(order)
        placed.append(order)
        order_counter += 1
    cart.clear()
    return {"placed_orders": placed, "grand_total": sum(o["total"] for o in placed)}
