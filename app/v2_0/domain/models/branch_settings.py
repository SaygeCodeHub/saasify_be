"""Model - BranchSettings"""

from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP, Double, Boolean, DateTime
from sqlalchemy.sql.expression import text

from app.v2_0.infrastructure.database import Base


class BranchSettings(Base):
    """Contains all the fields required in the 'branch_settings' table"""
    __tablename__ = 'branch_settings'

    setting_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    working_days = Column(Integer, nullable=True)
    time_in = Column(DateTime(timezone=True), nullable=True)
    time_out = Column(DateTime(timezone=True), nullable=True)
    timezone = Column(DateTime(timezone=True), nullable=True,server_default=text("(now() at time zone 'IST')"))
    currency = Column(String, nullable=True)
    default_approver = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    total_medical_leaves = Column(Integer, nullable=True)
    total_casual_leaves = Column(Integer, nullable=True)
    overtime_rate = Column(Double, nullable=True)
    overtime_rate_per = Column(String, nullable=True)
    is_hq_settings = Column(Boolean, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
    geo_fencing = Column(Boolean,nullable=True,server_default=text('true'))
