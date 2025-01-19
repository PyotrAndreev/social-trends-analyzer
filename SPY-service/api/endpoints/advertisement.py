from fastapi import APIRouter, HTTPException
from database.db_API import DBAPI
from schemas.advertisement import Advertisement, AdvertisementCreate

router = APIRouter()

@router.post("/", response_model=Advertisement)
def create_advertisement_endpoint(advertisement: AdvertisementCreate):
    with DBAPI() as db_api:
        return db_api.create_advertisement(advertisement)

@router.get("/{advertisement_id}", response_model=Advertisement)
def get_advertisement_endpoint(expanded_link: str):
    with DBAPI() as db_api:
        db_advertisement = db_api.get_advertisement(expanded_link)
        if not db_advertisement:
            raise HTTPException(status_code=404, detail="Advertisement not found")
        return db_advertisement

@router.get("/", response_model=list[Advertisement])
def get_advertisements_endpoint(skip: int = 0, limit: int = 100):
    with DBAPI() as db_api:
        return db_api.get_advertisements(skip=skip, limit=limit)