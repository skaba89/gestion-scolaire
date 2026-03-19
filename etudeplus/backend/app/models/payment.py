"""Invoice and Payment models with complete business rules for school finance"""
from sqlalchemy import Column, String, Date, ForeignKey, Text, Integer, Boolean, Numeric, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date, datetime, timedelta
from decimal import Decimal
import enum
import random
import string

from app.models.base import Base, UUIDMixin, TimestampMixin, TenantMixin


class InvoiceStatus(str, enum.Enum):
    """Invoice status"""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, enum.Enum):
    """Payment status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentMethod(str, enum.Enum):
    """Payment methods"""
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CARD = "card"
    CHECK = "check"
    OTHER = "other"


class FeeType(str, enum.Enum):
    """Types of school fees"""
    TUITION = "tuition"
    REGISTRATION = "registration"
    EXAM = "exam"
    LIBRARY = "library"
    LAB = "lab"
    SPORTS = "sports"
    TRANSPORT = "transport"
    MEAL = "meal"
    BOARDING = "boarding"
    UNIFORM = "uniform"
    BOOKS = "books"
    OTHER = "other"


class FeeStructure(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Fee structure for different levels/programs"""
    __tablename__ = "fee_structures"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    level_id = Column(UUID(as_uuid=True), ForeignKey("levels.id", ondelete="SET NULL"))
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id", ondelete="SET NULL"))
    
    # Fee details
    fee_type = Column(SQLEnum(FeeType), default=FeeType.TUITION)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="GNF")
    
    # Payment schedule
    due_date = Column(Date)
    installments_allowed = Column(Boolean, default=True)
    max_installments = Column(Integer, default=3)
    
    # Discounts
    early_payment_discount = Column(Numeric(5, 2), default=0)  # Percentage
    early_payment_days = Column(Integer, default=30)
    sibling_discount = Column(Numeric(5, 2), default=0)  # Percentage
    
    is_active = Column(Boolean, default=True)
    is_mandatory = Column(Boolean, default=True)
    
    # Relationships
    level = relationship("Level")
    academic_year = relationship("AcademicYear")


class Invoice(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Student invoice"""
    __tablename__ = "invoices"
    
    # Invoice identification
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Relations
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id", ondelete="SET NULL"))
    
    # Amounts
    subtotal = Column(Numeric(12, 2), nullable=False, default=0)
    discount_amount = Column(Numeric(12, 2), default=0)
    tax_amount = Column(Numeric(12, 2), default=0)
    total_amount = Column(Numeric(12, 2), nullable=False)
    amount_paid = Column(Numeric(12, 2), default=0)
    balance_due = Column(Numeric(12, 2), default=0)
    currency = Column(String(10), default="GNF")
    
    # Status and dates
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    issue_date = Column(Date, default=date.today)
    due_date = Column(Date, nullable=False)
    sent_at = Column(Date)
    viewed_at = Column(Date)
    paid_at = Column(Date)
    
    # Line items
    items = Column(JSON, default=list)  # [{description, quantity, unit_price, total}]
    
    # Notes
    notes = Column(Text)
    terms_conditions = Column(Text)
    internal_notes = Column(Text)
    
    # Discounts applied
    discount_type = Column(String(50))  # early_payment, sibling, scholarship, custom
    discount_percentage = Column(Numeric(5, 2), default=0)
    
    # Payment tracking
    reminder_count = Column(Integer, default=0)
    last_reminder_at = Column(Date)
    
    # Relationships
    student = relationship("Student", back_populates="invoices")
    academic_year = relationship("AcademicYear")
    payments = relationship("Payment", back_populates="invoice")
    
    @property
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        return self.due_date < date.today() and self.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]
    
    @property
    def days_overdue(self) -> int:
        """Get number of days overdue"""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days
    
    @property
    def payment_progress(self) -> float:
        """Get payment progress percentage"""
        if self.total_amount == 0:
            return 100.0
        return float((self.amount_paid / self.total_amount) * 100)


class Payment(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Payment record"""
    __tablename__ = "payments"
    
    # Payment identification
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    reference_number = Column(String(100))
    
    # Relations
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id", ondelete="SET NULL"), index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Amount
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), default="GNF")
    
    # Payment details
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    payment_date = Column(Date, default=date.today)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Gateway/Payment processor info
    gateway = Column(String(50))  # stripe, orange_money, etc.
    gateway_transaction_id = Column(String(255))
    gateway_response = Column(JSON)
    
    # Additional info
    bank_name = Column(String(100))
    check_number = Column(String(50))
    account_number = Column(String(50))
    
    # Processing
    processed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    processed_at = Column(Date)
    notes = Column(Text)
    
    # Refund info
    refunded_amount = Column(Numeric(12, 2), default=0)
    refund_reason = Column(Text)
    refunded_at = Column(Date)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    student = relationship("Student")
    processor = relationship("User", foreign_keys=[processed_by])
    
    @property
    def is_successful(self) -> bool:
        return self.status == PaymentStatus.COMPLETED


