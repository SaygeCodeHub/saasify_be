from sqlalchemy import Column, String, BIGINT, Date, ForeignKey
from sqlalchemy.orm import validates
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


class Companies(Base):
    __tablename__ = "companies"

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

    user_id = Column(String, primary_key=True, nullable=False, unique=True)
    user_name = Column(String, nullable=False)
    user_contact = Column(BIGINT, nullable=False, unique=True)
    user_birthdate = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user_image = Column(String, nullable=True)

    @validates('user_contact', 'user_id', 'user_name')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class UserCompany(Base):
    __tablename__ = 'user_company'

    id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
