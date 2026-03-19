"""CRUD operations for Grade model with complete business logic"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from uuid import UUID
from datetime import date
import logging

from app.models.grade import Grade, GradeType, GradeCalculation
from app.schemas.grade import GradeCreate, GradeUpdate, GradeStats, SubjectReport, ReportCard

logger = logging.getLogger(__name__)


def get_grade(db: Session, grade_id: UUID, tenant_id: UUID) -> Optional[Grade]:
    """Get a grade by ID"""
    return db.query(Grade).filter(
        Grade.id == grade_id,
        Grade.tenant_id == tenant_id
    ).first()


def get_grades(
    db: Session,
    tenant_id: UUID,
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
    classroom_id: Optional[UUID] = None,
    term_id: Optional[UUID] = None,
    academic_year_id: Optional[UUID] = None,
    grade_type: Optional[GradeType] = None,
    is_published: Optional[bool] = None,
) -> tuple[List[Grade], int]:
    """Get grades with pagination and filters"""
    query = db.query(Grade).filter(Grade.tenant_id == tenant_id)
    
    if student_id:
        query = query.filter(Grade.student_id == student_id)
    
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    
    if classroom_id:
        query = query.filter(Grade.classroom_id == classroom_id)
    
    if term_id:
        query = query.filter(Grade.term_id == term_id)
    
    if academic_year_id:
        query = query.filter(Grade.academic_year_id == academic_year_id)
    
    if grade_type:
        query = query.filter(Grade.grade_type == grade_type)
    
    if is_published is not None:
        query = query.filter(Grade.is_published == is_published)
    
    total = query.count()
    grades = query.order_by(Grade.exam_date.desc()).offset(skip).limit(limit).all()
    
    return grades, total


def create_grade(db: Session, grade_data: GradeCreate, tenant_id: UUID, graded_by: Optional[UUID] = None) -> Grade:
    """Create a new grade"""
    db_grade = Grade(
        tenant_id=tenant_id,
        **grade_data.model_dump(),
        graded_by=graded_by
    )
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    
    logger.info(f"Created grade {db_grade.id} for student {grade_data.student_id}")
    return db_grade


def update_grade(
    db: Session,
    grade_id: UUID,
    grade_update: GradeUpdate,
    tenant_id: UUID
) -> Optional[Grade]:
    """Update a grade"""
    db_grade = get_grade(db, grade_id, tenant_id)
    if not db_grade:
        return None
    
    update_data = grade_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_grade, field, value)
    
    db.commit()
    db.refresh(db_grade)
    return db_grade


def delete_grade(db: Session, grade_id: UUID, tenant_id: UUID) -> bool:
    """Delete a grade"""
    db_grade = get_grade(db, grade_id, tenant_id)
    if not db_grade:
        return False
    
    db.delete(db_grade)
    db.commit()
    return True


def bulk_create_grades(
    db: Session,
    classroom_id: UUID,
    subject_id: UUID,
    grades_data: List[Dict],
    tenant_id: UUID,
    term_id: Optional[UUID] = None,
    assessment_id: Optional[UUID] = None,
    grade_type: GradeType = GradeType.EXAM,
    title: Optional[str] = None,
    exam_date: Optional[date] = None,
    max_score: float = 20.0,
    coefficient: float = 1.0,
    graded_by: Optional[UUID] = None
) -> Dict[str, Any]:
    """Create multiple grades at once (bulk entry)"""
    created = 0
    updated = 0
    failed = 0
    errors = []
    
    for grade_entry in grades_data:
        try:
            student_id = grade_entry.get('student_id')
            score = grade_entry.get('score')
            
            if not student_id or score is None:
                errors.append({"student_id": str(student_id), "error": "Missing student_id or score"})
                failed += 1
                continue
            
            # Check if grade already exists
            existing = db.query(Grade).filter(
                Grade.tenant_id == tenant_id,
                Grade.student_id == student_id,
                Grade.subject_id == subject_id,
                Grade.assessment_id == assessment_id,
                Grade.term_id == term_id
            ).first()
            
            if existing:
                existing.score = score
                existing.max_score = max_score
                existing.coefficient = coefficient
                existing.comments = grade_entry.get('comments')
                updated += 1
            else:
                new_grade = Grade(
                    tenant_id=tenant_id,
                    student_id=student_id,
                    subject_id=subject_id,
                    classroom_id=classroom_id,
                    assessment_id=assessment_id,
                    term_id=term_id,
                    score=score,
                    max_score=max_score,
                    coefficient=coefficient,
                    grade_type=grade_type,
                    title=title,
                    exam_date=exam_date or date.today(),
                    comments=grade_entry.get('comments'),
                    graded_by=graded_by
                )
                db.add(new_grade)
                created += 1
                
        except Exception as e:
            errors.append({"student_id": str(grade_entry.get('student_id')), "error": str(e)})
            failed += 1
    
    db.commit()
    
    return {
        "created": created,
        "updated": updated,
        "failed": failed,
        "errors": errors
    }


def publish_grades(
    db: Session,
    grade_ids: List[UUID],
    tenant_id: UUID
) -> int:
    """Publish multiple grades (make visible to students/parents)"""
    count = db.query(Grade).filter(
        Grade.id.in_(grade_ids),
        Grade.tenant_id == tenant_id
    ).update({"is_published": 1}, synchronize_session=False)
    
    db.commit()
    return count


def get_student_average(
    db: Session,
    student_id: UUID,
    tenant_id: UUID,
    term_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
    academic_year_id: Optional[UUID] = None
) -> GradeStats:
    """Calculate student's grade statistics"""
    query = db.query(Grade).filter(
        Grade.student_id == student_id,
        Grade.tenant_id == tenant_id,
        Grade.is_published == True
    )
    
    if term_id:
        query = query.filter(Grade.term_id == term_id)
    
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    
    if academic_year_id:
        query = query.filter(Grade.academic_year_id == academic_year_id)
    
    grades = query.all()
    
    if not grades:
        return GradeStats(
            average=0.0,
            min_score=0.0,
            max_score=0.0,
            count=0,
            passing_count=0,
            failing_count=0,
            pass_rate=0.0
        )
    
    normalized_scores = [g.normalized_score for g in grades]
    avg = GradeCalculation.calculate_weighted_average(grades)
    
    passing = [s for s in normalized_scores if s >= 10]
    failing = [s for s in normalized_scores if s < 10]
    
    return GradeStats(
        average=round(avg, 2),
        min_score=round(min(normalized_scores), 2),
        max_score=round(max(normalized_scores), 2),
        count=len(grades),
        passing_count=len(passing),
        failing_count=len(failing),
        pass_rate=round(len(passing) / len(grades) * 100, 1) if grades else 0
    )


