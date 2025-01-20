from pydantic import BaseModel
from typing import List
from datetime import datetime
from SPY_service.schemas.advertisement import Advertisement


class ProductBase(BaseModel):
    name: str
    brand_name: str
    last_update: datetime
    advertisements: List["Advertisement"] = []


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class Product(ProductBase):
    name: str
    brand_name: str
    last_update: datetime
    advertisements: List["Advertisement"] = []

    class Config:
        from_attributes = True
