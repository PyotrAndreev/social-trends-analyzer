from pydantic import BaseModel
from typing import List
from SPY_service.schemas.product import Product
from datetime import datetime


class BrandBase(BaseModel):
    name: str
    last_update: datetime
    products: List["Product"] = []


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BrandBase):
    pass


class Brand(BrandBase):
    name: int
    last_update: datetime
    products: List["Product"] = []

    class Config:
        from_attributes = True
