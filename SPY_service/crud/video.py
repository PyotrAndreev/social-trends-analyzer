from sqlalchemy.orm import Session
from SPY_service.database.models import Video
from SPY_service.schemas.video import VideoCreate


def create_video(db: Session, video: VideoCreate):
    db_video = Video(**video.model_dump())
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video


def get_video(db: Session, video_id: str):
    return db.query(Video).filter(Video.id == video_id).first()


def get_videos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Video).offset(skip).limit(limit).all()
