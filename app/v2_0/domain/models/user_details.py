"""Model - UsersDetails"""
from sqlalchemy import Column, Integer, ForeignKey, String, BIGINT, Date, Enum, TIMESTAMP
from sqlalchemy.sql.expression import text

from app.v2_0.domain.models.enums import ActivityStatus
from app.v2_0.infrastructure.database import Base


class UserDetails(Base):
    __tablename__ = 'user_details'

    details_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    first_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    user_contact = Column(BIGINT, nullable=True, unique=True)
    alternate_contact = Column(BIGINT, nullable=True, unique=True)
    user_birthdate = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    marital_status = Column(String, nullable=True)
    current_address = Column(String, nullable=True)
    permanent_address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(BIGINT, nullable=True)
    medical_leaves = Column(Integer, nullable=True)
    casual_leaves = Column(Integer, nullable=True)
    user_image = Column(String, nullable=True)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
