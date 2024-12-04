from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud.channel import create_channel, get_channel, get_channels
from schemas.channel import Channel, ChannelCreate
from ..dependencies import get_db

router = APIRouter()


@router.post("/", response_model=Channel)
def create_channel_endpoint(channel: ChannelCreate, db: Session = Depends(get_db)):
    return create_channel(db=db, channel=channel)


@router.get("/{channel_id}", response_model=Channel)
def get_channel_endpoint(channel_id: int, db: Session = Depends(get_db)):
    db_channel = get_channel(db=db, channel_id=channel_id)
    if not db_channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return db_channel


@router.get("/", response_model=list[Channel])
def get_channels_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_channels(db=db, skip=skip, limit=limit)
