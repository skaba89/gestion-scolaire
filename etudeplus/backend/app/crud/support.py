"""
Support CRUD Operations for GROUP_AGENT (Support & Maintenance)
"""
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from app.models.support import SupportTicket, TicketComment, MaintenanceLog, TicketStatus, TicketPriority
from app.schemas.support import TicketCreate, TicketUpdate, CommentCreate, MaintenanceLogCreate, MaintenanceLogUpdate


# ==================== Ticket CRUD ====================
def create_ticket(db: Session, ticket_data: TicketCreate, reporter_id: UUID, tenant_id: UUID) -> SupportTicket:
    """Create a new support ticket."""
    # Calculate SLA due date based on priority
    sla_hours = {
        "critical": 1,
        "high": 4,
        "medium": 24,
        "low": 72,
    }
    priority = ticket_data.priority.lower()
    sla_due = datetime.utcnow() + timedelta(hours=sla_hours.get(priority, 24))

    ticket = SupportTicket(
        title=ticket_data.title,
        description=ticket_data.description,
        category=ticket_data.category,
        priority=priority,
        status="open",
        reporter_id=reporter_id,
        tenant_id=tenant_id,
        sla_due_at=sla_due,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: UUID, tenant_id: UUID) -> Optional[SupportTicket]:
    """Get a ticket by ID."""
    return db.query(SupportTicket).filter(
        and_(SupportTicket.id == ticket_id, SupportTicket.tenant_id == tenant_id)
    ).first()


def get_tickets(
    db: Session,
    tenant_id: UUID,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to_id: Optional[UUID] = None,
    reporter_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[SupportTicket], int]:
    """Get filtered list of tickets."""
    query = db.query(SupportTicket).filter(SupportTicket.tenant_id == tenant_id)

    if status:
        query = query.filter(SupportTicket.status == status)
    if priority:
        query = query.filter(SupportTicket.priority == priority)
    if category:
        query = query.filter(SupportTicket.category == category)
    if assigned_to_id:
        query = query.filter(SupportTicket.assigned_to_id == assigned_to_id)
    if reporter_id:
        query = query.filter(SupportTicket.reporter_id == reporter_id)

    total = query.count()
    tickets = query.order_by(desc(SupportTicket.created_at)).offset(skip).limit(limit).all()
    return tickets, total


def update_ticket(db: Session, ticket_id: UUID, ticket_data: TicketUpdate, tenant_id: UUID) -> Optional[SupportTicket]:
    """Update a ticket."""
    ticket = get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        return None

    update_data = ticket_data.model_dump(exclude_unset=True)

    # Handle status changes
    if "status" in update_data:
        now = datetime.utcnow()
        if update_data["status"] == "in_progress" and not ticket.first_response_at:
            update_data["first_response_at"] = now
            update_data["response_time_minutes"] = int((now - ticket.created_at).total_seconds() / 60)
        elif update_data["status"] == "resolved":
            update_data["resolved_at"] = now
            update_data["resolution_time_minutes"] = int((now - ticket.created_at).total_seconds() / 60)
        elif update_data["status"] == "closed":
            update_data["closed_at"] = now

    for key, value in update_data.items():
        setattr(ticket, key, value)

    db.commit()
    db.refresh(ticket)
    return ticket


def assign_ticket(db: Session, ticket_id: UUID, agent_id: UUID, tenant_id: UUID) -> Optional[SupportTicket]:
    """Assign a ticket to an agent."""
    ticket = get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        return None

    ticket.assigned_to_id = agent_id
    if ticket.status == "open":
        ticket.status = "in_progress"
        ticket.first_response_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket_id: UUID, tenant_id: UUID) -> bool:
    """Delete a ticket."""
    ticket = get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        return False
    db.delete(ticket)
    db.commit()
    return True


