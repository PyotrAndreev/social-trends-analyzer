from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud.video import create_video, get_video, get_videos
from schemas.video import Video, VideoCreate
from ..dependencies import get_db

router = APIRouter()


@router.post("/", response_model=Video)
def create_video_endpoint(video: VideoCreate, db: Session = Depends(get_db)):
    return create_video(db=db, video=video)


@router.get("/{video_id}", response_model=Video)
def get_video_endpoint(video_id: int, db: Session = Depends(get_db)):
    db_video = get_video(db=db, video_id=video_id)
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video


@router.get("/", response_model=list[Video])
def get_videos_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_videos(db=db, skip=skip, limit=limit)
