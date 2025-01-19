from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    try:
        with engine.connect() as connection:
            print("Подключение к базе данных прошло успешно!")
        Base.metadata.create_all(engine)
    except Exception as e:
        print(f"Ошибка подключения или создания таблиц: {e}")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
