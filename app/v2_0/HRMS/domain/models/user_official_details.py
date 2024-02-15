"""Model - UserOfficial"""

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, String, Boolean
from sqlalchemy.sql.expression import text

from app.v2_0.infrastructure.database import Base


class UserOfficialDetails(Base):
    """Contains all the fields required in the 'user_finance' table"""
    __tablename__ = 'user_official'

    official_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    doj = Column(TIMESTAMP(timezone=True), nullable=True)
    job_confirmation = Column(Boolean, nullable=True)
    current_location = Column(String, nullable=True)
    department_head = Column(Integer, nullable=True)
    reporting_manager = Column(Integer, nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
