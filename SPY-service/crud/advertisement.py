from sqlalchemy.orm import Session
from database.models import Advertisement
from schemas.advertisement import AdvertisementCreate


def create_advertisement(db: Session, advertisement: AdvertisementCreate):
    db_advertisement = Advertisement(**advertisement.model_dump())
    db.add(db_advertisement)
    db.commit()
    db.refresh(db_advertisement)
    return db_advertisement


def get_advertisement(db: Session, link: str):
    return db.query(Advertisement).filter(Advertisement.link == link).first()


def get_advertisements(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Advertisement).offset(skip).limit(limit).all()