# ==================== Comment CRUD ====================
def create_comment(db: Session, ticket_id: UUID, comment_data: CommentCreate, author_id: UUID, tenant_id: UUID) -> Optional[TicketComment]:
    """Add a comment to a ticket."""
    ticket = get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        return None

    comment = TicketComment(
        ticket_id=ticket_id,
        author_id=author_id,
        content=comment_data.content,
        is_internal=1 if comment_data.is_internal else 0,
        tenant_id=tenant_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_ticket_comments(db: Session, ticket_id: UUID, tenant_id: UUID) -> List[TicketComment]:
    """Get all comments for a ticket."""
    return db.query(TicketComment).filter(
        and_(TicketComment.ticket_id == ticket_id, TicketComment.tenant_id == tenant_id)
    ).order_by(TicketComment.created_at).all()


# ==================== Maintenance Log CRUD ====================
def create_maintenance_log(db: Session, log_data: MaintenanceLogCreate, performed_by_id: UUID, tenant_id: UUID) -> MaintenanceLog:
    """Create a maintenance log entry."""
    import json
    log = MaintenanceLog(
        title=log_data.title,
        description=log_data.description,
        maintenance_type=log_data.maintenance_type,
        affected_services=json.dumps(log_data.affected_services) if log_data.affected_services else None,
        performed_by_id=performed_by_id,
        tenant_id=tenant_id,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_maintenance_logs(
    db: Session,
    tenant_id: UUID,
    status: Optional[str] = None,
    maintenance_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[MaintenanceLog], int]:
    """Get filtered maintenance logs."""
    query = db.query(MaintenanceLog).filter(MaintenanceLog.tenant_id == tenant_id)

    if status:
        query = query.filter(MaintenanceLog.status == status)
    if maintenance_type:
        query = query.filter(MaintenanceLog.maintenance_type == maintenance_type)

    total = query.count()
    logs = query.order_by(desc(MaintenanceLog.created_at)).offset(skip).limit(limit).all()
    return logs, total


def update_maintenance_log(db: Session, log_id: UUID, log_data: MaintenanceLogUpdate, tenant_id: UUID) -> Optional[MaintenanceLog]:
    """Update a maintenance log."""
    log = db.query(MaintenanceLog).filter(
        and_(MaintenanceLog.id == log_id, MaintenanceLog.tenant_id == tenant_id)
    ).first()
    if not log:
        return None

    update_data = log_data.model_dump(exclude_unset=True)
    if "affected_services" in update_data and update_data["affected_services"]:
        import json
        update_data["affected_services"] = json.dumps(update_data["affected_services"])

    for key, value in update_data.items():
        setattr(log, key, value)

    db.commit()
    db.refresh(log)
    return log


# ==================== Dashboard Stats ====================
def get_support_stats(db: Session, tenant_id: UUID) -> dict:
    """Get support dashboard statistics."""
    from sqlalchemy import func

    # Total tickets by status
    status_counts = db.query(
        SupportTicket.status,
        func.count(SupportTicket.id)
    ).filter(SupportTicket.tenant_id == tenant_id).group_by(SupportTicket.status).all()

    status_dict = {s: c for s, c in status_counts}

    # Average response time
    avg_response = db.query(func.avg(SupportTicket.response_time_minutes)).filter(
        and_(SupportTicket.tenant_id == tenant_id, SupportTicket.response_time_minutes.isnot(None))
    ).scalar()

    # Average resolution time
    avg_resolution = db.query(func.avg(SupportTicket.resolution_time_minutes)).filter(
        and_(SupportTicket.tenant_id == tenant_id, SupportTicket.resolution_time_minutes.isnot(None))
    ).scalar()

    # SLA breached count
    sla_breached = db.query(func.count(SupportTicket.id)).filter(
        and_(SupportTicket.tenant_id == tenant_id, SupportTicket.sla_breached == 1)
    ).scalar()

    # Tickets by category
    category_counts = db.query(
        SupportTicket.category,
        func.count(SupportTicket.id)
    ).filter(SupportTicket.tenant_id == tenant_id).group_by(SupportTicket.category).all()

    # Tickets by priority
    priority_counts = db.query(
        SupportTicket.priority,
        func.count(SupportTicket.id)
    ).filter(SupportTicket.tenant_id == tenant_id).group_by(SupportTicket.priority).all()

    # Recent tickets
    recent = db.query(SupportTicket).filter(
        SupportTicket.tenant_id == tenant_id
    ).order_by(desc(SupportTicket.created_at)).limit(5).all()

    return {
        "total_tickets": sum(status_dict.values()),
        "open_tickets": status_dict.get("open", 0),
        "in_progress_tickets": status_dict.get("in_progress", 0),
        "resolved_tickets": status_dict.get("resolved", 0),
        "closed_tickets": status_dict.get("closed", 0),
        "avg_response_time_minutes": float(avg_response) if avg_response else None,
        "avg_resolution_time_minutes": float(avg_resolution) if avg_resolution else None,
        "sla_breached_count": sla_breached or 0,
        "tickets_by_category": dict(category_counts),
        "tickets_by_priority": dict(priority_counts),
        "recent_tickets": recent,
    }


# Import timedelta for SLA calculation
from datetime import timedelta
