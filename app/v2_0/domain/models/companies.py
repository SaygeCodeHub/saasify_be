"""Model - Companies"""
from app.v2_0.domain.models.enums import ActivityStatus
from app.v2_0.infrastructure.database import Base

from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP, Enum
from sqlalchemy.sql.expression import text


class Companies(Base):
    """Contains all the fields required in the 'companies' table"""
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True}

    company_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_name = Column(String, nullable=False)
    company_domain = Column(String, nullable=True)
    company_logo = Column(String, nullable=True)
    company_email = Column(String, nullable=True)
    services = Column(String, nullable=True)
    owner = Column(Integer, ForeignKey('users_auth.user_id'), nullable=False)
    activity_status = Column(Enum(ActivityStatus), nullable=False)
    onboarding_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
