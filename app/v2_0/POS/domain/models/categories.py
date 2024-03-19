"""Model - Categories"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey

from app.infrastructure.database import Base


class Categories(Base):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)

