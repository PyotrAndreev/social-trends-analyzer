from pydantic import BaseModel
from datetime import datetime
from schemas.advertisement import Advertisement
from typing import List


class VideoBase(BaseModel):
    id: str
    title: str
    published_at: datetime
    channel_id: str
    last_update: datetime
    advertisements: List[Advertisement] = []


class VideoCreate(VideoBase):
    pass


class VideoUpdate(VideoBase):
    pass


class Video(VideoBase):
    id: str
    title: str
    published_at: datetime
    channel_id: str
    last_update: datetime
    advertisements: List[Advertisement] = []

    class Config:
        from_attributes = True
