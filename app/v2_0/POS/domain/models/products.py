"""Model - Products"""
from app.infrastructure.database import Base

from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey


class Products(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    product_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
