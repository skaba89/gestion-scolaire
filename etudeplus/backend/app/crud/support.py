"""
CRUD Operations for Support Tickets (GropAgent) - Support and Maintenance Management
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import random
import string

from app.models.support_ticket import (
    SupportTicket, TicketComment, TicketHistory, SupportCategory, SupportKnowledgeBase,
    TicketStatus, TicketPriority, TicketCategory
)
from app.schemas.support import (
    SupportTicketCreate, SupportTicketUpdate,
    TicketCommentCreate, TicketCommentUpdate,
    SupportCategoryCreate, SupportCategoryUpdate,
    KnowledgeBaseCreate, KnowledgeBaseUpdate,
    SupportTicketFeedback
)


def generate_ticket_number() -> str:
    """Generate a unique ticket number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"TKT-{timestamp}-{random_suffix}"


# ============ Support Ticket CRUD ============

def create_ticket(
    db: Session,
    ticket_data: SupportTicketCreate,
    tenant_id: UUID,
    reported_by: Optional[UUID] = None
) -> SupportTicket:
    """Create a new support ticket"""
    ticket_number = generate_ticket_number()

    # Calculate SLA due date based on priority
    sla_hours = {
        TicketPriority.URGENT: 4,
        TicketPriority.CRITICAL: 8,
        TicketPriority.HIGH: 24,
        TicketPriority.MEDIUM: 48,
        TicketPriority.LOW: 72
    }
    sla_due = datetime.utcnow() + timedelta(hours=sla_hours.get(ticket_data.priority, 48))

    db_ticket = SupportTicket(
        tenant_id=tenant_id,
        ticket_number=ticket_number,
        title=ticket_data.title,
        description=ticket_data.description,
        category=ticket_data.category,
        priority=ticket_data.priority,
        status=TicketStatus.OPEN,
        reported_by=reported_by,
        assigned_to=ticket_data.assigned_to,
        assigned_department=ticket_data.assigned_department,
        location=ticket_data.location,
        asset_id=ticket_data.asset_id,
        asset_name=ticket_data.asset_name,
        due_date=ticket_data.due_date,
        tags=ticket_data.tags or [],
        attachments=ticket_data.attachments or [],
        custom_fields=ticket_data.custom_fields or {},
        sla_due_date=sla_due
    )

    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)

    # Create history entry
    create_history_entry(
        db, db_ticket.id, tenant_id, reported_by,
        "status", None, TicketStatus.OPEN.value, "Ticket created"
    )

    return db_ticket


def get_ticket(db: Session, ticket_id: UUID, tenant_id: UUID) -> Optional[SupportTicket]:
    """Get a ticket by ID"""
    return db.query(SupportTicket).filter(
        SupportTicket.id == ticket_id,
        SupportTicket.tenant_id == tenant_id
    ).first()


def get_ticket_by_number(db: Session, ticket_number: str, tenant_id: UUID) -> Optional[SupportTicket]:
    """Get a ticket by ticket number"""
    return db.query(SupportTicket).filter(
        SupportTicket.ticket_number == ticket_number,
        SupportTicket.tenant_id == tenant_id
    ).first()


def get_tickets(
    db: Session,
    tenant_id: UUID,
    skip: int = 0,
    limit: int = 100,
    status: Optional[List[TicketStatus]] = None,
    priority: Optional[List[TicketPriority]] = None,
    category: Optional[List[TicketCategory]] = None,
    assigned_to: Optional[UUID] = None,
    reported_by: Optional[UUID] = None,
    search: Optional[str] = None,
    overdue_only: bool = False
) -> List[SupportTicket]:
    """Get list of tickets with filters"""
    query = db.query(SupportTicket).filter(SupportTicket.tenant_id == tenant_id)

    if status:
        query = query.filter(SupportTicket.status.in_(status))
    if priority:
        query = query.filter(SupportTicket.priority.in_(priority))
    if category:
        query = query.filter(SupportTicket.category.in_(category))
    if assigned_to:
        query = query.filter(SupportTicket.assigned_to == assigned_to)
    if reported_by:
        query = query.filter(SupportTicket.reported_by == reported_by)
    if search:
        query = query.filter(or_(
            SupportTicket.title.ilike(f"%{search}%"),
            SupportTicket.description.ilike(f"%{search}%"),
            SupportTicket.ticket_number.ilike(f"%{search}%")
        ))
    if overdue_only:
        query = query.filter(
            SupportTicket.due_date < datetime.utcnow(),
            SupportTicket.status.not_in([TicketStatus.RESOLVED, TicketStatus.CLOSED])
        )

    return query.order_by(desc(SupportTicket.created_at)).offset(skip).limit(limit).all()


