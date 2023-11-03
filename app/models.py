from sqlalchemy import Column, String, BIGINT, Date, JSON, ForeignKey, Boolean, Float, Integer
from sqlalchemy.orm import validates, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


class Companies(Base):
    __tablename__ = "companies"

    company_id = Column(String, nullable=True, primary_key=True, unique=True)
    company_name = Column(String, nullable=True, unique=True)
    company_password = Column(String, nullable=False)
    company_domain = Column(String, nullable=True)
    company_logo = Column(JSON, nullable=True)
    company_email = Column(String, nullable=True)
    services = Column(String, nullable=True)
    company_contact = Column(BIGINT, nullable=True)
    company_address = Column(String, nullable=True)
    white_labelled = Column(Boolean, nullable=True)
    onboarding_date = Column(TIMESTAMP(timezone=True), nullable=True, server_default=text('now()'))

    @validates('company_name', 'company_password', 'company_email', 'company_contact', 'company_address')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Users(Base):
    __tablename__ = "users"

    user_uniqueid = Column(BIGINT, primary_key=True, nullable=False,
                           server_default=text("EXTRACT(EPOCH FROM NOW())::BIGINT"))
    user_name = Column(String, nullable=True)
    user_contact = Column(BIGINT, nullable=True)
    user_birthdate = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    user_image = Column(String, nullable=True)
    user_emailId = Column(String, nullable=True)
    user_password = Column(String, nullable=True)

    @validates('user_contact', 'user_uniqueid')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(BIGINT, nullable=False, primary_key=True, autoincrement=True, unique=True)
    category_name = Column(String, nullable=False)

    @validates('category_name')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        return value


class Brand(Base):
    __tablename__ = "brands"

    brand_id = Column(BIGINT, autoincrement=True, primary_key=True)
    brand_name = Column(String, nullable=False)
    brand_image = Column(String, nullable=False)


class Products(Base):
    __tablename__ = "products"

    product_id = Column(BIGINT, nullable=False, primary_key=True, autoincrement=True, unique=True, index=True)
    brand_id = Column(BIGINT, ForeignKey("brands.brand_id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String, nullable=False)
    category_id = Column(BIGINT, ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)

    category = relationship("Category")
    brand = relationship("Brand")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    variant_id = Column(BIGINT, primary_key=True, index=True, autoincrement=True)
    variant_cost = Column(Float, nullable=False)
    brand_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    discounted_cost = Column(Float, nullable=True)
    discount = Column(BIGINT, nullable=True)
    stock = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    image = Column(JSON, nullable=True)
    ratings = Column(Integer, nullable=True)
    measuring_unit = Column(String, nullable=False)
    is_published = Column(Boolean, nullable=False)
    barcode_no = Column(BIGINT, nullable=False, unique=True)
    product_id = Column(BIGINT, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    branch_id = Column(BIGINT, ForeignKey("branch.branch_id", ondelete="CASCADE"), nullable=False)

    product = relationship("Products")
    branch = relationship("Branch")


class Branch(Base):
    __tablename__ = "branch"

    branch_id = Column(Integer, primary_key=True, autoincrement=True)
    branch_name = Column(String, nullable=False)
    branch_address = Column(String, nullable=False)
    branch_email = Column(String, nullable=False)
    branch_number = Column(BIGINT, nullable=False, unique=True)
    company_id = Column(String, ForeignKey("companies.company_id", ondelete="CASCADE"))

    company = relationship("Companies")
