from sqlalchemy import Column, String, BIGINT, ForeignKey, Date
from sqlalchemy.orm import validates, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP, Boolean, Float, JSON, Double

from app.database import Base


class CompaniesV(Base):
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


class UsersV(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

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


class UserCompanyV(Base):
    __tablename__ = 'user_company'
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)


class Branches(Base):
    __tablename__ = 'branches'

    branch_id = Column(BIGINT, primary_key=True, autoincrement=True)
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
    branch_name = Column(String, nullable=False)
    branch_address = Column(String, nullable=False)
    branch_currency = Column(String, nullable=False)
    branch_active = Column(Boolean, nullable=False, server_default='TRUE')
    branch_contact = Column(BIGINT, nullable=True)

    company = relationship("Companies")

    @validates('company_id', 'branch_name', 'branch_currency', 'branch_contact')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Brand(Base):
    __tablename__ = 'brand'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'))
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
    brand_id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    brand_name = Column(String, nullable=False)

    company = relationship("Companies")
    branch = relationship("Branches")

    @validates('company_id', 'branch_id', 'brand_name')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Category(Base):
    __tablename__ = 'category'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'))
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
    category_id = Column(BIGINT, primary_key=True, autoincrement=True)
    category_name = Column(String, nullable=False)
    is_active = Column(Boolean, server_default='TRUE', nullable=False)

    company = relationship("Companies")
    branch = relationship("Branches")

    @validates('company_id', 'branch_id', 'category_name', 'is_active')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class PaymentMethod(Base):
    __tablename__ = 'payment_method'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
    payment_id = Column(BIGINT, primary_key=True, autoincrement=True)
    payment_name = Column(String, nullable=False)
    is_active = Column(Boolean, server_default='TRUE', nullable=False)

    company = relationship("Companies")
    branch = relationship("Branches")

    @validates('company_id', 'branch_id', 'payment_name', 'is_active')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Products(Base):
    __tablename__ = 'products'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
    brand_id = Column(BIGINT, ForeignKey('brand.brand_id'), nullable=True)
    category_id = Column(BIGINT, ForeignKey('category.category_id'), nullable=False)
    product_id = Column(BIGINT, primary_key=True, nullable=False, autoincrement=True)
    product_name = Column(String, nullable=False)
    product_description = Column(String, nullable=True)

    company = relationship("Companies")
    branch = relationship("Branches")
    brand = relationship("Brand")
    category = relationship("Category")
    variants = relationship('Variants', back_populates='product')

    @validates('company_id', 'branch_id', 'product_name', )
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Variants(Base):
    __tablename__ = 'variants'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
    product_id = Column(BIGINT, ForeignKey('products.product_id', ondelete="CASCADE"), nullable=False)
    variant_id = Column(BIGINT, primary_key=True, autoincrement=True)
    cost = Column(Double, nullable=True)
    stock_id = Column(BIGINT, ForeignKey("inventory.stock_id", ondelete="CASCADE"), nullable=True)
    quantity = Column(BIGINT, nullable=True)
    unit = Column(String, nullable=True)
    discount_cost = Column(Double, nullable=True)
    discount_percent = Column(Double, nullable=True)
    images = Column(JSON, nullable=True)
    draft = Column(Boolean, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default='TRUE')
    barcode = Column(BIGINT, nullable=True)
    restock_reminder = Column(BIGINT, nullable=True)
    SGST = Column(Float, nullable=True)
    CGST = Column(Float, nullable=True)

    company = relationship("Companies", foreign_keys=[company_id])
    branch = relationship("Branches", foreign_keys=[branch_id])
    product = relationship("Products", foreign_keys=[product_id])
    stock = relationship("Inventory", foreign_keys=[stock_id])

    @validates('company_id', 'branch_id', 'product_name', 'barcode')
    def empty_string_to_null(self, key, value):
        if isinstance(value, str) and value == '':
            return None
        else:
            return value


class Inventory(Base):
    __tablename__ = 'inventory'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
    variant_id = Column(BIGINT, ForeignKey("variants.variant_id", ondelete="CASCADE"), nullable=True)
    stock_id = Column(BIGINT, primary_key=True, autoincrement=True)
    stock = Column(BIGINT, nullable=True)

    company = relationship("Companies", foreign_keys=[company_id])
    branch = relationship("Branches", foreign_keys=[branch_id])
    variants = relationship("Variants", foreign_keys=[variant_id])


class Orders(Base):
    __tablename__ = 'orders'

    branch_id = Column(BIGINT, ForeignKey('branches.branch_id'), nullable=False)
    company_id = Column(String, ForeignKey('companies.company_id'), nullable=False)
    order_id = Column(BIGINT, primary_key=True, autoincrement=True)
    order_no = Column(String, nullable=False, primary_key=True, unique=True,
                      server_default=text("EXTRACT(EPOCH FROM NOW())::BIGINT"))
    order_date = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    items_ordered = Column(JSON, nullable=False)
    discount_total = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    payment_status = Column(String, nullable=False)
    payment_type = Column(String, nullable=False)
    customer_contact = Column(BIGINT, nullable=False)
    customer_name = Column(String, nullable=True)
    gst = Column(String, nullable=True)

    company = relationship("Companies")
    branch = relationship("Branches")
