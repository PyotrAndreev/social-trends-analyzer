from sqlalchemy import Column, ForeignKey, String, BigInteger, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base
import uuid


class Channel(Base):
    __tablename__ = "channels"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    videos = relationship("Video", back_populates="channel", lazy="joined")


class Brand(Base):
    __tablename__ = "brands"
    name = Column(String, primary_key=True, nullable=False, unique=True)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    products = relationship("Product", back_populates="brand", lazy="joined")


class Product(Base):
    __tablename__ = "products"
    name = Column(String, primary_key=True, nullable=False)
    brand_name = Column(String, ForeignKey("brands.name"), nullable=False)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    brand = relationship("Brand", back_populates="products", lazy="joined")
    advertisements = relationship("Advertisement", back_populates="product", lazy="joined")


class Video(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    channel_id = Column(String, ForeignKey("channels.id"), nullable=False)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    channel = relationship("Channel", back_populates="videos", lazy="joined")
    advertisements = relationship("Advertisement", back_populates="video", lazy="joined")


class Advertisement(Base):
    __tablename__ = "advertisements"
    video_id = Column(String, ForeignKey('videos.id'), nullable=False)
    product_name = Column(String, ForeignKey('products.name'), nullable=False)
    link = Column(String, primary_key=True, nullable=False)
    utm_tags = Column(JSON, nullable=True)
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    video = relationship('Video', back_populates='advertisements', lazy="joined")
    product = relationship('Product', back_populates='advertisements', lazy="joined")
