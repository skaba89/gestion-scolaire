"""
Support Ticket Model for GROUP_AGENT (Support & Maintenance)
"""
from sqlalchemy import Column, String, Text, ForeignKey, Enum, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.models.base import Base, UUIDMixin, TimestampMixin, TenantMixin


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(str, enum.Enum):
    TECHNICAL = "technical"
    ACCOUNT = "account"
    BILLING = "billing"
    ACADEMIC = "academic"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    OTHER = "other"


class SupportTicket(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "support_tickets"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    category = Column(Enum(TicketCategory), default=TicketCategory.OTHER)

    # Relations
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Tracking
    first_response_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # SLA
    sla_due_at = Column(DateTime, nullable=True)
    sla_breached = Column(Integer, default=0)  # 0 = no, 1 = yes

    # Metrics
    response_time_minutes = Column(Integer, nullable=True)
    resolution_time_minutes = Column(Integer, nullable=True)

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], backref="reported_tickets")
    assigned_agent = relationship("User", foreign_keys=[assigned_to_id], backref="assigned_tickets")
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")


class TicketComment(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "ticket_comments"

    ticket_id = Column(UUID(as_uuid=True), ForeignKey("support_tickets.id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_internal = Column(Integer, default=0)  # 0 = public, 1 = internal (agent only)

    # Relationships
    ticket = relationship("SupportTicket", back_populates="comments")
    author = relationship("User", backref="ticket_comments")


class MaintenanceLog(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "maintenance_logs"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    maintenance_type = Column(String(50))  # scheduled, emergency, update
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed, cancelled
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    affected_services = Column(Text, nullable=True)  # JSON list of affected services
    performed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    performed_by = relationship("User", backref="maintenance_logs")
