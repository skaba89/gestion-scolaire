"""
Library API Endpoints - Complete Implementation
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.library import (
    LibraryCategory, LibraryCategoryCreate, LibraryCategoryUpdate,
    LibraryResource, LibraryResourceCreate, LibraryResourceUpdate,
    LibraryLoan, LibraryLoanCreate, LibraryLoanUpdate, LibraryLoanRenew,
    LibraryReservation, LibraryReservationCreate, LibraryReservationUpdate,
    LibraryInventoryItem, LibraryInventoryCreate, LibraryInventoryUpdate,
    LibraryStatistics
)
from app.crud import library as crud_library

router = APIRouter()


# ─── Categories ───────────────────────────────────────────────────────────────

@router.get("/categories/", response_model=List[LibraryCategory])
def list_categories(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List all library categories."""
    return crud_library.get_categories(db, tenant_id=current_user.get("tenant_id"))


@router.post("/categories/", response_model=LibraryCategory)
def create_category(
    obj_in: LibraryCategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new category."""
    return crud_library.create_category(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))


@router.get("/categories/{category_id}/", response_model=LibraryCategory)
def get_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific category."""
    category = crud_library.get_category(db, category_id=category_id, tenant_id=current_user.get("tenant_id"))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}/", response_model=LibraryCategory)
def update_category(
    category_id: UUID,
    obj_in: LibraryCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a category."""
    category = crud_library.update_category(db, category_id=category_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/categories/{category_id}/")
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a category."""
    success = crud_library.delete_category(db, category_id=category_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"status": "success"}


# ─── Resources ───────────────────────────────────────────────────────────────

@router.get("/resources/", response_model=List[LibraryResource])
def list_resources(
    category_id: Optional[UUID] = None,
    resource_type: Optional[str] = None,
    search: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List library resources with optional filters."""
    return crud_library.get_resources(
        db,
        tenant_id=current_user.get("tenant_id"),
        category_id=category_id,
        resource_type=resource_type,
        search=search,
        status=status,
        skip=skip,
        limit=limit
    )


@router.post("/resources/", response_model=LibraryResource)
def create_resource(
    obj_in: LibraryResourceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new library resource."""
    return crud_library.create_resource(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))


@router.get("/resources/{resource_id}/", response_model=LibraryResource)
def get_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific resource."""
    resource = crud_library.get_resource(db, resource_id=resource_id, tenant_id=current_user.get("tenant_id"))
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.put("/resources/{resource_id}/", response_model=LibraryResource)
def update_resource(
    resource_id: UUID,
    obj_in: LibraryResourceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a resource."""
    resource = crud_library.update_resource(db, resource_id=resource_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.delete("/resources/{resource_id}/")
def delete_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a resource."""
    success = crud_library.delete_resource(db, resource_id=resource_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"status": "success"}


# ─── Loans ───────────────────────────────────────────────────────────────────

@router.get("/loans/", response_model=List[LibraryLoan])
def list_loans(
    user_id: Optional[UUID] = None,
    status: Optional[str] = None,
    overdue_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List loans with optional filters."""
    return crud_library.get_loans(
        db,
        tenant_id=current_user.get("tenant_id"),
        user_id=user_id,
        status=status,
        overdue_only=overdue_only,
        skip=skip,
        limit=limit
    )


@router.post("/loans/", response_model=LibraryLoan)
def create_loan(
    obj_in: LibraryLoanCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Borrow a book (create a loan)."""
    try:
        return crud_library.create_loan(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/loans/{loan_id}/", response_model=LibraryLoan)
def get_loan(
    loan_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific loan."""
    loan = crud_library.get_loan(db, loan_id=loan_id, tenant_id=current_user.get("tenant_id"))
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.put("/loans/{loan_id}/return/", response_model=LibraryLoan)
def return_loan(
    loan_id: UUID,
    obj_in: LibraryLoanUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Return a borrowed book."""
    try:
        loan = crud_library.return_loan(db, loan_id=loan_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/loans/{loan_id}/renew/", response_model=LibraryLoan)
def renew_loan(
    loan_id: UUID,
    obj_in: LibraryLoanRenew,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Renew a loan."""
    try:
        loan = crud_library.renew_loan(db, loan_id=loan_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
        if not loan:
            raise HTTPException(status_code=404, detail="Loan not found")
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/loans/mark-overdue/")
def mark_overdue_loans(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark all overdue loans (admin task)."""
    count = crud_library.mark_overdue_loans(db, tenant_id=current_user.get("tenant_id"))
    return {"status": "success", "overdue_loans_updated": count}


# ─── Reservations ─────────────────────────────────────────────────────────────

@router.get("/reservations/", response_model=List[LibraryReservation])
def list_reservations(
    user_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List reservations."""
    return crud_library.get_reservations(
        db,
        tenant_id=current_user.get("tenant_id"),
        user_id=user_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.post("/reservations/", response_model=LibraryReservation)
def create_reservation(
    obj_in: LibraryReservationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Reserve a book."""
    try:
        return crud_library.create_reservation(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reservations/{reservation_id}/", response_model=LibraryReservation)
def get_reservation(
    reservation_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific reservation."""
    reservation = crud_library.get_reservation(db, reservation_id=reservation_id, tenant_id=current_user.get("tenant_id"))
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


@router.delete("/reservations/{reservation_id}/")
def cancel_reservation(
    reservation_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Cancel a reservation."""
    success = crud_library.cancel_reservation(db, reservation_id=reservation_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return {"status": "cancelled"}


@router.post("/reservations/{reservation_id}/fulfill/", response_model=LibraryLoan)
def fulfill_reservation(
    reservation_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Fulfill a reservation by creating a loan."""
    try:
        loan = crud_library.fulfill_reservation(db, reservation_id=reservation_id, tenant_id=current_user.get("tenant_id"))
        if not loan:
            raise HTTPException(status_code=404, detail="Reservation not found or not pending")
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Inventory ───────────────────────────────────────────────────────────────

@router.get("/inventory/", response_model=List[LibraryInventoryItem])
def list_inventory(
    resource_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List inventory items."""
    return crud_library.get_inventory_items(
        db,
        tenant_id=current_user.get("tenant_id"),
        resource_id=resource_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.post("/inventory/", response_model=LibraryInventoryItem)
def create_inventory_item(
    obj_in: LibraryInventoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Add an inventory item."""
    return crud_library.create_inventory_item(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))


@router.get("/inventory/{item_id}/", response_model=LibraryInventoryItem)
def get_inventory_item(
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific inventory item."""
    item = crud_library.get_inventory_item(db, item_id=item_id, tenant_id=current_user.get("tenant_id"))
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.get("/inventory/barcode/{barcode}/", response_model=LibraryInventoryItem)
def get_inventory_by_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get inventory item by barcode."""
    item = crud_library.get_inventory_item_by_barcode(db, barcode=barcode, tenant_id=current_user.get("tenant_id"))
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.put("/inventory/{item_id}/", response_model=LibraryInventoryItem)
def update_inventory_item(
    item_id: UUID,
    obj_in: LibraryInventoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update an inventory item."""
    item = crud_library.update_inventory_item(db, item_id=item_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


# ─── Statistics ───────────────────────────────────────────────────────────────

@router.get("/statistics/", response_model=LibraryStatistics)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get library statistics for dashboard."""
    return crud_library.get_library_statistics(db, tenant_id=current_user.get("tenant_id"))
