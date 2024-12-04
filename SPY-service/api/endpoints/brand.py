from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud.brand import create_brand, get_brand, get_brands
from schemas.brand import Brand, BrandCreate
from ..dependencies import get_db

router = APIRouter()


@router.post("/", response_model=Brand)
def create_brand_endpoint(brand: BrandCreate, db: Session = Depends(get_db)):
    return create_brand(db=db, brand=brand)


@router.get("/{brand_id}", response_model=Brand)
def get_brand_endpoint(brand_id: int, db: Session = Depends(get_db)):
    db_brand = get_brand(db=db, brand_id=brand_id)
    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return db_brand


@router.get("/", response_model=list[Brand])
def get_brands_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_brands(db=db, skip=skip, limit=limit)
