"""Model - Orders"""
from app.enums.task_status_enum import TaskStatus
from app.infrastructure.database import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP, text, ForeignKey, Double, ARRAY, JSON, BIGINT, Enum


class Orders(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_contact = Column(BIGINT, nullable=False, unique=True)
    placed_by = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    products_ordered = Column(ARRAY(JSON), nullable=False)
    grand_total = Column(Double, nullable=True)
    gst = Column(Double, nullable=True)
    discount_amount = Column(Double, nullable=True)
    payment_type = Column(String, nullable=True)
    payment_status = Column(Enum(TaskStatus), nullable=True)
    order_placed_timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
