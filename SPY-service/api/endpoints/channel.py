from schemas.channel import Channel
from fastapi import APIRouter, HTTPException
from youtube_parser.parser import YouTubeParser

from database.db_API import DBAPI
from schemas.channel import ChannelCreate

router = APIRouter()


@router.post("/", response_model=Channel)
def create_channel_endpoint(channel: ChannelCreate):
    with DBAPI() as db_api:
        return db_api.create_channel(channel)


@router.get("/{channel_id}", response_model=Channel)
def get_channel_endpoint(channel_id: str):
    with DBAPI() as db_api:
        db_channel = db_api.get_channel(channel_id)
        if not db_channel:
            raise HTTPException(status_code=404, detail="Channel not found")
        return db_channel


@router.get("/", response_model=list[Channel])
def get_channels_endpoint(skip: int = 0, limit: int = 100):
    with DBAPI() as db_api:
        return db_api.get_channels(skip=skip, limit=limit)


@router.post("/parse-channel/")
def parse_channel_endpoint(channel_url: str):
    YouTubeParser().parse_channel(channel_url)
