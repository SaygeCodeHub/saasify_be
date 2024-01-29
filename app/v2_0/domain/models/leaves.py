"""Model - Leaves"""
from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP, Boolean, Enum, ARRAY, Date
from sqlalchemy.sql.expression import text

from app.v2_0.domain.models.enums import LeaveType, LeaveStatus
from app.v2_0.infrastructure.database import Base


class Leaves(Base):
    __tablename__ = 'leaves'

    leave_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    leave_type = Column(Enum(LeaveType), nullable=False)
    leave_reason = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    comment = Column(String, nullable=True)
    approvers = Column(ARRAY(Integer), nullable=False)
    leave_status = Column(Enum(LeaveStatus), nullable=True)
    is_leave_approved = Column(Boolean, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)