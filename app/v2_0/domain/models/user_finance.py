"""Model - UserFinance"""

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Double
from sqlalchemy.sql.expression import text

from app.v2_0.infrastructure.database import Base


class UserFinance(Base):
    """Contains all the fields required in the 'user_finance' table"""
    __tablename__ = 'user_finance'

    fin_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    basic_salary = Column(Double, nullable=True)
    BOA = Column(Double, nullable=True)
    bonus = Column(Double, nullable=True)
    PF = Column(Double, nullable=True)
    performance_bonus = Column(Double, nullable=True)
    gratuity = Column(Double, nullable=True)
    deduction = Column(Double, nullable=True, server_default='0.0')
    fixed_monthly_gross = Column(Double, nullable=True)
    total_annual_gross = Column(Double, nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
