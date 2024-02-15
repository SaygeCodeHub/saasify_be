"""Model - UserCompanyBranch"""

from sqlalchemy import Column, Integer, ForeignKey, Enum, ARRAY, String, TIMESTAMP, text

from app.v2_0.enums import DesignationEnum, Modules, Features
from app.v2_0.infrastructure.database import Base


class UserCompanyBranch(Base):
    """Contains all the fields required in the table"""
    __tablename__ = 'user_company_branch'

    ucb_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=True)
    designations = Column(ARRAY(Enum(DesignationEnum)), nullable=True)
    approvers = Column(ARRAY(Integer), nullable=False)
    accessible_modules = Column(ARRAY(Enum(Modules)), nullable=True)
    accessible_features = Column(ARRAY(Enum(Features)), nullable=True)
    device_token = Column(String, nullable=True)
    shift_id = Column(Integer, ForeignKey("shifts.shift_id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