def update_ticket(
    db: Session,
    ticket_id: UUID,
    tenant_id: UUID,
    ticket_data: SupportTicketUpdate,
    changed_by: Optional[UUID] = None
) -> Optional[SupportTicket]:
    """Update a ticket"""
    ticket = get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        return None

    update_data = ticket_data.model_dump(exclude_unset=True)

    # Track changes in history
    for field, new_value in update_data.items():
        old_value = getattr(ticket, field, None)
        if old_value != new_value:
            create_history_entry(
                db, ticket_id, tenant_id, changed_by,
                field,
                str(old_value) if old_value else None,
                str(new_value) if new_value else None
            )

    # Handle status changes
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == TicketStatus.RESOLVED:
            update_data["resolved_at"] = datetime.utcnow()
            if ticket.created_at:
                update_data["resolution_time_minutes"] = int(
                    (datetime.utcnow() - ticket.created_at).total_seconds() / 60
                )
        elif new_status == TicketStatus.CLOSED:
            update_data["closed_at"] = datetime.utcnow()
        elif new_status == TicketStatus.REOPENED:
            update_data["resolved_at"] = None
            update_data["closed_at"] = None

    for field, value in update_data.items():
        setattr(ticket, field, value)

    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket_id: UUID, tenant_id: UUID) -> bool:
    """Delete a ticket"""
    ticket = get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        return False

    db.delete(ticket)
    db.commit()
    return True


def assign_ticket(
    db: Session,
    ticket_id: UUID,
    tenant_id: UUID,
    assigned_to: Optional[UUID],
    assigned_department: Optional[str] = None,
    assigned_by: Optional[UUID] = None
) -> Optional[SupportTicket]:
    """Assign a ticket to a user or department"""
    ticket = get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        return None

    old_assignee = ticket.assigned_to
    ticket.assigned_to = assigned_to
    if assigned_department:
        ticket.assigned_department = assigned_department

    if ticket.status == TicketStatus.OPEN:
        ticket.status = TicketStatus.IN_PROGRESS

    create_history_entry(
        db, ticket_id, tenant_id, assigned_by,
        "assigned_to",
        str(old_assignee) if old_assignee else None,
        str(assigned_to) if assigned_to else None,
        f"Ticket assigned to {'department ' + assigned_department if not assigned_to else 'user'}"
    )

    db.commit()
    db.refresh(ticket)
    return ticket


def add_feedback(
    db: Session,
    ticket_id: UUID,
    tenant_id: UUID,
    feedback: SupportTicketFeedback
) -> Optional[SupportTicket]:
    """Add satisfaction feedback to a resolved ticket"""
    ticket = get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        return None

    ticket.satisfaction_rating = feedback.satisfaction_rating
    ticket.feedback_comment = feedback.feedback_comment

    db.commit()
    db.refresh(ticket)
    return ticket


# ============ Ticket Comment CRUD ============

