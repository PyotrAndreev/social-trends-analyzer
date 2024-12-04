from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud.product import create_product, get_product, get_products
from schemas.product import Product, ProductCreate
from ..dependencies import get_db

router = APIRouter()


@router.post("/", response_model=Product)
def create_product_endpoint(product: ProductCreate, db: Session = Depends(get_db)):
    return create_product(db=db, product=product)


@router.get("/{product_id}", response_model=Product)
def get_product_endpoint(product_id: int, db: Session = Depends(get_db)):
    db_product = get_product(db=db, product_id=product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


@router.get("/", response_model=list[Product])
def get_products_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_products(db=db, skip=skip, limit=limit)
