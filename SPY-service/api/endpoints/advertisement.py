from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from crud.advertisement import create_advertisement, get_advertisement, get_advertisements
from schemas.advertisement import Advertisement, AdvertisementCreate
from ..dependencies import get_db

router = APIRouter()


@router.post("/", response_model=Advertisement)
def create_advertisement_endpoint(advertisement: AdvertisementCreate, db: Session = Depends(get_db)):
    return create_advertisement(db=db, advertisement=advertisement)


@router.get("/{advertisement_id}", response_model=Advertisement)
def get_advertisement_endpoint(advertisement_id: int, db: Session = Depends(get_db)):
    db_advertisement = get_advertisement(db=db, advertisement_id=advertisement_id)
    if not db_advertisement:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_advertisement


@router.get("/", response_model=list[Advertisement])
def get_advertisements_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_advertisements(db=db, skip=skip, limit=limit)
