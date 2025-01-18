from sqlalchemy.orm import Session
from database.models import Brand
from schemas.brand import BrandCreate


def create_brand(db: Session, brand: BrandCreate):
    db_brand = Brand(**brand.model_dump())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


def get_brand(db: Session, brand_name: str):
    return db.query(Brand).filter(Brand.name == brand_name).first()


def get_brands(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Brand).offset(skip).limit(limit).all()
