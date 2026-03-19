"""Grade endpoints with complete business logic"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
import math

from app.core.database import get_db
from app.core.security import get_current_user, require_permission
from app.crud import grade as crud_grade
from app.schemas.grade import (
    GradeCreate, GradeUpdate, GradeResponse, GradeListResponse,
    GradeStats, BulkGradeCreate, BulkGradeResponse, ReportCard
)
from app.models.grade import GradeType

router = APIRouter()


@router.get("/", response_model=GradeListResponse)
def list_grades(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    student_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
    classroom_id: Optional[UUID] = None,
    term_id: Optional[UUID] = None,
    academic_year_id: Optional[UUID] = None,
    grade_type: Optional[GradeType] = None,
    is_published: Optional[bool] = None,
):
    """
    List grades with pagination and filters
    
    - **student_id**: Filter by student
    - **subject_id**: Filter by subject
    - **classroom_id**: Filter by classroom
    - **term_id**: Filter by term/semester
    - **academic_year_id**: Filter by academic year
    - **grade_type**: Filter by grade type (exam, quiz, homework, etc.)
    - **is_published**: Filter by publication status
    """
    tenant_id = current_user.get("tenant_id")
    skip = (page - 1) * page_size
    
    grades, total = crud_grade.get_grades(
        db=db,
        tenant_id=tenant_id,
        skip=skip,
        limit=page_size,
        student_id=student_id,
        subject_id=subject_id,
        classroom_id=classroom_id,
        term_id=term_id,
        academic_year_id=academic_year_id,
        grade_type=grade_type,
        is_published=is_published,
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    return GradeListResponse(
        items=grades,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/stats/{student_id}/", response_model=GradeStats)
def get_student_stats(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    term_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
    academic_year_id: Optional[UUID] = None,
):
    """
    Get student's grade statistics including average, min, max, and pass rate
    """
    tenant_id = current_user.get("tenant_id")
    
    return crud_grade.get_student_average(
        db=db,
        student_id=student_id,
        tenant_id=tenant_id,
        term_id=term_id,
        subject_id=subject_id,
        academic_year_id=academic_year_id,
    )


@router.get("/report-card/{student_id}/", response_model=ReportCard)
def get_report_card(
    student_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    term_id: Optional[UUID] = None,
    academic_year_id: Optional[UUID] = None,
):
    """
    Generate a complete report card (bulletin) for a student
    
    Returns all grades, averages per subject, general average, rank, and mention
    """
    tenant_id = current_user.get("tenant_id")
    
    report_card = crud_grade.get_report_card(
        db=db,
        student_id=student_id,
        tenant_id=tenant_id,
        term_id=term_id,
        academic_year_id=academic_year_id,
    )
    
    if not report_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No grades found for this student in the specified period"
        )
    
    return report_card


@router.get("/classroom/{classroom_id}/averages/")
def get_classroom_averages(
    classroom_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    term_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
):
    """
    Get averages for all students in a classroom with rankings
    """
    tenant_id = current_user.get("tenant_id")
    
    return crud_grade.get_classroom_averages(
        db=db,
        classroom_id=classroom_id,
        tenant_id=tenant_id,
        term_id=term_id,
        subject_id=subject_id,
    )


@router.get("/distribution/")
def get_grade_distribution(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    classroom_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
):
    """
    Get distribution of grades by letter grade (A, B, C, D, E, F)
    """
    tenant_id = current_user.get("tenant_id")
    
    return crud_grade.get_grade_distribution(
        db=db,
        tenant_id=tenant_id,
        classroom_id=classroom_id,
        subject_id=subject_id,
    )


@router.get("/{grade_id}/", response_model=GradeResponse)
def get_grade(
    grade_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get a specific grade by ID
    """
    tenant_id = current_user.get("tenant_id")
    grade = crud_grade.get_grade(db, grade_id, tenant_id)
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    return grade


@router.post("/", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def create_grade(
    grade: GradeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("grades:write")),
):
    """
    Create a new grade
    
    Permissions: grades:write
    """
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("user_id")
    
    return crud_grade.create_grade(db, grade, tenant_id, graded_by=user_id)


@router.post("/bulk/", response_model=BulkGradeResponse)
def bulk_create_grades(
    bulk_data: BulkGradeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("grades:write")),
):
    """
    Create multiple grades at once (bulk entry)
    
    Use this endpoint for entering grades for an entire class at once.
    
    Permissions: grades:write
    """
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("user_id")
    
    result = crud_grade.bulk_create_grades(
        db=db,
        classroom_id=bulk_data.classroom_id,
        subject_id=bulk_data.subject_id,
        grades_data=bulk_data.grades,
        tenant_id=tenant_id,
        term_id=bulk_data.term_id,
        assessment_id=bulk_data.assessment_id,
        grade_type=bulk_data.grade_type,
        title=bulk_data.title,
        exam_date=bulk_data.exam_date,
        max_score=bulk_data.max_score,
        coefficient=bulk_data.coefficient,
        graded_by=user_id
    )
    
    return BulkGradeResponse(**result)


@router.post("/publish/")
def publish_grades(
    grade_ids: List[UUID],
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("grades:write")),
):
    """
    Publish multiple grades (make visible to students/parents)
    
    Permissions: grades:write
    """
    tenant_id = current_user.get("tenant_id")
    
    count = crud_grade.publish_grades(db, grade_ids, tenant_id)
    
    return {
        "message": f"{count} grades published successfully",
        "published_count": count
    }


@router.put("/{grade_id}/", response_model=GradeResponse)
def update_grade(
    grade_id: UUID,
    grade_update: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("grades:write")),
):
    """
    Update a grade
    
    Permissions: grades:write
    """
    tenant_id = current_user.get("tenant_id")
    
    updated_grade = crud_grade.update_grade(
        db, grade_id, grade_update, tenant_id
    )
    
    if not updated_grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    return updated_grade


@router.delete("/{grade_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_grade(
    grade_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_permission("grades:write")),
):
    """
    Delete a grade
    
    Permissions: grades:write
    """
    tenant_id = current_user.get("tenant_id")
    
    success = crud_grade.delete_grade(db, grade_id, tenant_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