def get_classroom_averages(
    db: Session,
    classroom_id: UUID,
    tenant_id: UUID,
    term_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None
) -> List[Dict]:
    """Get averages for all students in a classroom"""
    query = db.query(Grade).filter(
        Grade.classroom_id == classroom_id,
        Grade.tenant_id == tenant_id,
        Grade.is_published == True
    )
    
    if term_id:
        query = query.filter(Grade.term_id == term_id)
    
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    
    grades = query.all()
    
    # Group by student
    student_grades = {}
    for g in grades:
        if g.student_id not in student_grades:
            student_grades[g.student_id] = []
        student_grades[g.student_id].append(g)
    
    # Calculate averages
    results = []
    for student_id, student_grade_list in student_grades.items():
        avg = GradeCalculation.calculate_weighted_average(student_grade_list)
        results.append({
            "student_id": str(student_id),
            "average": round(avg, 2),
            "count": len(student_grade_list)
        })
    
    # Sort by average descending
    results.sort(key=lambda x: x['average'], reverse=True)
    
    # Add ranks
    for i, r in enumerate(results, 1):
        r['rank'] = i
    
    return results


def get_report_card(
    db: Session,
    student_id: UUID,
    tenant_id: UUID,
    term_id: Optional[UUID] = None,
    academic_year_id: Optional[UUID] = None
) -> Optional[ReportCard]:
    """Generate a complete report card (bulletin) for a student"""
    from app.models import Student, Subject, Classroom, Term, AcademicYear
    
    # Get student info
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return None
    
    # Get all grades for the period
    query = db.query(Grade).filter(
        Grade.student_id == student_id,
        Grade.tenant_id == tenant_id,
        Grade.is_published == True
    )
    
    if term_id:
        query = query.filter(Grade.term_id == term_id)
    
    if academic_year_id:
        query = query.filter(Grade.academic_year_id == academic_year_id)
    
    grades = query.all()
    
    if not grades:
        return None
    
    # Group grades by subject
    subject_grades = {}
    for g in grades:
        if g.subject_id not in subject_grades:
            subject_grades[g.subject_id] = []
        subject_grades[g.subject_id].append(g)
    
    # Build subject reports
    subject_reports = []
    for subject_id, subject_grade_list in subject_grades.items():
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        avg = GradeCalculation.calculate_weighted_average(subject_grade_list)
        
        subject_report = SubjectReport(
            subject_id=subject_id,
            subject_name=subject.name if subject else "Unknown",
            coefficient=subject.coefficient if subject else 1.0,
            grades=subject_grade_list,
            average=round(avg, 2),
            rank=None,  # Would need to calculate per subject
            mention=GradeCalculation.calculate_appreciation(avg).split('.')[0] if avg >= 10 else "Insuffisant",
            appreciation=None
        )
        subject_reports.append(subject_report)
    
    # Calculate general average
    general_avg = GradeCalculation.calculate_weighted_average(grades)
    
    # Get class rank
    classroom_grades = get_classroom_averages(db, student.classroom_id, tenant_id, term_id) if student.classroom_id else []
    rank = 1
    total_students = len(classroom_grades)
    for i, cg in enumerate(classroom_grades, 1):
        if cg['student_id'] == str(student_id):
            rank = i
            break
    
    # Get term and academic year info
    term = db.query(Term).filter(Term.id == term_id).first() if term_id else None
    academic_year = db.query(AcademicYear).filter(AcademicYear.id == academic_year_id).first() if academic_year_id else None
    classroom = db.query(Classroom).filter(Classroom.id == student.classroom_id).first() if student.classroom_id else None
    
    return ReportCard(
        student_id=student_id,
        student_name=f"{student.first_name} {student.last_name}",
        classroom_name=classroom.name if classroom else "N/A",
        term_name=term.name if term else None,
        academic_year=academic_year.name if academic_year else "N/A",
        subjects=subject_reports,
        general_average=round(general_avg, 2),
        rank=rank,
        total_students=total_students,
        mention=GradeCalculation.calculate_appreciation(general_avg).split('.')[0] if general_avg >= 10 else "Insuffisant",
        appreciation=GradeCalculation.calculate_appreciation(general_avg),
        principal_comment=None,
        generated_at=date.today()
    )


def get_grade_distribution(
    db: Session,
    tenant_id: UUID,
    classroom_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None
) -> Dict[str, int]:
    """Get distribution of grades by letter grade"""
    query = db.query(Grade).filter(Grade.tenant_id == tenant_id)
    
    if classroom_id:
        query = query.filter(Grade.classroom_id == classroom_id)
    
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    
    grades = query.all()
    
    distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
    for g in grades:
        letter = g.letter_grade
        distribution[letter] = distribution.get(letter, 0) + 1
    
    return distribution
