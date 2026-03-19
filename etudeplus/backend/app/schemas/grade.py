"""Grade schemas for request/response validation"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from enum import Enum


class GradeType(str, Enum):
    EXAM = "exam"
    QUIZ = "quiz"
    HOMEWORK = "homework"
    PROJECT = "project"
    ORAL = "oral"
    PARTICIPATION = "participation"
    COMPOSITION = "composition"


# Base schema
class GradeBase(BaseModel):
    score: float = Field(..., ge=0, description="Score obtenu")
    max_score: float = Field(default=20.0, gt=0, description="Score maximum")
    coefficient: float = Field(default=1.0, gt=0, description="Coefficient de la note")
    grade_type: GradeType = Field(default=GradeType.EXAM, description="Type d'évaluation")
    title: Optional[str] = Field(None, max_length=255, description="Titre de l'évaluation")
    comments: Optional[str] = Field(None, max_length=500, description="Commentaires")
    exam_date: Optional[date] = Field(None, description="Date de l'évaluation")


# Schema for creating a grade
class GradeCreate(GradeBase):
    student_id: UUID = Field(..., description="ID de l'étudiant")
    subject_id: Optional[UUID] = Field(None, description="ID de la matière")
    classroom_id: Optional[UUID] = Field(None, description="ID de la classe")
    assessment_id: Optional[UUID] = Field(None, description="ID de l'évaluation liée")
    term_id: Optional[UUID] = Field(None, description="ID du trimestre/semestre")
    academic_year_id: Optional[UUID] = Field(None, description="ID de l'année académique")

    @field_validator('score')
    @classmethod
    def validate_score(cls, v, info):
        max_score = info.data.get('max_score', 20.0)
        if v > max_score * 2:  # Allow scores up to 2x max for bonus
            raise ValueError(f'Score {v} is unreasonably high for max_score {max_score}')
        return v


# Schema for updating a grade
class GradeUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0)
    max_score: Optional[float] = Field(None, gt=0)
    coefficient: Optional[float] = Field(None, gt=0)
    grade_type: Optional[GradeType] = None
    title: Optional[str] = Field(None, max_length=255)
    comments: Optional[str] = Field(None, max_length=500)
    exam_date: Optional[date] = None
    is_published: Optional[bool] = None


# Schema for grade in database (response)
class GradeResponse(GradeBase):
    id: UUID
    tenant_id: UUID
    student_id: UUID
    subject_id: Optional[UUID]
    classroom_id: Optional[UUID]
    assessment_id: Optional[UUID]
    term_id: Optional[UUID]
    academic_year_id: Optional[UUID]
    graded_by: Optional[UUID]
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    percentage: float
    weighted_score: float
    normalized_score: float
    letter_grade: str
    mention: str
    is_passing: bool
    
    # Related data
    subject_name: Optional[str] = None
    student_name: Optional[str] = None

    class Config:
        from_attributes = True


# Schema for list response
class GradeListResponse(BaseModel):
    items: List[GradeResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Schema for grade statistics
class GradeStats(BaseModel):
    average: float
    min_score: float
    max_score: float
    count: int
    passing_count: int
    failing_count: int
    pass_rate: float


# Schema for student report card (bulletin)
class SubjectReport(BaseModel):
    subject_id: UUID
    subject_name: str
    coefficient: float
    grades: List[GradeResponse]
    average: float
    rank: Optional[int]
    mention: str
    appreciation: Optional[str]


class ReportCard(BaseModel):
    student_id: UUID
    student_name: str
    classroom_name: str
    term_name: Optional[str]
    academic_year: str
    subjects: List[SubjectReport]
    general_average: float
    rank: int
    total_students: int
    mention: str
    appreciation: str
    principal_comment: Optional[str]
    generated_at: datetime


# Schema for bulk grade creation
class BulkGradeCreate(BaseModel):
    classroom_id: UUID
    subject_id: UUID
    assessment_id: Optional[UUID] = None
    term_id: Optional[UUID] = None
    grades: List[dict]  # [{student_id, score, comments}, ...]
    grade_type: GradeType = GradeType.EXAM
    title: Optional[str] = None
    exam_date: Optional[date] = None
    max_score: float = 20.0
    coefficient: float = 1.0


class BulkGradeResponse(BaseModel):
    created: int
    updated: int
    failed: int
    errors: List[dict]
