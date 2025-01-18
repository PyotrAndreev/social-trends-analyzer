from database.database import SessionLocal
from crud import (
    advertisement as crud_advertisement,
    brand as crud_brand,
    channel as crud_channel,
    product as crud_product,
    video as crud_video,
)
from schemas.advertisement import AdvertisementCreate
from schemas.brand import BrandCreate
from schemas.channel import ChannelCreate
from schemas.product import ProductCreate
from schemas.video import VideoCreate



class DBAPI:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def create_advertisement(self, advertisement: AdvertisementCreate):
        return crud_advertisement.create_advertisement(self.db, advertisement)

    def get_advertisement(self, link: str):
        return crud_advertisement.get_advertisement(self.db, link)

    def get_advertisements(self, skip: int = 0, limit: int = 100):
        return crud_advertisement.get_advertisements(self.db, skip, limit)

    def create_brand(self, brand: BrandCreate):
        return crud_brand.create_brand(self.db, brand)

    def get_brand(self, brand_name: str):
        return crud_brand.get_brand(self.db, brand_name)

    def get_brands(self, skip: int = 0, limit: int = 100):
        return crud_brand.get_brands(self.db, skip, limit)

    def create_channel(self, channel: ChannelCreate):
        return crud_channel.create_channel(self.db, channel)

    def get_channel(self, channel_id: str):
        return crud_channel.get_channel(self.db, channel_id)

    def get_channels(self, skip: int = 0, limit: int = 100):
        return crud_channel.get_channels(self.db, skip, limit)

    def create_product(self, product: ProductCreate):
        return crud_product.create_product(self.db, product)

    def get_product(self, product_name: str):
        return crud_product.get_product(self.db, product_name)

    def get_products(self, skip: int = 0, limit: int = 100):
        return crud_product.get_products(self.db, skip, limit)

    def create_video(self, video: VideoCreate):
        return crud_video.create_video(self.db, video)

    def get_video(self, video_id: str):
        return crud_video.get_video(self.db, video_id)

    def get_videos(self, skip: int = 0, limit: int = 100):
        return crud_video.get_videos(self.db, skip, limit)