def create_comment(
    db: Session,
    ticket_id: UUID,
    tenant_id: UUID,
    comment_data: TicketCommentCreate,
    author_id: Optional[UUID] = None
) -> Optional[TicketComment]:
    """Add a comment to a ticket"""
    ticket = get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        return None

    comment = TicketComment(
        tenant_id=tenant_id,
        ticket_id=ticket_id,
        author_id=author_id,
        content=comment_data.content,
        is_internal=comment_data.is_internal,
        attachments=comment_data.attachments or []
    )

    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def get_ticket_comments(
    db: Session,
    ticket_id: UUID,
    tenant_id: UUID,
    include_internal: bool = False
) -> List[TicketComment]:
    """Get comments for a ticket"""
    query = db.query(TicketComment).filter(
        TicketComment.ticket_id == ticket_id,
        TicketComment.tenant_id == tenant_id
    )

    if not include_internal:
        query = query.filter(TicketComment.is_internal == False)

    return query.order_by(TicketComment.created_at).all()


def update_comment(
    db: Session,
    comment_id: UUID,
    tenant_id: UUID,
    comment_data: TicketCommentUpdate,
    author_id: Optional[UUID] = None
) -> Optional[TicketComment]:
    """Update a comment"""
    comment = db.query(TicketComment).filter(
        TicketComment.id == comment_id,
        TicketComment.tenant_id == tenant_id
    ).first()

    if not comment:
        return None

    # Only author can edit
    if author_id and comment.author_id != author_id:
        return None

    if comment_data.content:
        comment.content = comment_data.content

    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(
    db: Session,
    comment_id: UUID,
    tenant_id: UUID,
    author_id: Optional[UUID] = None
) -> bool:
    """Delete a comment"""
    comment = db.query(TicketComment).filter(
        TicketComment.id == comment_id,
        TicketComment.tenant_id == tenant_id
    ).first()

    if not comment:
        return False

    # Only author can delete
    if author_id and comment.author_id != author_id:
        return False

    db.delete(comment)
    db.commit()
    return True


# ============ History CRUD ============

def create_history_entry(
    db: Session,
    ticket_id: UUID,
    tenant_id: UUID,
    changed_by: Optional[UUID],
    field_name: str,
    old_value: Optional[str],
    new_value: Optional[str],
    change_reason: Optional[str] = None
) -> TicketHistory:
    """Create a history entry for a ticket change"""
    history = TicketHistory(
        tenant_id=tenant_id,
        ticket_id=ticket_id,
        changed_by=changed_by,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        change_reason=change_reason
    )

    db.add(history)
    db.commit()
    return history


def get_ticket_history(db: Session, ticket_id: UUID, tenant_id: UUID) -> List[TicketHistory]:
    """Get history for a ticket"""
    return db.query(TicketHistory).filter(
        TicketHistory.ticket_id == ticket_id,
        TicketHistory.tenant_id == tenant_id
    ).order_by(TicketHistory.created_at).all()


# ============ Support Category CRUD ============

def create_category(
    db: Session,
    category_data: SupportCategoryCreate,
    tenant_id: UUID
) -> SupportCategory:
    """Create a support category"""
    category = SupportCategory(
        tenant_id=tenant_id,
        **category_data.model_dump()
    )

    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_categories(db: Session, tenant_id: UUID, active_only: bool = True) -> List[SupportCategory]:
    """Get all categories for a tenant"""
    query = db.query(SupportCategory).filter(SupportCategory.tenant_id == tenant_id)

    if active_only:
        query = query.filter(SupportCategory.is_active == True)

    return query.order_by(SupportCategory.sort_order).all()


def update_category(
    db: Session,
    category_id: UUID,
    tenant_id: UUID,
    category_data: SupportCategoryUpdate
) -> Optional[SupportCategory]:
    """Update a category"""
    category = db.query(SupportCategory).filter(
        SupportCategory.id == category_id,
        SupportCategory.tenant_id == tenant_id
    ).first()

    if not category:
        return None

    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


# ============ Knowledge Base CRUD ============

