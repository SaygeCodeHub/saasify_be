"""Model - UserDocuments"""
from sqlalchemy import Column, Integer, ForeignKey, BIGINT, String, Date, TIMESTAMP
from sqlalchemy.sql.expression import text

from app.v2_0.infrastructure.database import Base


class UserDocuments(Base):
    """Contains all the fields required in the 'user_documents' table"""
    __tablename__ = 'user_documents'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users_auth.user_id"), nullable=False)
    aadhar_number = Column(BIGINT, nullable=True, unique=True)
    name_as_per_aadhar = Column(String, nullable=True)
    pan_number = Column(String, nullable=True, unique=True)
    passport_num = Column(String, nullable=True, unique=True)
    passport_fname = Column(String, nullable=True)
    passport_lname = Column(String, nullable=True)
    expiry_date = Column(Date, nullable=True)
    issue_date = Column(Date, nullable=True)
    mobile_number = Column(BIGINT, nullable=True)
    current_address = Column(String, nullable=True)
    permanent_address = Column(String, nullable=True)
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
