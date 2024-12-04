from sqlalchemy import Column, ForeignKey, String, BigInteger, DateTime
from sqlalchemy.orm import relationship
from database.database import Base


class Channel(Base):
    __tablename__ = "channels"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    videos = relationship("Video", back_populates="channel")


class Brand(Base):
    __tablename__ = "brands"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    products = relationship("Product", back_populates="brand")


class Product(Base):
    __tablename__ = "products"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    brand_id = Column(BigInteger, ForeignKey("brands.id"), nullable=False)
    brand = relationship("Brand", back_populates="products")
    advertisements = relationship("Advertisement", back_populates="product")


class Video(Base):
    __tablename__ = "videos"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    channel_id = Column(BigInteger, ForeignKey("channels.id"), nullable=False)
    channel = relationship("Channel", back_populates="videos")
    advertisements = relationship("Advertisement", back_populates="video")


class Advertisement(Base):
    __tablename__ = "advertisements"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    video_id = Column(BigInteger, ForeignKey("videos.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    video = relationship("Video", back_populates="advertisements")
    product = relationship("Product", back_populates="advertisements")