def create_knowledge_article(
    db: Session,
    article_data: KnowledgeBaseCreate,
    tenant_id: UUID,
    author_id: Optional[UUID] = None
) -> SupportKnowledgeBase:
    """Create a knowledge base article"""
    article = SupportKnowledgeBase(
        tenant_id=tenant_id,
        author_id=author_id,
        **article_data.model_dump()
    )

    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_knowledge_articles(
    db: Session,
    tenant_id: UUID,
    category_id: Optional[UUID] = None,
    published_only: bool = True,
    search: Optional[str] = None
) -> List[SupportKnowledgeBase]:
    """Get knowledge base articles"""
    query = db.query(SupportKnowledgeBase).filter(
        SupportKnowledgeBase.tenant_id == tenant_id
    )

    if published_only:
        query = query.filter(SupportKnowledgeBase.is_published == True)

    if category_id:
        query = query.filter(SupportKnowledgeBase.category_id == category_id)

    if search:
        query = query.filter(or_(
            SupportKnowledgeBase.title.ilike(f"%{search}%"),
            SupportKnowledgeBase.content.ilike(f"%{search}%")
        ))

    return query.order_by(desc(SupportKnowledgeBase.view_count)).all()


def increment_article_view(db: Session, article_id: UUID, tenant_id: UUID) -> None:
    """Increment view count for an article"""
    article = db.query(SupportKnowledgeBase).filter(
        SupportKnowledgeBase.id == article_id,
        SupportKnowledgeBase.tenant_id == tenant_id
    ).first()

    if article:
        article.view_count += 1
        db.commit()


# ============ Statistics ============

def get_dashboard_stats(db: Session, tenant_id: UUID) -> Dict[str, Any]:
    """Get dashboard statistics for support tickets"""

    # Total counts by status
    status_counts = db.query(
        SupportTicket.status,
        func.count(SupportTicket.id)
    ).filter(SupportTicket.tenant_id == tenant_id).group_by(SupportTicket.status).all()

    status_dict = {str(s): c for s, c in status_counts}

    # Overdue tickets
    overdue_count = db.query(SupportTicket).filter(
        SupportTicket.tenant_id == tenant_id,
        SupportTicket.sla_due_date < datetime.utcnow(),
        SupportTicket.status.not_in([TicketStatus.RESOLVED, TicketStatus.CLOSED])
    ).count()

    # Average resolution time
    avg_resolution = db.query(
        func.avg(SupportTicket.resolution_time_minutes)
    ).filter(
        SupportTicket.tenant_id == tenant_id,
        SupportTicket.resolution_time_minutes.isnot(None)
    ).scalar()

    # Tickets by category
    category_counts = db.query(
        SupportTicket.category,
        func.count(SupportTicket.id)
    ).filter(SupportTicket.tenant_id == tenant_id).group_by(SupportTicket.category).all()

    category_dict = {str(c): count for c, count in category_counts}

    # Tickets by priority
    priority_counts = db.query(
        SupportTicket.priority,
        func.count(SupportTicket.id)
    ).filter(SupportTicket.tenant_id == tenant_id).group_by(SupportTicket.priority).all()

    priority_dict = {str(p): count for p, count in priority_counts}

    # Average satisfaction
    avg_satisfaction = db.query(
        func.avg(SupportTicket.satisfaction_rating)
    ).filter(
        SupportTicket.tenant_id == tenant_id,
        SupportTicket.satisfaction_rating.isnot(None)
    ).scalar()

    return {
        "total_tickets": sum(status_dict.values()),
        "open_tickets": status_dict.get(TicketStatus.OPEN.value, 0) + status_dict.get(TicketStatus.REOPENED.value, 0),
        "in_progress_tickets": status_dict.get(TicketStatus.IN_PROGRESS.value, 0) + status_dict.get(TicketStatus.PENDING.value, 0),
        "resolved_tickets": status_dict.get(TicketStatus.RESOLVED.value, 0),
        "closed_tickets": status_dict.get(TicketStatus.CLOSED.value, 0),
        "overdue_tickets": overdue_count,
        "avg_resolution_time_minutes": float(avg_resolution) if avg_resolution else None,
        "tickets_by_category": category_dict,
        "tickets_by_priority": priority_dict,
        "satisfaction_avg": float(avg_satisfaction) if avg_satisfaction else None
    }
