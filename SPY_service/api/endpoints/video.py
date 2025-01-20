from fastapi import APIRouter, HTTPException
from SPY_service.database.db_API import DBAPI
from SPY_service.schemas.video import Video, VideoCreate

router = APIRouter()

@router.post("/", response_model=Video)
def create_video_endpoint(video: VideoCreate):
    with DBAPI() as db_api:
        return db_api.create_video(video)

@router.get("/{video_id}", response_model=Video)
def get_video_endpoint(video_id: str):
    with DBAPI() as db_api:
        db_video = db_api.get_video(video_id)
        if not db_video:
            raise HTTPException(status_code=404, detail="Video not found")
        return db_video

@router.get("/", response_model=list[Video])
def get_videos_endpoint(skip: int = 0, limit: int = 100):
    with DBAPI() as db_api:
        return db_api.get_videos(skip=skip, limit=limit)