from pydantic import BaseModel
from typing import List
from schemas.video import Video
from datetime import datetime


class ChannelBase(BaseModel):
    id: str
    name: str
    last_update: datetime
    videos: List["Video"] = []


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(ChannelBase):
    pass


class Channel(ChannelBase):
    id: str
    name: str
    last_update: datetime
    videos: List["Video"] = []

    class Config:
        from_attributes = True
