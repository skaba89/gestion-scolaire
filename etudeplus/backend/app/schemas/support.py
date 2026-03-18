"""
Pydantic Schemas for Support Ticket (GropAgent) - Support and Maintenance Management
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"


class TicketCategory(str, Enum):
    TECHNICAL = "technical"
    MAINTENANCE = "maintenance"
    SOFTWARE = "software"
    HARDWARE = "hardware"
    NETWORK = "network"
    USER_SUPPORT = "user_support"
    ACADEMIC = "academic"
    ADMINISTRATIVE = "administrative"
    OTHER = "other"


# ============ Ticket Comment Schemas ============

class TicketCommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    is_internal: bool = False


class TicketCommentCreate(TicketCommentBase):
    attachments: Optional[List[Dict[str, Any]]] = None


class TicketCommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=5000)


class TicketCommentResponse(TicketCommentBase):
    id: UUID
    tenant_id: UUID
    ticket_id: UUID
    author_id: Optional[UUID]
    author_name: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============ Ticket History Schemas ============

class TicketHistoryResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    changed_by: Optional[UUID]
    changed_by_name: Optional[str] = None
    field_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    change_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ Support Ticket Schemas ============

class SupportTicketBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    category: TicketCategory = TicketCategory.OTHER
    priority: TicketPriority = TicketPriority.MEDIUM
    location: Optional[str] = Field(None, max_length=255)
    asset_id: Optional[str] = Field(None, max_length=100)
    asset_name: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None


class SupportTicketCreate(SupportTicketBase):
    assigned_to: Optional[UUID] = None
    assigned_department: Optional[str] = None
    due_date: Optional[datetime] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class SupportTicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_to: Optional[UUID] = None
    assigned_department: Optional[str] = None
    location: Optional[str] = None
    asset_id: Optional[str] = None
    asset_name: Optional[str] = None
    due_date: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class SupportTicketResponse(SupportTicketBase):
    id: UUID
    tenant_id: UUID
    ticket_number: str
    status: TicketStatus
    reported_by: Optional[UUID]
    reporter_name: Optional[str] = None
    assigned_to: Optional[UUID]
    assignee_name: Optional[str] = None
    assigned_department: Optional[str]
    due_date: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    resolution_notes: Optional[str]
    resolution_time_minutes: Optional[int]
    attachments: Optional[List[Dict[str, Any]]]
    custom_fields: Optional[Dict[str, Any]]
    sla_due_date: Optional[datetime]
    sla_breached: bool
    satisfaction_rating: Optional[int]
    feedback_comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    comments: List[TicketCommentResponse] = []
    history: List[TicketHistoryResponse] = []

    class Config:
        from_attributes = True


class SupportTicketListResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    ticket_number: str
    title: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus
    reporter_name: Optional[str]
    assignee_name: Optional[str]
    location: Optional[str]
    created_at: datetime
    due_date: Optional[datetime]
    sla_breached: bool

    class Config:
        from_attributes = True


# ============ Support Category Schemas ============

class SupportCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=20)
    default_priority: TicketPriority = TicketPriority.MEDIUM
    sla_response_hours: int = 24
    sla_resolution_hours: int = 72
    auto_assign_department: Optional[str] = None
    requires_approval: bool = False
    is_active: bool = True
    sort_order: int = 0


class SupportCategoryCreate(SupportCategoryBase):
    auto_assign_to: Optional[UUID] = None


class SupportCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    default_priority: Optional[TicketPriority] = None
    sla_response_hours: Optional[int] = None
    sla_resolution_hours: Optional[int] = None
    auto_assign_to: Optional[UUID] = None
    auto_assign_department: Optional[str] = None
    requires_approval: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class SupportCategoryResponse(SupportCategoryBase):
    id: UUID
    tenant_id: UUID
    auto_assign_to: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============ Knowledge Base Schemas ============

class KnowledgeBaseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=10)
    summary: Optional[str] = Field(None, max_length=500)
    category_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    is_published: bool = False
    is_internal: bool = False


class KnowledgeBaseCreate(KnowledgeBaseBase):
    pass


class KnowledgeBaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    content: Optional[str] = Field(None, min_length=10)
    summary: Optional[str] = None
    category_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_internal: Optional[bool] = None


class KnowledgeBaseResponse(KnowledgeBaseBase):
    id: UUID
    tenant_id: UUID
    author_id: Optional[UUID]
    author_name: Optional[str] = None
    view_count: int
    helpful_count: int
    not_helpful_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============ Statistics & Dashboard Schemas ============

class SupportDashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_tickets: int
    closed_tickets: int
    overdue_tickets: int
    avg_resolution_time_minutes: Optional[float]
    tickets_by_category: Dict[str, int]
    tickets_by_priority: Dict[str, int]
    satisfaction_avg: Optional[float]


class SupportTicketFeedback(BaseModel):
    satisfaction_rating: int = Field(..., ge=1, le=5)
    feedback_comment: Optional[str] = Field(None, max_length=1000)
