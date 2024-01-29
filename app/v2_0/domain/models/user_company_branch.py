"""Model - UserCompanyBranch"""

from sqlalchemy import Column, Integer, ForeignKey, BIGINT, String, TIMESTAMP, Double, Boolean, Enum, ARRAY


from app.v2_0.domain.models.enums import RolesEnum
from app.v2_0.infrastructure.database import Base


class UserCompanyBranch(Base):
    """Contains all the fields required for creating the table"""
    __tablename__ = 'user_company_branch'

    ucb_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=True)
    roles = Column(ARRAY(Enum(RolesEnum)), nullable=True)
    approvers = Column(ARRAY(Integer), nullable=False)