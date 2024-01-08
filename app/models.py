from sqlalchemy import Column, String, BIGINT, Date, ForeignKey
from sqlalchemy.orm import validates, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean
from .database import Base


class Companies(Base):
    __tablename__ = "companies"
    __table_args__ = {'extend_existing': True}

    company_id = Column(String, nullable=False, primary_key=True, unique=True,
                        server_default=text("EXTRACT(EPOCH FROM NOW())::BIGINT"))
    company_name = Column(String, nullable=False)
    company_domain = Column(String, nullable=True)
    company_logo = Column(String, nullable=True)
    company_email = Column(String, nullable=True)
    services = Column(String, nullable=True)
    owner = Column(String, ForeignKey('users.user_id'), nullable=False)
    onboarding_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    @validates('company_name', 'company_email', 'company_contact')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    user_id = Column(String, primary_key=True, nullable=False, unique=True)
    user_name = Column(String, nullable=False)
    user_contact = Column(BIGINT, nullable=False, unique=True)
    user_email = Column(String, nullable=True, unique=True)
    user_birthdate = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user_image = Column(String, nullable=True)

    @validates('user_contact', 'user_id', 'user_name','user_email')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class UserCompany(Base):
    __tablename__ = 'user_company'
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
