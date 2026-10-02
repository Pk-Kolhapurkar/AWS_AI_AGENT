# catalog.py
PRODUCTS = [
    {
        "product_id": "101",
        "name": "Running Shoes",
        "category": "Shoes",
        "price": 89.99,
        "description": "Lightweight running shoes with breathable mesh.",
    },
    {
        "product_id": "102",
        "name": "Basketball Shoes",
        "category": "Shoes",
        "price": 119.99,
        "description": "High-top basketball shoes with ankle support.",
    },
    {
        "product_id": "201",
        "name": "Wireless Earbuds",
        "category": "Electronics",
        "price": 49.99,
        "description": "Bluetooth 5.3 earbuds with 24h battery life.",
    },
    {
        "product_id": "202",
        "name": "Smart Watch",
        "category": "Electronics",
        "price": 149.99,
        "description": "Fitness tracking smart watch with AMOLED display.",
    },
    {
        "product_id": "301",
        "name": "Coffee Maker",
        "category": "Home",
        "price": 69.99,
        "description": "12-cup programmable coffee maker.",
    },
    {
        "product_id": "302",
        "name": "Air Fryer",
        "category": "Home",
        "price": 99.99,
        "description": "5.8QT digital air fryer with 8 presets.",
    },
]

FEATURED_PRODUCTS = [PRODUCTS[0], PRODUCTS[2], PRODUCTS[3]]

def format_price(price):
    return f"${price:.2f}"

def all_categories():
    return sorted({p["category"] for p in PRODUCTS})

def find_product(product_id):
    for p in PRODUCTS:
        if p["product_id"] == str(product_id):
            return p
    return None