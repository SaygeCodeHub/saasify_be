"""Model - Branches"""

from sqlalchemy import Column, Integer, ForeignKey, BIGINT, String, TIMESTAMP, Double, Boolean, Enum
from sqlalchemy.sql.expression import text

from app.enums.activity_status_enum import ActivityStatus
from app.infrastructure.database import Base


class Branches(Base):
    """Contains all the fields required in the 'branches' table"""
    __tablename__ = 'branches'

    branch_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.company_id'), nullable=False)
    branch_name = Column(String, nullable=False)
    branch_contact = Column(BIGINT, nullable=True)
    branch_currency = Column(String, nullable=True)
    branch_address = Column(String, nullable=True)
    location = Column(String, nullable=True)
    pincode = Column(Integer, nullable=True)
    longitude = Column(Double, nullable=True)
    latitude = Column(Double, nullable=True)
    is_head_quarter = Column(Boolean, nullable=True)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
