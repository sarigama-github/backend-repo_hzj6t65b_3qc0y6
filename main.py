import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="Helioskin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Helioskin backend running"}

@app.get("/schema")
def get_schema():
    return {
        "collections": [
            "user",
            "product",
            "order",
        ]
    }

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# Seed products (10 premium men's skincare items)
SEED_PRODUCTS: List[Product] = [
    Product(slug="purifying-face-wash", name="Purifying Face Wash", description="Sulfate-free daily cleanser for men.", price=19.90, size_ml=150, skin_type="All", ingredients=["Aloe Vera", "Niacinamide"], image="https://images.unsplash.com/photo-1608248597279-d8b8746e67d1?w=800&q=80", in_stock=True),
    Product(slug="revitalizing-moisturizer", name="Revitalizing Moisturizer", description="Kevyt kosteusvoide päivittäiseen käyttöön.", price=29.90, size_ml=75, skin_type="Normal/Oily", ingredients=["Hyaluronic Acid", "Vitamin E"], image="https://images.unsplash.com/photo-1609840114035-10affa6b8a12?w=800&q=80", in_stock=True),
    Product(slug="age-defense-serum", name="Age Defense Serum", description="Peptidipitoinen ikääntymistä ehkäisevä seerumi.", price=49.90, size_ml=30, skin_type="All", ingredients=["Peptides", "Retinal"], image="https://images.unsplash.com/photo-1585238342028-4bbc5b9b3a3b?w=800&q=80", in_stock=True),
    Product(slug="energizing-eye-cream", name="Energizing Eye Cream", description="Virkistävä silmänympärysvoide kofeiinilla.", price=24.90, size_ml=15, skin_type="All", ingredients=["Caffeine", "Niacinamide"], image="https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=800&q=80", in_stock=True),
    Product(slug="post-shave-balm", name="Post-Shave Balm", description="Rauhoittava after shave -balsami.", price=22.90, size_ml=100, skin_type="All", ingredients=["Allantoin", "Panthenol"], image="https://images.unsplash.com/photo-1585386959984-a4155223168f?w=800&q=80", in_stock=True),
    Product(slug="deep-clean-charcoal-mask", name="Deep Clean Charcoal Mask", description="Syväpuhdistava hiilinaamio.", price=27.90, size_ml=75, skin_type="Oily/Combination", ingredients=["Charcoal", "Kaolin"], image="https://images.unsplash.com/photo-1585238342164-1a7f6eb3b2db?w=800&q=80", in_stock=True),
    Product(slug="ultra-protect-spf50", name="Ultra Protect SPF50", description="Laajakirjoinen mineraaliaurinkosuoja.", price=32.90, size_ml=50, skin_type="All", ingredients=["Zinc Oxide", "Vitamin C"], image="https://images.unsplash.com/photo-1619784691579-94b2071ca92b?w=800&q=80", in_stock=True),
    Product(slug="beard-conditioning-oil", name="Beard Conditioning Oil", description="Partaöljy pehmeyttä ja kiiltoa varten.", price=21.90, size_ml=30, skin_type="All", ingredients=["Argan Oil", "Jojoba Oil"], image="https://images.unsplash.com/photo-1595152452543-e5fc28ebc2b8?w=800&q=80", in_stock=True),
    Product(slug="clarifying-toner", name="Clarifying Toner", description="Ihoa tasapainottava BHA-toner.", price=18.90, size_ml=200, skin_type="Oily/Acne-prone", ingredients=["Salicylic Acid", "Green Tea"], image="https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=800&q=80", in_stock=True),
    Product(slug="nourishing-night-cream", name="Nourishing Night Cream", description="Ravitseva yövoide palautumiseen.", price=34.90, size_ml=50, skin_type="Dry/Normal", ingredients=["Ceramides", "Squalane"], image="https://images.unsplash.com/photo-1585238342028-4bbc5b9b3a3b?w=800&q=80", in_stock=True),
]

@app.get("/products", response_model=List[Product])
def list_products():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")

    existing = db["product"].count_documents({})
    if existing == 0:
        for p in SEED_PRODUCTS:
            create_document("product", p)

    docs = get_documents("product", {})
    products: List[Product] = []
    for d in docs:
        products.append(Product(
            slug=d.get("slug"),
            name=d.get("name"),
            description=d.get("description"),
            price=float(d.get("price", 0)),
            size_ml=d.get("size_ml"),
            skin_type=d.get("skin_type"),
            ingredients=d.get("ingredients"),
            image=d.get("image"),
            in_stock=bool(d.get("in_stock", True)),
            rating=float(d.get("rating", 4.8)),
        ))
    return products

@app.get("/products/{slug}", response_model=Product)
def get_product(slug: str):
    d = db["product"].find_one({"slug": slug})
    if not d:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(
        slug=d.get("slug"),
        name=d.get("name"),
        description=d.get("description"),
        price=float(d.get("price", 0)),
        size_ml=d.get("size_ml"),
        skin_type=d.get("skin_type"),
        ingredients=d.get("ingredients"),
        image=d.get("image"),
        in_stock=bool(d.get("in_stock", True)),
        rating=float(d.get("rating", 4.8)),
    )

@app.post("/orders")
def create_order(order: Order):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    for item in order.items:
        prod = db["product"].find_one({"slug": item.slug})
        if not prod:
            raise HTTPException(status_code=400, detail=f"Invalid product: {item.slug}")
    order_id = create_document("order", order)
    return {"order_id": order_id, "status": "received"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
