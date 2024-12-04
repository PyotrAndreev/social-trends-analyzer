from pydantic import BaseModel


class AdvertisementBase(BaseModel):
    video_id: int
    product_id: int


class AdvertisementCreate(AdvertisementBase):
    pass


class Advertisement(AdvertisementBase):
    id: int

    class Config:
        orm_mode = True
