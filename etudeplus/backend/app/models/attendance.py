"""Attendance model with complete business rules for absence tracking"""
from sqlalchemy import Column, String, Date, ForeignKey, Text, Integer, Boolean, Time, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date, time
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin, TenantMixin


class AttendanceStatus(str, enum.Enum):
    """Attendance status types"""
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"
    HALF_DAY = "half_day"
    EARLY_DEPARTURE = "early_departure"


class AttendanceSession(str, enum.Enum):
    """Session period for attendance"""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    FULL_DAY = "full_day"


class Attendance(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "attendance"
    
    # Core fields
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    
    # Date and time
    date = Column(Date, nullable=False, index=True)
    session = Column(SQLEnum(AttendanceSession), default=AttendanceSession.FULL_DAY)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    
    # Status
    status = Column(SQLEnum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
    reason = Column(Text)
    excuse_type = Column(String(50))  # medical, family, administrative, etc.
    excuse_document_url = Column(Text)
    is_justified = Column(Boolean, default=False)
    
    # Tracking
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text)
    
    # Relationships
    student = relationship("Student", back_populates="attendance_records")
    classroom = relationship("Classroom")
    subject = relationship("Subject")
    recorder = relationship("User", foreign_keys=[recorded_by])
    
    @property
    def is_absent(self) -> bool:
        """Check if student is absent"""
        return self.status in [AttendanceStatus.ABSENT, AttendanceStatus.HALF_DAY]
    
    @property
    def requires_justification(self) -> bool:
        """Check if absence requires justification"""
        return self.status in [AttendanceStatus.ABSENT, AttendanceStatus.LATE] and not self.is_justified


class AttendanceThreshold(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Configurable thresholds for absence alerts per tenant"""
    __tablename__ = "attendance_thresholds"
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Warning levels
    warning_threshold = Column(Integer, default=5)  # Absences before warning
    alert_threshold = Column(Integer, default=10)   # Absences before alert
    critical_threshold = Column(Integer, default=15) # Absences before critical action
    
    # Notification settings
    notify_parent = Column(Boolean, default=True)
    notify_admin = Column(Boolean, default=True)
    notify_teacher = Column(Boolean, default=False)
    
    # Actions
    auto_escalate = Column(Boolean, default=False)
    escalation_role = Column(String(50))  # Role to escalate to
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    tenant = relationship("Tenant")


class AttendanceAlert(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Alerts generated when thresholds are crossed"""
    __tablename__ = "attendance_alerts"
    
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    threshold_id = Column(UUID(as_uuid=True), ForeignKey("attendance_thresholds.id", ondelete="SET NULL"))
    
    alert_type = Column(String(50))  # warning, alert, critical
    absences_count = Column(Integer, nullable=False)
    message = Column(Text)
    
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(Date)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolution_notes = Column(Text)
    
    # Notifications sent
    parent_notified = Column(Boolean, default=False)
    admin_notified = Column(Boolean, default=False)
    
    created_at = Column(Date, default=date.today)
    
    # Relationships
    student = relationship("Student")
    threshold = relationship("AttendanceThreshold")
    resolver = relationship("User", foreign_keys=[resolved_by])


class AttendanceCalculation:
    """Business rules for attendance calculations"""
    
    @staticmethod
    def get_absence_count(attendance_records: list) -> int:
        """Count total absences"""
        return sum(1 for a in attendance_records if a.is_absent)
    
    @staticmethod
    def get_late_count(attendance_records: list) -> int:
        """Count total late arrivals"""
        return sum(1 for a in attendance_records if a.status == AttendanceStatus.LATE)
    
    @staticmethod
    def get_justified_count(attendance_records: list) -> int:
        """Count justified absences"""
        return sum(1 for a in attendance_records if a.is_absent and a.is_justified)
    
    @staticmethod
    def get_unjustified_count(attendance_records: list) -> int:
        """Count unjustified absences"""
        return sum(1 for a in attendance_records if a.is_absent and not a.is_justified)
    
    @staticmethod
    def calculate_attendance_rate(attendance_records: list) -> float:
        """Calculate attendance rate percentage"""
        if not attendance_records:
            return 100.0
        
        present_count = sum(1 for a in attendance_records if a.status == AttendanceStatus.PRESENT)
        return round((present_count / len(attendance_records)) * 100, 1)
    
    @staticmethod
    def get_alert_level(absences_count: int, thresholds: AttendanceThreshold) -> str:
        """Determine alert level based on absences"""
        if absences_count >= thresholds.critical_threshold:
            return "critical"
        elif absences_count >= thresholds.alert_threshold:
            return "alert"
        elif absences_count >= thresholds.warning_threshold:
            return "warning"
        return "none"
    
    @staticmethod
    def should_generate_alert(student_absences: int, thresholds: AttendanceThreshold) -> bool:
        """Check if an alert should be generated"""
        return student_absences in [thresholds.warning_threshold, thresholds.alert_threshold, thresholds.critical_threshold]
    
    @staticmethod
    def get_attendance_summary(attendance_records: list) -> dict:
        """Get comprehensive attendance summary"""
        return {
            "total_days": len(attendance_records),
            "present": sum(1 for a in attendance_records if a.status == AttendanceStatus.PRESENT),
            "absent": sum(1 for a in attendance_records if a.status == AttendanceStatus.ABSENT),
            "late": sum(1 for a in attendance_records if a.status == AttendanceStatus.LATE),
            "excused": sum(1 for a in attendance_records if a.status == AttendanceStatus.EXCUSED),
            "half_day": sum(1 for a in attendance_records if a.status == AttendanceStatus.HALF_DAY),
            "early_departure": sum(1 for a in attendance_records if a.status == AttendanceStatus.EARLY_DEPARTURE),
            "justified": sum(1 for a in attendance_records if a.is_justified),
            "unjustified": sum(1 for a in attendance_records if a.is_absent and not a.is_justified),
            "attendance_rate": AttendanceCalculation.calculate_attendance_rate(attendance_records)
        }
