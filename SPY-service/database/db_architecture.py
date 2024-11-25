import os
from dotenv import load_dotenv
from sqlalchemy import (
    BigInteger, Column, ForeignKey, String, DateTime, create_engine, text
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("DB_NAME")


class Channel(Base):
    __tablename__ = 'channels'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    videos = relationship('Video', back_populates='channel')

    def __repr__(self):
        return f"<Channel(id={self.id}, name='{self.name}')>"


class Brand(Base):
    __tablename__ = 'brands'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    products = relationship('Product', back_populates='brand')

    def __repr__(self):
        return f"<Brand(id={self.id}, name='{self.name}')>"


class Product(Base):
    __tablename__ = 'products'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    brand_id = Column(BigInteger, ForeignKey('brands.id'), nullable=False)

    brand = relationship('Brand', back_populates='products')
    advertisements = relationship('Advertisement', back_populates='product')

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', brand_id={self.brand_id})>"


class Video(Base):
    __tablename__ = 'videos'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    channel_id = Column(BigInteger, ForeignKey('channels.id'), nullable=False)

    channel = relationship('Channel', back_populates='videos')
    advertisements = relationship('Advertisement', back_populates='video')

    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}', published_at='{self.published_at}')>"


class Advertisement(Base):
    __tablename__ = 'advertisements'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    video_id = Column(BigInteger, ForeignKey('videos.id'), nullable=False)
    product_id = Column(BigInteger, ForeignKey('products.id'), nullable=False)

    video = relationship('Video', back_populates='advertisements')
    product = relationship('Product', back_populates='advertisements')

    def __repr__(self):
        return f"<Advertisement(id={self.id}, video_id={self.video_id}, product_id={self.product_id})>"


engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{DB_NAME}')
Base.metadata.create_all(engine)

with engine.connect() as connection:
    trigger_ads_to_log = text("""
        CREATE OR REPLACE FUNCTION log_ad_changes()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE NOTICE 'Advertisement updated: %', OLD.id;
            RETURN NEW;
        END;
        $$ LANGUAGE 'plpgsql';

        CREATE TRIGGER log_ads_trigger
        BEFORE UPDATE ON advertisements
        FOR EACH ROW
        EXECUTE FUNCTION log_ad_changes();
    """)
    connection.execute(trigger_ads_to_log)
