"""Model - Tasks"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date, TIMESTAMP, text, Enum, DateTime
from sqlalchemy.orm import relationship

from app.v2_0.enums import TaskPriority, TaskStatus
from app.v2_0.infrastructure.database import Base


class Tasks(Base):
    """Contains all the fields required in the 'tasks' table"""
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("branches.branch_id"), nullable=False)
    title = Column(String, nullable=True)
    task_description = Column(String, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users_auth.user_id"), nullable=True)
    monitored_by = Column(Integer, ForeignKey("users_auth.user_id"), nullable=True)
    due_date = Column(Date, nullable=True)
    completion_date = Column(DateTime, nullable=True)
    priority = Column(Enum(TaskPriority), nullable=False)
    task_status = Column(Enum(TaskStatus), nullable=True, server_default=TaskStatus.PENDING.name)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    modified_on = Column(TIMESTAMP(timezone=True), nullable=True)
    modified_by = Column(Integer, nullable=True)

    # assigned_user = relationship('UsersAuth',back_populates='task_1', foreign_keys=[assigned_to])
    # monitored_user = relationship('UsersAuth',back_populates='task_2', foreign_keys=[monitored_by])
