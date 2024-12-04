from pydantic import BaseModel
from typing import List
from schemas.video import Video


class ChannelBase(BaseModel):
    name: str


class ChannelCreate(ChannelBase):
    pass


class Channel(ChannelBase):
    id: int
    videos: List[Video] = []

    class Config:
        orm_mode = True
