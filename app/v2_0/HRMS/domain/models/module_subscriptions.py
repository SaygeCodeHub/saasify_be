"""Model - ModuleSubscription"""
from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, Boolean, Enum, Date, ARRAY
from sqlalchemy.sql.expression import text

from app.v2_0.enums import Modules
from app.v2_0.infrastructure.database import Base


class ModuleSubscriptions(Base):
    __tablename__ = 'module_subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    module_name = Column(ARRAY(Enum(Modules)), nullable=True)
    is_subscribed = Column(Boolean, nullable=True, server_default=text('true'))
    start_date = Column(Date, nullable=False, server_default=text('CURRENT_DATE'))
    end_date = Column(Date, nullable=False, server_default=text("(current_date + interval '1 months')"))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)
