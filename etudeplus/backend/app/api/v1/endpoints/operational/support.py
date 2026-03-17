"""
Support API Endpoints for GROUP_AGENT (Support & Maintenance)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.crud import support as crud_support
from app.schemas.support import (
    TicketCreate, TicketUpdate, TicketResponse, TicketListResponse,
    CommentCreate, CommentResponse,
    MaintenanceLogCreate, MaintenanceLogUpdate, MaintenanceLogResponse,
    SupportDashboardStats,
)

router = APIRouter(prefix="/support", tags=["support"])


# ==================== Dashboard ====================
@router.get("/dashboard", response_model=SupportDashboardStats)
def get_support_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("support:read")),
):
    """Get support dashboard statistics (GROUP_AGENT only)."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    stats = crud_support.get_support_stats(db, UUID(tenant_id))
    return stats


# ==================== Tickets ====================
@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new support ticket."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    return crud_support.create_ticket(
        db, ticket_data, UUID(current_user["id"]), UUID(tenant_id)
    )


@router.get("/tickets", response_model=TicketListResponse)
def list_tickets(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    assigned_to_id: Optional[UUID] = Query(None),
    reporter_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("tickets:read")),
):
    """List support tickets with filters."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    skip = (page - 1) * per_page
    tickets, total = crud_support.get_tickets(
        db, UUID(tenant_id),
        status=status, priority=priority, category=category,
        assigned_to_id=assigned_to_id, reporter_id=reporter_id,
        skip=skip, limit=per_page,
    )

    return TicketListResponse(
        items=tickets,
        total=total,
        page=page,
        pages=(total + per_page - 1) // per_page,
    )


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("tickets:read")),
):
    """Get a specific ticket."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    ticket = crud_support.get_ticket(db, ticket_id, UUID(tenant_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: UUID,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("tickets:write")),
):
    """Update a ticket."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    ticket = crud_support.update_ticket(db, ticket_id, ticket_data, UUID(tenant_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.post("/tickets/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: UUID,
    agent_id: UUID = Query(..., description="Agent UUID to assign"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("tickets:assign")),
):
    """Assign a ticket to an agent."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    ticket = crud_support.assign_ticket(db, ticket_id, agent_id, UUID(tenant_id))
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.delete("/tickets/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("support:delete")),
):
    """Delete a ticket."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    if not crud_support.delete_ticket(db, ticket_id, UUID(tenant_id)):
        raise HTTPException(status_code=404, detail="Ticket not found")


# ==================== Comments ====================
@router.post("/tickets/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    ticket_id: UUID,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Add a comment to a ticket."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    comment = crud_support.create_comment(
        db, ticket_id, comment_data, UUID(current_user["id"]), UUID(tenant_id)
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return comment


@router.get("/tickets/{ticket_id}/comments", response_model=list[CommentResponse])
def get_comments(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("tickets:read")),
):
    """Get all comments for a ticket."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    return crud_support.get_ticket_comments(db, ticket_id, UUID(tenant_id))


# ==================== Maintenance Logs ====================
@router.post("/maintenance", response_model=MaintenanceLogResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_log(
    log_data: MaintenanceLogCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("maintenance:write")),
):
    """Create a maintenance log entry."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    return crud_support.create_maintenance_log(
        db, log_data, UUID(current_user["id"]), UUID(tenant_id)
    )


@router.get("/maintenance", response_model=list[MaintenanceLogResponse])
def list_maintenance_logs(
    status: Optional[str] = Query(None),
    maintenance_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("maintenance:read")),
):
    """List maintenance logs."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    skip = (page - 1) * per_page
    logs, _ = crud_support.get_maintenance_logs(
        db, UUID(tenant_id),
        status=status, maintenance_type=maintenance_type,
        skip=skip, limit=per_page,
    )
    return logs


@router.patch("/maintenance/{log_id}", response_model=MaintenanceLogResponse)
def update_maintenance_log(
    log_id: UUID,
    log_data: MaintenanceLogUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("maintenance:write")),
):
    """Update a maintenance log."""
    tenant_id = current_user.get("tenant_id")
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant ID required")

    log = crud_support.update_maintenance_log(db, log_id, log_data, UUID(tenant_id))
    if not log:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    return log
