"""
Library CRUD Operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from uuid import UUID
from datetime import date, timedelta

from app.models.library import (
    LibraryCategory, LibraryResource, LibraryLoan, 
    LibraryReservation, LibraryInventoryItem
)
from app.schemas.library import (
    LibraryCategoryCreate, LibraryCategoryUpdate,
    LibraryResourceCreate, LibraryResourceUpdate,
    LibraryLoanCreate, LibraryLoanUpdate, LibraryLoanRenew,
    LibraryReservationCreate, LibraryReservationUpdate,
    LibraryInventoryCreate, LibraryInventoryUpdate
)


# ─── Categories ───────────────────────────────────────────────────────────

def get_categories(db: Session, tenant_id: UUID) -> List[LibraryCategory]:
    """Get all categories for a tenant."""
    return db.query(LibraryCategory).filter(
        LibraryCategory.tenant_id == tenant_id
    ).order_by(LibraryCategory.name).all()


def get_category(db: Session, category_id: UUID, tenant_id: UUID) -> Optional[LibraryCategory]:
    """Get a specific category."""
    return db.query(LibraryCategory).filter(
        LibraryCategory.id == category_id,
        LibraryCategory.tenant_id == tenant_id
    ).first()


def create_category(db: Session, obj_in: LibraryCategoryCreate, tenant_id: UUID) -> LibraryCategory:
    """Create a new category."""
    category = LibraryCategory(**obj_in.model_dump(), tenant_id=tenant_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: UUID, obj_in: LibraryCategoryUpdate, tenant_id: UUID) -> Optional[LibraryCategory]:
    """Update a category."""
    category = get_category(db, category_id, tenant_id)
    if not category:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category_id: UUID, tenant_id: UUID) -> bool:
    """Delete a category."""
    category = get_category(db, category_id, tenant_id)
    if not category:
        return False
    db.delete(category)
    db.commit()
    return True


# ─── Resources ───────────────────────────────────────────────────────────

def get_resources(
    db: Session, 
    tenant_id: UUID,
    category_id: Optional[UUID] = None,
    resource_type: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[LibraryResource]:
    """Get resources with optional filters."""
    query = db.query(LibraryResource).filter(LibraryResource.tenant_id == tenant_id)
    
    if category_id:
        query = query.filter(LibraryResource.category_id == category_id)
    
    if resource_type:
        query = query.filter(LibraryResource.resource_type == resource_type)
    
    if status:
        query = query.filter(LibraryResource.status == status)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                LibraryResource.title.ilike(search_pattern),
                LibraryResource.author.ilike(search_pattern),
                LibraryResource.isbn.ilike(search_pattern),
                LibraryResource.description.ilike(search_pattern)
            )
        )
    
    return query.order_by(LibraryResource.title).offset(skip).limit(limit).all()


def get_resource(db: Session, resource_id: UUID, tenant_id: UUID) -> Optional[LibraryResource]:
    """Get a specific resource."""
    return db.query(LibraryResource).filter(
        LibraryResource.id == resource_id,
        LibraryResource.tenant_id == tenant_id
    ).first()


def get_resource_by_isbn(db: Session, isbn: str, tenant_id: UUID) -> Optional[LibraryResource]:
    """Get a resource by ISBN."""
    return db.query(LibraryResource).filter(
        LibraryResource.isbn == isbn,
        LibraryResource.tenant_id == tenant_id
    ).first()


def create_resource(db: Session, obj_in: LibraryResourceCreate, tenant_id: UUID) -> LibraryResource:
    """Create a new resource."""
    resource = LibraryResource(
        **obj_in.model_dump(),
        available_copies=obj_in.total_copies,
        status="available",
        tenant_id=tenant_id
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def update_resource(db: Session, resource_id: UUID, obj_in: LibraryResourceUpdate, tenant_id: UUID) -> Optional[LibraryResource]:
    """Update a resource."""
    resource = get_resource(db, resource_id, tenant_id)
    if not resource:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
    
    db.commit()
    db.refresh(resource)
    return resource


def delete_resource(db: Session, resource_id: UUID, tenant_id: UUID) -> bool:
    """Delete a resource."""
    resource = get_resource(db, resource_id, tenant_id)
    if not resource:
        return False
    db.delete(resource)
    db.commit()
    return True


# ─── Loans ───────────────────────────────────────────────────────────────

def get_loans(
    db: Session,
    tenant_id: UUID,
    user_id: Optional[UUID] = None,
    status: Optional[str] = None,
    overdue_only: bool = False,
    skip: int = 0,
    limit: int = 20
) -> List[LibraryLoan]:
    """Get loans with optional filters."""
    query = db.query(LibraryLoan).filter(LibraryLoan.tenant_id == tenant_id)
    
    if user_id:
        query = query.filter(LibraryLoan.user_id == user_id)
    
    if status:
        query = query.filter(LibraryLoan.status == status)
    
    if overdue_only:
        query = query.filter(
            LibraryLoan.status == "active",
            LibraryLoan.due_date < date.today()
        )
    
    return query.order_by(LibraryLoan.loan_date.desc()).offset(skip).limit(limit).all()


def get_loan(db: Session, loan_id: UUID, tenant_id: UUID) -> Optional[LibraryLoan]:
    """Get a specific loan."""
    return db.query(LibraryLoan).filter(
        LibraryLoan.id == loan_id,
        LibraryLoan.tenant_id == tenant_id
    ).first()


def create_loan(db: Session, obj_in: LibraryLoanCreate, tenant_id: UUID) -> LibraryLoan:
    """Create a new loan (borrow a book)."""
    resource = get_resource(db, obj_in.resource_id, tenant_id)
    if not resource:
        raise ValueError("Resource not found")
    
    if resource.available_copies <= 0:
        raise ValueError("No available copies")
    
    if not resource.is_borrowable:
        raise ValueError("This resource is not borrowable")
    
    # Calculate dates
    loan_date = date.today()
    due_date = loan_date + timedelta(days=obj_in.loan_days or resource.max_loan_days)
    
    # Create loan
    loan = LibraryLoan(
        resource_id=obj_in.resource_id,
        user_id=obj_in.user_id,
        loan_date=loan_date,
        due_date=due_date,
        status="active",
        tenant_id=tenant_id,
        notes=obj_in.notes
    )
    
    # Update resource
    resource.available_copies -= 1
    resource.times_borrowed += 1
    if resource.available_copies == 0:
        resource.status = "borrowed"
    
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan_id: UUID, obj_in: LibraryLoanUpdate, tenant_id: UUID) -> Optional[LibraryLoan]:
    """Return a borrowed book."""
    loan = get_loan(db, loan_id, tenant_id)
    if not loan:
        return None
    
    if loan.status != "active":
        raise ValueError("Loan is not active")
    
    # Update loan
    loan.return_date = obj_in.return_date or date.today()
    loan.status = "returned"
    loan.condition_at_return = obj_in.condition_at_return
    loan.notes = obj_in.notes or loan.notes
    
    # Calculate late fee
    if loan.return_date > loan.due_date:
        days_late = (loan.return_date - loan.due_date).days
        resource = get_resource(db, loan.resource_id, tenant_id)
        loan.late_fee = days_late * (resource.daily_fee if resource else 0)
        loan.status = "overdue" if loan.late_fee > 0 else "returned"
    
    # Update resource availability
    resource = get_resource(db, loan.resource_id, tenant_id)
    if resource:
        resource.available_copies += 1
        if resource.status == "borrowed":
            resource.status = "available"
    
    db.commit()
    db.refresh(loan)
    return loan


def renew_loan(db: Session, loan_id: UUID, obj_in: LibraryLoanRenew, tenant_id: UUID) -> Optional[LibraryLoan]:
    """Renew a loan."""
    loan = get_loan(db, loan_id, tenant_id)
    if not loan:
        return None
    
    if loan.status != "active":
        raise ValueError("Only active loans can be renewed")
    
    if loan.renewed_count >= loan.max_renewals:
        raise ValueError("Maximum renewals reached")
    
    # Check if there are reservations
    pending_reservations = db.query(LibraryReservation).filter(
        LibraryReservation.resource_id == loan.resource_id,
        LibraryReservation.status == "pending"
    ).count()
    
    if pending_reservations > 0:
        raise ValueError("Cannot renew - there are pending reservations")
    
    # Renew
    loan.due_date = loan.due_date + timedelta(days=obj_in.additional_days)
    loan.renewed_count += 1
    
    db.commit()
    db.refresh(loan)
    return loan


def mark_overdue_loans(db: Session, tenant_id: UUID) -> int:
    """Mark all overdue loans and calculate fees. Returns count of updated loans."""
    overdue_loans = db.query(LibraryLoan).filter(
        LibraryLoan.tenant_id == tenant_id,
        LibraryLoan.status == "active",
        LibraryLoan.due_date < date.today()
    ).all()
    
    count = 0
    for loan in overdue_loans:
        days_late = (date.today() - loan.due_date).days
        resource = get_resource(db, loan.resource_id, tenant_id)
        loan.late_fee = days_late * (resource.daily_fee if resource else 0)
        loan.status = "overdue"
        count += 1
    
    db.commit()
    return count


# ─── Reservations ─────────────────────────────────────────────────────────

def get_reservations(
    db: Session,
    tenant_id: UUID,
    user_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[LibraryReservation]:
    """Get reservations with optional filters."""
    query = db.query(LibraryReservation).filter(
        LibraryReservation.tenant_id == tenant_id
    )
    
    if user_id:
        query = query.filter(LibraryReservation.user_id == user_id)
    
    if status:
        query = query.filter(LibraryReservation.status == status)
    
    return query.order_by(LibraryReservation.reservation_date.desc()).offset(skip).limit(limit).all()


def get_reservation(db: Session, reservation_id: UUID, tenant_id: UUID) -> Optional[LibraryReservation]:
    """Get a specific reservation."""
    return db.query(LibraryReservation).filter(
        LibraryReservation.id == reservation_id,
        LibraryReservation.tenant_id == tenant_id
    ).first()


def create_reservation(db: Session, obj_in: LibraryReservationCreate, tenant_id: UUID) -> LibraryReservation:
    """Create a new reservation."""
    resource = get_resource(db, obj_in.resource_id, tenant_id)
    if not resource:
        raise ValueError("Resource not found")
    
    if resource.available_copies > 0:
        raise ValueError("Resource is available - no need to reserve")
    
    reservation = LibraryReservation(
        resource_id=obj_in.resource_id,
        user_id=obj_in.user_id,
        reservation_date=date.today(),
        expiry_date=date.today() + timedelta(days=obj_in.expiry_days),
        status="pending",
        tenant_id=tenant_id,
        notes=obj_in.notes
    )
    
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, reservation_id: UUID, tenant_id: UUID) -> bool:
    """Cancel a reservation."""
    reservation = get_reservation(db, reservation_id, tenant_id)
    if not reservation:
        return False
    
    reservation.status = "cancelled"
    db.commit()
    return True


def fulfill_reservation(db: Session, reservation_id: UUID, tenant_id: UUID) -> Optional[LibraryLoan]:
    """Fulfill a reservation by creating a loan."""
    reservation = get_reservation(db, reservation_id, tenant_id)
    if not reservation or reservation.status != "pending":
        return None
    
    # Create loan
    loan = create_loan(db, LibraryLoanCreate(
        resource_id=reservation.resource_id,
        user_id=reservation.user_id
    ), tenant_id)
    
    # Update reservation
    reservation.status = "fulfilled"
    
    db.commit()
    return loan


# ─── Inventory ───────────────────────────────────────────────────────────

def get_inventory_items(
    db: Session,
    tenant_id: UUID,
    resource_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[LibraryInventoryItem]:
    """Get inventory items."""
    query = db.query(LibraryInventoryItem).filter(
        LibraryInventoryItem.tenant_id == tenant_id
    )
    
    if resource_id:
        query = query.filter(LibraryInventoryItem.resource_id == resource_id)
    
    if status:
        query = query.filter(LibraryInventoryItem.status == status)
    
    return query.offset(skip).limit(limit).all()


def get_inventory_item(db: Session, item_id: UUID, tenant_id: UUID) -> Optional[LibraryInventoryItem]:
    """Get a specific inventory item."""
    return db.query(LibraryInventoryItem).filter(
        LibraryInventoryItem.id == item_id,
        LibraryInventoryItem.tenant_id == tenant_id
    ).first()


def get_inventory_item_by_barcode(db: Session, barcode: str, tenant_id: UUID) -> Optional[LibraryInventoryItem]:
    """Get an inventory item by barcode."""
    return db.query(LibraryInventoryItem).filter(
        LibraryInventoryItem.barcode == barcode,
        LibraryInventoryItem.tenant_id == tenant_id
    ).first()


def create_inventory_item(db: Session, obj_in: LibraryInventoryCreate, tenant_id: UUID) -> LibraryInventoryItem:
    """Create a new inventory item."""
    item = LibraryInventoryItem(**obj_in.model_dump(), tenant_id=tenant_id)
    db.add(item)
    
    # Update resource total copies
    resource = get_resource(db, obj_in.resource_id, tenant_id)
    if resource:
        resource.total_copies += 1
        resource.available_copies += 1
    
    db.commit()
    db.refresh(item)
    return item


def update_inventory_item(db: Session, item_id: UUID, obj_in: LibraryInventoryUpdate, tenant_id: UUID) -> Optional[LibraryInventoryItem]:
    """Update an inventory item."""
    item = get_inventory_item(db, item_id, tenant_id)
    if not item:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item


# ─── Statistics ───────────────────────────────────────────────────────────

def get_library_statistics(db: Session, tenant_id: UUID) -> dict:
    """Get library statistics for dashboard."""
    # Total resources and copies
    resource_stats = db.query(
        func.count(LibraryResource.id).label('total_resources'),
        func.sum(LibraryResource.total_copies).label('total_copies'),
        func.sum(LibraryResource.available_copies).label('available_copies')
    ).filter(LibraryResource.tenant_id == tenant_id).first()
    
    # Active loans
    active_loans = db.query(func.count(LibraryLoan.id)).filter(
        LibraryLoan.tenant_id == tenant_id,
        LibraryLoan.status.in_(["active", "overdue"])
    ).scalar()
    
    # Overdue loans
    overdue_loans = db.query(func.count(LibraryLoan.id)).filter(
        LibraryLoan.tenant_id == tenant_id,
        LibraryLoan.status == "overdue"
    ).scalar()
    
    # Pending reservations
    pending_reservations = db.query(func.count(LibraryReservation.id)).filter(
        LibraryReservation.tenant_id == tenant_id,
        LibraryReservation.status == "pending"
    ).scalar()
    
    # By category
    by_category = db.query(
        LibraryCategory.name,
        func.count(LibraryResource.id).label('count')
    ).join(LibraryResource).filter(
        LibraryResource.tenant_id == tenant_id
    ).group_by(LibraryCategory.name).all()
    
    # By type
    by_type = db.query(
        LibraryResource.resource_type,
        func.count(LibraryResource.id).label('count')
    ).filter(
        LibraryResource.tenant_id == tenant_id
    ).group_by(LibraryResource.resource_type).all()
    
    # Most borrowed
    most_borrowed = db.query(
        LibraryResource.title,
        LibraryResource.author,
        LibraryResource.times_borrowed
    ).filter(
        LibraryResource.tenant_id == tenant_id
    ).order_by(LibraryResource.times_borrowed.desc()).limit(10).all()
    
    return {
        'total_resources': resource_stats.total_resources or 0,
        'total_copies': resource_stats.total_copies or 0,
        'available_copies': resource_stats.available_copies or 0,
        'borrowed_copies': (resource_stats.total_copies or 0) - (resource_stats.available_copies or 0),
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
        'pending_reservations': pending_reservations,
        'by_category': [{'category': r[0], 'count': r[1]} for r in by_category],
        'by_type': [{'type': r[0], 'count': r[1]} for r in by_type],
        'most_borrowed': [{'title': r[0], 'author': r[1], 'times_borrowed': r[2]} for r in most_borrowed],
    }
