"""Model - Shifts"""
from sqlalchemy import Column, String, Integer, TIMESTAMP, Time, ForeignKey
from sqlalchemy.sql.expression import text

from app.infrastructure.database import Base


class Shifts(Base):
    """Contains all the fields required in the 'shifts' table"""
    __tablename__ = "shifts"

    shift_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=True)
    shift_name = Column(String, nullable=True)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
