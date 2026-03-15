from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# --- Mock Database ---
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

cart = []
orders = []

# --- Pydantic Models ---
class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

# --- Cart Endpoints ---

@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}
    
    grand_total = sum(item["subtotal"] for item in cart)
    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = Query(1, gt=0)):
    # 1. Find the product
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # 2. Check stock (Q3)
    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")
    
    # 3. Check if already in cart (Q4)
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]
            return {"message": "Cart updated", "cart_item": item}
    
    # 4. Add as new item
    cart_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }
    cart.append(cart_item)
    return {"message": "Added to cart", "cart_item": cart_item}

@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    global cart
    item = next((i for i in cart if i["product_id"] == product_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    cart = [i for i in cart if i["product_id"] != product_id]
    return {"message": f"Removed {item['product_name']} from cart"}

@app.post("/cart/checkout")
def checkout(request: CheckoutRequest):
    # Bonus: Check if cart is empty
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")
    
    placed_orders = []
    grand_total = sum(item["subtotal"] for item in cart)
    
    # Process each cart item into the orders list
    for item in cart:
        order_id = len(orders) + 1
        order_entry = {
            "order_id": order_id,
            "customer_name": request.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }
        orders.append(order_entry)
        placed_orders.append(order_entry)
    
    # Clear the cart (Q5)
    cart.clear()
    
    return {
        "message": "Order placed successfully",
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }

@app.get("/orders")
def get_orders():
    return {"orders": orders, "total_orders": len(orders)}
