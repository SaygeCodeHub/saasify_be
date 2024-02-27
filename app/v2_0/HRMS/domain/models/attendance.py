"""Model - Attendance"""
from sqlalchemy import Column, Integer, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class Attendance(Base):
    __tablename__ = 'attendance'

    attendance_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    date = Column(Date, nullable=False)
    check_in = Column(DateTime(timezone=True), nullable=True)
    check_out = Column(DateTime(timezone=True), nullable=True)

    user_auth = relationship('UsersAuth', back_populates='attendance')
