from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://db_saasify_user:V45gnfQG3nZzPXzTRId6iE0hP3wL3X23@dpg-cl3idg0t3kic73dclg0g-a.oregon-postgres.render.com/db_saasify"

# "postgresql://postgres:Mun1chad$@localhost/postgres"
#
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