class FinanceCalculation:
    """Business rules for financial calculations"""
    
    @staticmethod
    def generate_invoice_number() -> str:
        """Generate unique invoice number"""
        prefix = "INV"
        year = date.today().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{year}-{random_part}"
    
    @staticmethod
    def generate_payment_number() -> str:
        """Generate unique payment number"""
        prefix = "PAY"
        year = date.today().year
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}-{year}-{random_part}"
    
    @staticmethod
    def calculate_early_payment_discount(invoice: Invoice, payment_date: date = None) -> Decimal:
        """Calculate early payment discount if applicable"""
        if not payment_date:
            payment_date = date.today()
        
        # Check if fee structure has early payment discount
        days_before_due = (invoice.due_date - payment_date).days
        
        # Default 5% discount if paid 30+ days before due date
        if days_before_due >= 30:
            return invoice.subtotal * Decimal('0.05')
        return Decimal('0')
    
    @staticmethod
    def calculate_sibling_discount(total_students: int) -> Decimal:
        """Calculate sibling discount percentage"""
        if total_students >= 3:
            return Decimal('0.15')  # 15% for 3+ siblings
        elif total_students == 2:
            return Decimal('0.10')  # 10% for 2 siblings
        return Decimal('0')
    
    @staticmethod
    def apply_payment_to_invoice(invoice: Invoice, payment_amount: Decimal) -> dict:
        """Apply payment to invoice and update status"""
        new_amount_paid = invoice.amount_paid + payment_amount
        new_balance = invoice.total_amount - new_amount_paid
        
        result = {
            "amount_paid": new_amount_paid,
            "balance_due": max(new_balance, Decimal('0')),
            "status": invoice.status
        }
        
        if new_balance <= 0:
            result["status"] = InvoiceStatus.PAID
            result["paid_at"] = date.today()
        elif new_amount_paid > 0:
            result["status"] = InvoiceStatus.PARTIAL
        
        return result
    
    @staticmethod
    def calculate_total_revenue(invoices: list) -> dict:
        """Calculate total revenue from invoices"""
        total_billed = sum(i.total_amount for i in invoices)
        total_collected = sum(i.amount_paid for i in invoices)
        total_pending = total_billed - total_collected
        
        return {
            "total_billed": float(total_billed),
            "total_collected": float(total_collected),
            "total_pending": float(total_pending),
            "collection_rate": round((total_collected / total_billed * 100), 1) if total_billed > 0 else 0
        }
    
    @staticmethod
    def get_overdue_invoices(invoices: list) -> list:
        """Filter overdue invoices"""
        return [i for i in invoices if i.is_overdue]
    
    @staticmethod
    def calculate_collection_forecast(invoices: list, days_ahead: int = 30) -> dict:
        """Forecast expected collections"""
        today = date.today()
        upcoming_due = [i for i in invoices 
                       if today <= i.due_date <= today + timedelta(days=days_ahead)
                       and i.status not in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED]]
        
        expected = sum(i.balance_due for i in upcoming_due)
        
        return {
            "upcoming_invoices": len(upcoming_due),
            "expected_amount": float(expected),
            "period_days": days_ahead
        }
