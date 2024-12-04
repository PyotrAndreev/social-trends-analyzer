from pydantic import BaseModel
from datetime import datetime


class VideoBase(BaseModel):
    title: str
    published_at: datetime
    channel_id: int


class VideoCreate(VideoBase):
    pass


class Video(VideoBase):
    id: int

    class Config:
        orm_mode = True
