"""
Support Ticket Model for GropAgent - Support and Maintenance Management
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, JSON, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.models.base import Base


class TicketStatus(str, enum.Enum):
    """Ticket status enum"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class TicketPriority(str, enum.Enum):
    """Ticket priority enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class TicketCategory(str, enum.Enum):
    """Ticket category enum"""
    TECHNICAL = "technical"
    MAINTENANCE = "maintenance"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    NETWORK = "network"
    USER_SUPPORT = "user_support"
    ACADEMIC = "academic"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


class SupportTicket(Base):
    """Support Ticket model for maintenance and support requests"""
    __tablename__ = "support_tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    # Ticket identification
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Classification
    category = Column(SQLEnum(TicketCategory), nullable=False, default=TicketCategory.OTHER)
    priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM)
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.OPEN, index=True)

    # Assignment
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_department = Column(String(100), nullable=True)

    # Location/Asset information
    location = Column(String(255), nullable=True)
    asset_id = Column(String(100), nullable=True)
    asset_name = Column(String(255), nullable=True)

    # Tracking
    due_date = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Resolution
    resolution_notes = Column(Text, nullable=True)
    resolution_time_minutes = Column(Integer, nullable=True)

    # Metadata
    tags = Column(ARRAY(String), nullable=True, default=list)
    attachments = Column(JSON, nullable=True, default=list)
    custom_fields = Column(JSON, nullable=True, default=dict)

    # SLA tracking
    sla_due_date = Column(DateTime(timezone=True), nullable=True)
    sla_breached = Column(Boolean, default=False)

    # Feedback
    satisfaction_rating = Column(Integer, nullable=True)  # 1-5 scale
    feedback_comment = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    history = relationship("TicketHistory", back_populates="ticket", cascade="all, delete-orphan")


class TicketComment(Base):
    """Comment on a support ticket"""
    __tablename__ = "ticket_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True)

    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal note vs public comment
    attachments = Column(JSON, nullable=True, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ticket = relationship("SupportTicket", back_populates="comments")


class TicketHistory(Base):
    """History log for ticket changes"""
    __tablename__ = "ticket_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True)

    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    change_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ticket = relationship("SupportTicket", back_populates="history")


class SupportCategory(Base):
    """Support category configuration"""
    __tablename__ = "support_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    color = Column(String(20), nullable=True)

    # SLA configuration
    default_priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM)
    sla_response_hours = Column(Integer, default=24)  # Hours for first response
    sla_resolution_hours = Column(Integer, default=72)  # Hours for resolution

    # Assignment rules
    auto_assign_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    auto_assign_department = Column(String(100), nullable=True)

    # Workflow
    requires_approval = Column(Boolean, default=False)
    approval_workflow_id = Column(UUID(as_uuid=True), nullable=True)

    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SupportKnowledgeBase(Base):
    """Knowledge base articles for self-service support"""
    __tablename__ = "support_knowledge_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)

    category_id = Column(UUID(as_uuid=True), ForeignKey("support_categories.id", ondelete="SET NULL"), nullable=True)
    tags = Column(ARRAY(String), nullable=True, default=list)

    # Visibility
    is_published = Column(Boolean, default=False)
    is_internal = Column(Boolean, default=False)  # Internal only vs public

    # Statistics
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)

    # Author
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
