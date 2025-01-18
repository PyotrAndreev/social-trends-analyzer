from fastapi import APIRouter, HTTPException
from database.db_API import DBAPI
from schemas.product import Product, ProductCreate

router = APIRouter()

@router.post("/", response_model=Product)
def create_product_endpoint(product: ProductCreate):
    with DBAPI() as db_api:
        return db_api.create_product(product)

@router.get("/{product_id}", response_model=Product)
def get_product_endpoint(product_name: str):
    with DBAPI() as db_api:
        db_product = db_api.get_product(product_name)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        return db_product

@router.get("/", response_model=list[Product])
def get_products_endpoint(skip: int = 0, limit: int = 100):
    with DBAPI() as db_api:
        return db_api.get_products(skip=skip, limit=limit)