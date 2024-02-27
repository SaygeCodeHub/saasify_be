"""Model - Announcements"""
from sqlalchemy import Column, Integer, Date, String, Boolean, text, ForeignKey, TIMESTAMP

from app.infrastructure.database import Base


class Announcements(Base):
    """Contains all the fields required in the 'announcements' table"""
    __tablename__ = "announcements"

    announcement_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    due_date = Column(Date, nullable=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=True, server_default=text('true'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
