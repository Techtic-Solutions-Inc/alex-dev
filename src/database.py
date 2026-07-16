from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import DATABASE_URL
from src.models.base import Base
from src.models.admin import Admin  # noqa: F401
from src.models.user import User  # noqa: F401

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
