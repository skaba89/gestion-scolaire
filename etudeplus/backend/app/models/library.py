"""
Library Models - Books, Loans, Categories, and Inventory
"""
from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, Boolean, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import date
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin, TenantMixin


class BookStatus(str, enum.Enum):
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    LOST = "lost"
    MAINTENANCE = "maintenance"


class LoanStatus(str, enum.Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"


class LibraryCategory(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Categories for library resources."""
    __tablename__ = "library_categories"
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    color = Column(String(7), default="#3498db")  # Hex color code
    icon = Column(String(50))  # Icon name
    parent_id = Column(UUID(as_uuid=True), ForeignKey("library_categories.id"), nullable=True)
    
    # Relationships
    children = relationship("LibraryCategory", backref="parent", remote_side="LibraryCategory.id")
    resources = relationship("LibraryResource", back_populates="category")


class LibraryResource(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Books and other library resources."""
    __tablename__ = "library_resources"
    
    title = Column(String(255), nullable=False)
    author = Column(String(255))
    isbn = Column(String(20), unique=True)
    publisher = Column(String(100))
    publication_year = Column(Integer)
    edition = Column(String(50))
    description = Column(Text)
    resource_type = Column(String(50), default="book")  # book, magazine, dvd, ebook, etc.
    category_id = Column(UUID(as_uuid=True), ForeignKey("library_categories.id"))
    
    # Physical properties
    total_copies = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    location = Column(String(100))  # Shelf/Room location
    cover_image_url = Column(String(500))
    
    # Status
    status = Column(String(20), default="available")
    is_borrowable = Column(Boolean, default=True)
    max_loan_days = Column(Integer, default=14)
    daily_fee = Column(Float, default=0.0)  # Late fee per day
    
    # Metadata
    language = Column(String(50))
    pages = Column(Integer)
    tags = Column(String(500))  # JSON array of tags
    
    # Tracking
    times_borrowed = Column(Integer, default=0)
    
    # Relationships
    category = relationship("LibraryCategory", back_populates="resources")
    loans = relationship("LibraryLoan", back_populates="resource", cascade="all, delete-orphan")
    reservations = relationship("LibraryReservation", back_populates="resource", cascade="all, delete-orphan")


class LibraryLoan(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Book loans/borrows."""
    __tablename__ = "library_loans"
    
    resource_id = Column(UUID(as_uuid=True), ForeignKey("library_resources.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Dates
    loan_date = Column(Date, nullable=False, default=date.today)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    
    # Status
    status = Column(String(20), default="active")
    
    # Fees
    late_fee = Column(Float, default=0.0)
    is_fee_paid = Column(Boolean, default=False)
    
    # Notes
    condition_at_loan = Column(String(50), default="good")  # good, fair, poor
    condition_at_return = Column(String(50))
    notes = Column(Text)
    
    # Tracking
    renewed_count = Column(Integer, default=0)
    max_renewals = Column(Integer, default=2)
    
    # Relationships
    resource = relationship("LibraryResource", back_populates="loans")
    user = relationship("User", backref="library_loans")


class LibraryReservation(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Book reservations."""
    __tablename__ = "library_reservations"
    
    resource_id = Column(UUID(as_uuid=True), ForeignKey("library_resources.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    reservation_date = Column(Date, nullable=False, default=date.today)
    expiry_date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")  # pending, fulfilled, cancelled, expired
    
    notes = Column(Text)
    
    # Relationships
    resource = relationship("LibraryResource", back_populates="reservations")
    user = relationship("User", backref="library_reservations")


class LibraryInventoryItem(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Individual copies of resources with barcodes."""
    __tablename__ = "library_inventory"
    
    resource_id = Column(UUID(as_uuid=True), ForeignKey("library_resources.id", ondelete="CASCADE"), nullable=False)
    barcode = Column(String(50), unique=True, nullable=False)
    serial_number = Column(String(50))
    
    status = Column(String(20), default="available")
    condition = Column(String(20), default="good")
    location = Column(String(100))
    
    acquisition_date = Column(Date)
    acquisition_price = Column(Float)
    supplier = Column(String(100))
    
    notes = Column(Text)
    
    # Relationships
    resource = relationship("LibraryResource", backref="inventory_items")
