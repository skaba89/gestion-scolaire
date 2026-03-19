"""Grade model with complete business rules"""
from sqlalchemy import Column, String, Float, ForeignKey, Date, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import date
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin, TenantMixin


class GradeType(str, enum.Enum):
    """Type of grade/evaluation"""
    EXAM = "exam"
    QUIZ = "quiz"
    HOMEWORK = "homework"
    PROJECT = "project"
    ORAL = "oral"
    PARTICIPATION = "participation"
    COMPOSITION = "composition"  # Composition (exam trimestriel/semestriel)


class Grade(Base, UUIDMixin, TimestampMixin, TenantMixin):
    __tablename__ = "grades"
    
    # Core fields
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id", ondelete="CASCADE"), nullable=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True, index=True)
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Academic context
    term_id = Column(UUID(as_uuid=True), ForeignKey("terms.id", ondelete="SET NULL"), nullable=True, index=True)
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Grade details
    score = Column(Float, nullable=False)
    max_score = Column(Float, default=20.0, nullable=False)
    coefficient = Column(Float, default=1.0)
    grade_type = Column(SQLEnum(GradeType), default=GradeType.EXAM)
    
    # Additional info
    title = Column(String(255))  # Title of the exam/assignment
    comments = Column(Text)
    exam_date = Column(Date, default=date.today)
    
    # Tracking
    graded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_published = Column(Integer, default=0)  # 0=draft, 1=published
    
    # Relationships
    student = relationship("Student", back_populates="grades")
    assessment = relationship("Assessment", back_populates="grades")
    subject = relationship("Subject")
    classroom = relationship("Classroom")
    term = relationship("Term")
    academic_year = relationship("AcademicYear")
    grader = relationship("User", foreign_keys=[graded_by])
    
    @property
    def percentage(self) -> float:
        """Calculate percentage score"""
        return (self.score / self.max_score) * 100 if self.max_score > 0 else 0
    
    @property
    def weighted_score(self) -> float:
        """Calculate weighted score for average calculation"""
        return self.score * self.coefficient
    
    @property
    def normalized_score(self) -> float:
        """Normalize score to base 20"""
        if self.max_score == 20:
            return self.score
        return (self.score / self.max_score) * 20
    
    @property
    def letter_grade(self) -> str:
        """Get letter grade based on French system"""
        pct = self.percentage
        if pct >= 80:
            return "A"
        elif pct >= 70:
            return "B"
        elif pct >= 60:
            return "C"
        elif pct >= 50:
            return "D"
        elif pct >= 40:
            return "E"
        else:
            return "F"
    
    @property
    def mention(self) -> str:
        """Get mention based on French system (out of 20)"""
        normalized = self.normalized_score
        if normalized >= 16:
            return "Très Bien"
        elif normalized >= 14:
            return "Bien"
        elif normalized >= 12:
            return "Assez Bien"
        elif normalized >= 10:
            return "Passable"
        else:
            return "Insuffisant"
    
    @property
    def is_passing(self) -> bool:
        """Check if grade is passing (>= 10/20)"""
        return self.normalized_score >= 10


class GradeCalculation:
    """Business rules for grade calculations"""
    
    @staticmethod
    def calculate_weighted_average(grades: list) -> float:
        """Calculate weighted average from list of grades"""
        if not grades:
            return 0.0
        
        total_weight = sum(g.coefficient for g in grades)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(g.normalized_score * g.coefficient for g in grades)
        return round(weighted_sum / total_weight, 2)
    
    @staticmethod
    def calculate_subject_average(grades: list, subject_id) -> float:
        """Calculate average for a specific subject"""
        subject_grades = [g for g in grades if g.subject_id == subject_id]
        return GradeCalculation.calculate_weighted_average(subject_grades)
    
    @staticmethod
    def calculate_term_average(grades: list, term_id) -> float:
        """Calculate average for a term/semester"""
        term_grades = [g for g in grades if g.term_id == term_id]
        return GradeCalculation.calculate_weighted_average(term_grades)
    
    @staticmethod
    def get_annual_average(grades: list) -> float:
        """Calculate annual average (moyenne générale)"""
        return GradeCalculation.calculate_weighted_average(grades)
    
    @staticmethod
    def determine_rank(student_average: float, all_averages: list) -> int:
        """Determine student rank in class"""
        sorted_averages = sorted(all_averages, reverse=True)
        for i, avg in enumerate(sorted_averages, 1):
            if avg == student_average:
                return i
        return len(sorted_averages)
    
    @staticmethod
    def calculate_appreciation(average: float) -> str:
        """Get appreciation text based on average"""
        if average >= 16:
            return "Excellent travail. Continuez ainsi!"
        elif average >= 14:
            return "Très bon travail. Des efforts constants."
        elif average >= 12:
            return "Bon travail dans l'ensemble. Peut mieux faire."
        elif average >= 10:
            return "Résultats satisfaisants. Des progrès sont possibles."
        elif average >= 8:
            return "Travail insuffisant. Un effort particulier est nécessaire."
        else:
            return "Résultats très insuffisants. Un suivi particulier est recommandé."
