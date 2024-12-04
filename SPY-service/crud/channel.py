from sqlalchemy.orm import Session
from database.models import Channel
from schemas.channel import ChannelCreate


def create_channel(db: Session, channel: ChannelCreate):
    db_channel = Channel(name=channel.name)
    db.add(db_channel)
    db.commit()
    db.refresh(db_channel)
    return db_channel


def get_channel(db: Session, channel_id: int):
    return db.query(Channel).filter(Channel.id == channel_id).first()


def get_channels(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Channel).offset(skip).limit(limit).all()
