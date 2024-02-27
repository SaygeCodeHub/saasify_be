"""Model - UserBank"""

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, String, BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text

from app.infrastructure.database import Base


class UserBankDetails(Base):
    """Contains all the fields required in the 'user_finance' table"""
    __tablename__ = 'user_bank_details'

    bank_detail_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    bank_name = Column(String, nullable=True)
    account_number = Column(BIGINT, nullable=True)
    ifsc_code = Column(String, nullable=True)
    branch_name = Column(String, nullable=True)
    account_type = Column(String, nullable=True)
    country = Column(String, nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    user_auth = relationship('UsersAuth', back_populates='bank_details')
