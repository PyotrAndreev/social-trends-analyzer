from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from SPY_service.core.config import settings

Base = declarative_base()
engine = create_engine(settings.DATABASE_URL, connect_args={"options": "-c timezone=utc"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_ads_db():
    Base.metadata.create_all(bind=engine)
