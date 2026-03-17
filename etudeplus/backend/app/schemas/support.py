"""
Support Schemas for GROUP_AGENT (Support & Maintenance)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ==================== Ticket Status/Priority/Category Enums ====================
class TicketStatusSchema(BaseModel):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPrioritySchema(BaseModel):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategorySchema(BaseModel):
    TECHNICAL = "technical"
    ACCOUNT = "account"
    BILLING = "billing"
    ACADEMIC = "academic"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    OTHER = "other"


# ==================== Ticket Schemas ====================
class TicketBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    category: str = Field(default="other")
    priority: str = Field(default="medium")


class TicketCreate(TicketBase):
    pass


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    assigned_to_id: Optional[UUID] = None


class TicketResponse(TicketBase):
    id: UUID
    status: str
    reporter_id: UUID
    assigned_to_id: Optional[UUID] = None
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    sla_due_at: Optional[datetime] = None
    sla_breached: int = 0
    response_time_minutes: Optional[int] = None
    resolution_time_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    tenant_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    items: List[TicketResponse]
    total: int
    page: int
    pages: int


# ==================== Ticket Comment Schemas ====================
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    is_internal: bool = False


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: UUID
    ticket_id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Maintenance Log Schemas ====================
class MaintenanceLogBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    maintenance_type: str = Field(default="scheduled")
    affected_services: Optional[List[str]] = None


class MaintenanceLogCreate(MaintenanceLogBase):
    pass


class MaintenanceLogUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    maintenance_type: Optional[str] = None
    status: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    affected_services: Optional[List[str]] = None


class MaintenanceLogResponse(MaintenanceLogBase):
    id: UUID
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    performed_by_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    tenant_id: Optional[UUID] = None

    class Config:
        from_attributes = True


# ==================== Dashboard Stats ====================
class SupportDashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    avg_response_time_minutes: Optional[float] = None
    avg_resolution_time_minutes: Optional[float] = None
    sla_breached_count: int
    tickets_by_category: dict
    tickets_by_priority: dict
    recent_tickets: List[TicketResponse]
