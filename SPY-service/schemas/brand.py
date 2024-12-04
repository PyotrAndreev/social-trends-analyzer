from pydantic import BaseModel
from typing import List
from schemas.product import Product


class BrandBase(BaseModel):
    name: str


class BrandCreate(BrandBase):
    pass


class Brand(BrandBase):
    id: int
    products: List[Product] = []

    class Config:
        orm_mode = True
