from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.v2_0.infrastructure.db_config import DATABASE_URL_LOCAL_JAYRAJ, DATABASE_URL_PROD, DATABASE_URL_LOCAL_ADITI, \
    DATABASE_URL_SAYGE_ADITI

SQLALCHEMY_DATABASE_URL = DATABASE_URL_PROD

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=300)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
