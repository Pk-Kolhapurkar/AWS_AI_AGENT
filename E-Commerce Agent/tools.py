# tools.py
import uuid
import json
from catalog import PRODUCTS, find_product

# In-memory order store
ORDERS = {}

def recommend_products(prompt: str) -> dict:
    """Suggest products from the catalog based on a shopper's request."""
    prompt_lower = prompt.lower()
    matches = []
    for p in PRODUCTS:
        if (p["category"].lower() in prompt_lower
                or p["name"].lower() in prompt_lower
                or any(word in prompt_lower for word in p["description"].lower().split())):
            matches.append(p)
    if not matches:
        matches = PRODUCTS[:3]
    return {"recommendations": matches}

def place_order(product_id: str, quantity: int) -> dict:
    """Place an order for a product with the given quantity."""
    product = find_product(product_id)
    if not product:
        return {"error": f"Product {product_id} not found"}
    order_id = str(uuid.uuid4())
    ORDERS[order_id] = {
        "order_id": order_id,
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": int(quantity),
        "total": product["price"] * int(quantity),
        "status": "CONFIRMED",
    }
    return {"order_id": order_id, "status": "CONFIRMED", "details": ORDERS[order_id]}

def get_order(order_id: str) -> dict:
    """Look up the status of an existing order by its order id."""
    order = ORDERS.get(order_id)
    if not order:
        return {"error": f"Order {order_id} not found"}
    return {"order_id": order_id, "status": order["status"], "details": order}