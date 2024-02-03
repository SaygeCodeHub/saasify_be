"""Model - UsersAuth"""
from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.sql.expression import text

from app.v2_0.infrastructure.database import Base


class UsersAuth(Base):
    """Contains all the fields required in the 'users' table"""
    __tablename__ = "users_auth"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    password = Column(String, nullable=True)
    user_email = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    invited_by = Column(String, nullable=True)
    modified_by = Column(Integer, nullable=True)
    change_password_token = Column(String, nullable=True)
