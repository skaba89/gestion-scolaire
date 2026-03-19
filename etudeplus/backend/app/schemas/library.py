"""
Library Schemas - Pydantic models for API validation
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime


# --- Category Schemas ---

class LibraryCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#3498db"
    icon: Optional[str] = None
    parent_id: Optional[UUID] = None


class LibraryCategoryCreate(LibraryCategoryBase):
    pass


class LibraryCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[UUID] = None


class LibraryCategory(LibraryCategoryBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Resource Schemas ---

class LibraryResourceBase(BaseModel):
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    edition: Optional[str] = None
    description: Optional[str] = None
    resource_type: str = "book"
    category_id: Optional[UUID] = None
    total_copies: int = 1
    location: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_borrowable: bool = True
    max_loan_days: int = 14
    daily_fee: float = 0.0
    language: Optional[str] = None
    pages: Optional[int] = None
    tags: Optional[str] = None


class LibraryResourceCreate(LibraryResourceBase):
    pass


class LibraryResourceUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    edition: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    category_id: Optional[UUID] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
    location: Optional[str] = None
    cover_image_url: Optional[str] = None
    status: Optional[str] = None
    is_borrowable: Optional[bool] = None
    max_loan_days: Optional[int] = None
    daily_fee: Optional[float] = None
    language: Optional[str] = None
    pages: Optional[int] = None
    tags: Optional[str] = None


class LibraryResource(LibraryResourceBase):
    id: UUID
    tenant_id: UUID
    available_copies: int
    status: str
    times_borrowed: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Loan Schemas ---

class LibraryLoanBase(BaseModel):
    resource_id: UUID
    user_id: UUID
    loan_date: date
    due_date: date
    condition_at_loan: str = "good"
    notes: Optional[str] = None


class LibraryLoanCreate(BaseModel):
    resource_id: UUID
    user_id: UUID
    loan_days: int = 14
    notes: Optional[str] = None


class LibraryLoanUpdate(BaseModel):
    return_date: Optional[date] = None
    condition_at_return: Optional[str] = None
    notes: Optional[str] = None
    late_fee: Optional[float] = None
    is_fee_paid: Optional[bool] = None


class LibraryLoanRenew(BaseModel):
    additional_days: int = 14


class LibraryLoan(LibraryLoanBase):
    id: UUID
    tenant_id: UUID
    return_date: Optional[date]
    status: str
    late_fee: float
    is_fee_paid: bool
    condition_at_return: Optional[str]
    renewed_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Reservation Schemas ---

class LibraryReservationBase(BaseModel):
    resource_id: UUID
    user_id: UUID
    expiry_days: int = 7


class LibraryReservationCreate(BaseModel):
    resource_id: UUID
    user_id: UUID
    expiry_days: int = 7
    notes: Optional[str] = None


class LibraryReservationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class LibraryReservation(LibraryReservationBase):
    id: UUID
    tenant_id: UUID
    reservation_date: date
    expiry_date: date
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Inventory Schemas ---

class LibraryInventoryBase(BaseModel):
    resource_id: UUID
    barcode: str
    serial_number: Optional[str] = None
    location: Optional[str] = None
    acquisition_date: Optional[date] = None
    acquisition_price: Optional[float] = None
    supplier: Optional[str] = None
    notes: Optional[str] = None


class LibraryInventoryCreate(LibraryInventoryBase):
    pass


class LibraryInventoryUpdate(BaseModel):
    status: Optional[str] = None
    condition: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class LibraryInventoryItem(LibraryInventoryBase):
    id: UUID
    tenant_id: UUID
    status: str
    condition: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Statistics Schema ---

class LibraryStatistics(BaseModel):
    total_resources: int
    total_copies: int
    available_copies: int
    borrowed_copies: int
    active_loans: int
    overdue_loans: int
    pending_reservations: int
    by_category: List[dict]
    by_type: List[dict]
    most_borrowed: List[dict]
