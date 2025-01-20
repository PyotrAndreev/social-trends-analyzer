from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdvertisementBase(BaseModel):
    video_id: str
    product_name: str
    link: str
    utm_tags: Optional[dict]
    last_update: datetime


class AdvertisementCreate(AdvertisementBase):
    pass


class AdvertisementUpdate(AdvertisementBase):
    pass


class Advertisement(AdvertisementBase):
    video_id: str
    product_name: str
    link: str
    utm_tags: Optional[dict]
    last_update: datetime

    class Config:
        from_attributes = True
