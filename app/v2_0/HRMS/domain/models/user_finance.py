"""Model - UserFinance"""

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Double
from sqlalchemy.sql.expression import text

from app.v2_0.infrastructure.database import Base


class UserFinance(Base):
    """Contains all the fields required in the 'user_finance' table"""
    __tablename__ = 'user_finance'

    fin_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    basic_salary = Column(Double, nullable=True, server_default=text('0.0'))
    BOA = Column(Double, nullable=True, server_default=text('0.0'))
    bonus = Column(Double, nullable=True, server_default=text('0.0'))
    PF = Column(Double, nullable=True, server_default=text('0.0'))
    performance_bonus = Column(Double, nullable=True, server_default=text('0.0'))
    gratuity = Column(Double, nullable=True, server_default=text('0.0'))
    deduction = Column(Double, nullable=True, server_default=text('0.0'))
    fixed_monthly_gross = Column(Double, nullable=True, server_default=text('0.0'))
    total_annual_gross = Column(Double, nullable=True, server_default=text('0.0'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
