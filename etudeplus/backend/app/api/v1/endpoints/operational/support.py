"""
Support Ticket API Endpoints (GropAgent) - Support and Maintenance Management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.models.support_ticket import TicketStatus, TicketPriority, TicketCategory
from app.schemas.support import (
    SupportTicketCreate, SupportTicketUpdate, SupportTicketResponse, SupportTicketListResponse,
    TicketCommentCreate, TicketCommentUpdate, TicketCommentResponse,
    TicketHistoryResponse,
    SupportCategoryCreate, SupportCategoryUpdate, SupportCategoryResponse,
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse,
    SupportDashboardStats, SupportTicketFeedback
)
from app.crud import support as support_crud

router = APIRouter()


# ============ Dashboard & Statistics ============

@router.get("/dashboard", response_model=SupportDashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get support dashboard statistics"""
    tenant_id = current_user["tenant_id"]
    return support_crud.get_dashboard_stats(db, tenant_id)


# ============ Support Tickets ============

@router.get("/", response_model=List[SupportTicketListResponse])
def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[List[TicketStatus]] = Query(None),
    priority: Optional[List[TicketPriority]] = Query(None),
    category: Optional[List[TicketCategory]] = Query(None),
    assigned_to: Optional[UUID] = None,
    reported_by: Optional[UUID] = None,
    search: Optional[str] = None,
    overdue_only: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List support tickets with filters"""
    tenant_id = current_user["tenant_id"]
    return support_crud.get_tickets(
        db, tenant_id, skip, limit, status, priority, category,
        assigned_to, reported_by, search, overdue_only
    )


@router.get("/{ticket_id}", response_model=SupportTicketResponse)
def get_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific support ticket"""
    tenant_id = current_user["tenant_id"]
    ticket = support_crud.get_ticket(db, ticket_id, tenant_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return ticket


@router.get("/number/{ticket_number}", response_model=SupportTicketResponse)
def get_ticket_by_number(
    ticket_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a ticket by its ticket number"""
    tenant_id = current_user["tenant_id"]
    ticket = support_crud.get_ticket_by_number(db, ticket_number, tenant_id)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return ticket


@router.post("/", response_model=SupportTicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: SupportTicketCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new support ticket"""
    tenant_id = current_user["tenant_id"]
    user_id = current_user.get("user_id")

    ticket = support_crud.create_ticket(
        db, ticket_data, tenant_id, user_id
    )

    return ticket


@router.put("/{ticket_id}", response_model=SupportTicketResponse)
def update_ticket(
    ticket_id: UUID,
    ticket_data: SupportTicketUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a support ticket"""
    tenant_id = current_user["tenant_id"]
    user_id = current_user.get("user_id")

    ticket = support_crud.update_ticket(
        db, ticket_id, tenant_id, ticket_data, user_id
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return ticket


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("support:delete"))
):
    """Delete a support ticket (requires permission)"""
    tenant_id = current_user["tenant_id"]

    success = support_crud.delete_ticket(db, ticket_id, tenant_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )


@router.post("/{ticket_id}/assign", response_model=SupportTicketResponse)
def assign_ticket(
    ticket_id: UUID,
    assigned_to: Optional[UUID] = None,
    assigned_department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Assign a ticket to a user or department"""
    tenant_id = current_user["tenant_id"]
    user_id = current_user.get("user_id")

    ticket = support_crud.assign_ticket(
        db, ticket_id, tenant_id, assigned_to, assigned_department, user_id
    )

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return ticket


@router.post("/{ticket_id}/feedback", response_model=SupportTicketResponse)
def add_ticket_feedback(
    ticket_id: UUID,
    feedback: SupportTicketFeedback,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add satisfaction feedback to a resolved ticket"""
    tenant_id = current_user["tenant_id"]

    ticket = support_crud.add_feedback(db, ticket_id, tenant_id, feedback)

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return ticket


# ============ Ticket Comments ============

@router.get("/{ticket_id}/comments", response_model=List[TicketCommentResponse])
def list_ticket_comments(
    ticket_id: UUID,
    include_internal: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List comments for a ticket"""
    tenant_id = current_user["tenant_id"]

    # Check ticket exists
    ticket = support_crud.get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return support_crud.get_ticket_comments(
        db, ticket_id, tenant_id,
        include_internal=include_internal
    )


@router.post("/{ticket_id}/comments", response_model=TicketCommentResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_comment(
    ticket_id: UUID,
    comment_data: TicketCommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a comment to a ticket"""
    tenant_id = current_user["tenant_id"]
    user_id = current_user.get("user_id")

    comment = support_crud.create_comment(
        db, ticket_id, tenant_id, comment_data, user_id
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return comment


@router.put("/{ticket_id}/comments/{comment_id}", response_model=TicketCommentResponse)
def update_ticket_comment(
    ticket_id: UUID,
    comment_id: UUID,
    comment_data: TicketCommentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a comment"""
    tenant_id = current_user["tenant_id"]
    user_id = current_user.get("user_id")

    comment = support_crud.update_comment(
        db, comment_id, tenant_id, comment_data, user_id
    )

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to edit"
        )

    return comment


@router.delete("/{ticket_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket_comment(
    ticket_id: UUID,
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a comment"""
    tenant_id = current_user["tenant_id"]
    user_id = current_user.get("user_id")

    success = support_crud.delete_comment(db, comment_id, tenant_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete"
        )


# ============ Ticket History ============

@router.get("/{ticket_id}/history", response_model=List[TicketHistoryResponse])
def list_ticket_history(
    ticket_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get history for a ticket"""
    tenant_id = current_user["tenant_id"]

    # Check ticket exists
    ticket = support_crud.get_ticket(db, ticket_id, tenant_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    return support_crud.get_ticket_history(db, ticket_id, tenant_id)


# ============ Support Categories ============

@router.get("/categories/", response_model=List[SupportCategoryResponse])
def list_categories(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List support categories"""
    tenant_id = current_user["tenant_id"]
    return support_crud.get_categories(db, tenant_id, active_only)


@router.post("/categories/", response_model=SupportCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: SupportCategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("support:manage"))
):
    """Create a support category (requires permission)"""
    tenant_id = current_user["tenant_id"]
    return support_crud.create_category(db, category_data, tenant_id)


@router.put("/categories/{category_id}", response_model=SupportCategoryResponse)
def update_category(
    category_id: UUID,
    category_data: SupportCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("support:manage"))
):
    """Update a support category (requires permission)"""
    tenant_id = current_user["tenant_id"]

    category = support_crud.update_category(db, category_id, tenant_id, category_data)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


# ============ Knowledge Base ============

@router.get("/knowledge-base/", response_model=List[KnowledgeBaseResponse])
def list_knowledge_articles(
    category_id: Optional[UUID] = None,
    published_only: bool = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List knowledge base articles"""
    tenant_id = current_user["tenant_id"]
    return support_crud.get_knowledge_articles(
        db, tenant_id, category_id, published_only, search
    )


@router.post("/knowledge-base/", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_article(
    article_data: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("support:manage"))
):
    """Create a knowledge base article (requires permission)"""
    tenant_id = current_user["tenant_id"]
    user_id = current_user.get("user_id")
    return support_crud.create_knowledge_article(db, article_data, tenant_id, user_id)


@router.post("/knowledge-base/{article_id}/view")
def increment_article_views(
    article_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Increment view count for an article"""
    tenant_id = current_user["tenant_id"]
    support_crud.increment_article_view(db, article_id, tenant_id)
    return {"status": "ok"}
