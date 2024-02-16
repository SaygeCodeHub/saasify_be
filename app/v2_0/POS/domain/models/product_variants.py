"""Model - ProductVariants"""
from app.v2_0.enums import Unit
from app.v2_0.infrastructure.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, Double, Enum


class ProductVariants(Base):
    __tablename__ = 'product_variants'

    variant_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    variant_name = Column(String, nullable=True)
    measuring_qty = Column(String, nullable=True)
    stock_qty = Column(Integer, nullable=True)
    unit = Column(Enum(Unit), nullable=True)
    price = Column(Double, nullable=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
