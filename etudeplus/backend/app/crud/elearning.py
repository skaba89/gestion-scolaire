"""
E-Learning CRUD Operations
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from uuid import UUID
from datetime import date, timedelta

from app.models.elearning import (
    Course, CourseEnrollment, Lesson, LessonResource, LessonProgress,
    HomeworkAssignment, HomeworkSubmission, CourseDiscussion, DiscussionReply
)
from app.schemas.elearning import (
    CourseCreate, CourseUpdate,
    LessonCreate, LessonUpdate, LessonResourceCreate, LessonResourceUpdate,
    CourseEnrollmentCreate, CourseEnrollmentUpdate,
    LessonProgressUpdate,
    HomeworkAssignmentCreate, HomeworkAssignmentUpdate,
    HomeworkSubmissionCreate, HomeworkSubmissionGrade,
    DiscussionCreate, DiscussionUpdate, DiscussionReplyCreate
)


# ─── Courses ────────────────────────────────────────────────────────────────

def get_courses(
    db: Session,
    tenant_id: UUID,
    teacher_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
    level_id: Optional[UUID] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[Course]:
    """Get courses with optional filters."""
    query = db.query(Course).filter(Course.tenant_id == tenant_id)
    
    if teacher_id:
        query = query.filter(Course.teacher_id == teacher_id)
    
    if subject_id:
        query = query.filter(Course.subject_id == subject_id)
    
    if level_id:
        query = query.filter(Course.level_id == level_id)
    
    if status:
        query = query.filter(Course.status == status)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Course.title.ilike(search_pattern),
                Course.description.ilike(search_pattern),
                Course.code.ilike(search_pattern)
            )
        )
    
    return query.order_by(Course.created_at.desc()).offset(skip).limit(limit).all()


def get_course(db: Session, course_id: UUID, tenant_id: UUID) -> Optional[Course]:
    """Get a specific course."""
    return db.query(Course).filter(
        Course.id == course_id,
        Course.tenant_id == tenant_id
    ).first()


def create_course(db: Session, obj_in: CourseCreate, tenant_id: UUID) -> Course:
    """Create a new course."""
    course = Course(**obj_in.model_dump(), tenant_id=tenant_id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def update_course(db: Session, course_id: UUID, obj_in: CourseUpdate, tenant_id: UUID) -> Optional[Course]:
    """Update a course."""
    course = get_course(db, course_id, tenant_id)
    if not course:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: UUID, tenant_id: UUID) -> bool:
    """Delete a course."""
    course = get_course(db, course_id, tenant_id)
    if not course:
        return False
    db.delete(course)
    db.commit()
    return True


def publish_course(db: Session, course_id: UUID, tenant_id: UUID) -> Optional[Course]:
    """Publish a course."""
    course = get_course(db, course_id, tenant_id)
    if not course:
        return None
    course.status = "published"
    db.commit()
    db.refresh(course)
    return course


def archive_course(db: Session, course_id: UUID, tenant_id: UUID) -> Optional[Course]:
    """Archive a course."""
    course = get_course(db, course_id, tenant_id)
    if not course:
        return None
    course.status = "archived"
    db.commit()
    db.refresh(course)
    return course


# ─── Lessons ────────────────────────────────────────────────────────────────

def get_lessons(
    db: Session,
    course_id: UUID,
    tenant_id: UUID,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[Lesson]:
    """Get lessons for a course."""
    query = db.query(Lesson).filter(
        Lesson.course_id == course_id,
        Lesson.tenant_id == tenant_id
    )
    
    if status:
        query = query.filter(Lesson.status == status)
    
    return query.order_by(Lesson.order_index).offset(skip).limit(limit).all()


def get_lesson(db: Session, lesson_id: UUID, tenant_id: UUID) -> Optional[Lesson]:
    """Get a specific lesson."""
    return db.query(Lesson).filter(
        Lesson.id == lesson_id,
        Lesson.tenant_id == tenant_id
    ).first()


def create_lesson(db: Session, obj_in: LessonCreate, tenant_id: UUID) -> Lesson:
    """Create a new lesson."""
    lesson = Lesson(**obj_in.model_dump(), tenant_id=tenant_id)
    db.add(lesson)
    
    # Update course total lessons
    course = get_course(db, obj_in.course_id, tenant_id)
    if course:
        course.total_lessons += 1
        course.total_duration_hours += lesson.duration_minutes / 60
    
    db.commit()
    db.refresh(lesson)
    return lesson


def update_lesson(db: Session, lesson_id: UUID, obj_in: LessonUpdate, tenant_id: UUID) -> Optional[Lesson]:
    """Update a lesson."""
    lesson = get_lesson(db, lesson_id, tenant_id)
    if not lesson:
        return None
    
    old_duration = lesson.duration_minutes
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lesson, field, value)
    
    # Update course duration if changed
    if 'duration_minutes' in update_data:
        course = get_course(db, lesson.course_id, tenant_id)
        if course:
            course.total_duration_hours += (lesson.duration_minutes - old_duration) / 60
    
    db.commit()
    db.refresh(lesson)
    return lesson


def delete_lesson(db: Session, lesson_id: UUID, tenant_id: UUID) -> bool:
    """Delete a lesson."""
    lesson = get_lesson(db, lesson_id, tenant_id)
    if not lesson:
        return False
    
    # Update course total lessons
    course = get_course(db, lesson.course_id, tenant_id)
    if course:
        course.total_lessons -= 1
        course.total_duration_hours -= lesson.duration_minutes / 60
    
    db.delete(lesson)
    db.commit()
    return True


def reorder_lessons(db: Session, course_id: UUID, lesson_ids: List[UUID], tenant_id: UUID) -> bool:
    """Reorder lessons within a course."""
    for index, lesson_id in enumerate(lesson_ids):
        lesson = get_lesson(db, lesson_id, tenant_id)
        if lesson and lesson.course_id == course_id:
            lesson.order_index = index
    
    db.commit()
    return True


# ─── Lesson Resources ────────────────────────────────────────────────────────

def get_lesson_resources(db: Session, lesson_id: UUID, tenant_id: UUID) -> List[LessonResource]:
    """Get resources for a lesson."""
    return db.query(LessonResource).filter(
        LessonResource.lesson_id == lesson_id,
        LessonResource.tenant_id == tenant_id
    ).order_by(LessonResource.created_at).all()


def create_lesson_resource(db: Session, obj_in: LessonResourceCreate, tenant_id: UUID) -> LessonResource:
    """Create a lesson resource."""
    resource = LessonResource(**obj_in.model_dump(), tenant_id=tenant_id)
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def delete_lesson_resource(db: Session, resource_id: UUID, tenant_id: UUID) -> bool:
    """Delete a lesson resource."""
    resource = db.query(LessonResource).filter(
        LessonResource.id == resource_id,
        LessonResource.tenant_id == tenant_id
    ).first()
    
    if not resource:
        return False
    
    db.delete(resource)
    db.commit()
    return True


def increment_download_count(db: Session, resource_id: UUID, tenant_id: UUID) -> bool:
    """Increment download count for a resource."""
    resource = db.query(LessonResource).filter(
        LessonResource.id == resource_id,
        LessonResource.tenant_id == tenant_id
    ).first()
    
    if not resource:
        return False
    
    resource.download_count += 1
    db.commit()
    return True


# ─── Course Enrollments ──────────────────────────────────────────────────────

def get_enrollments(
    db: Session,
    tenant_id: UUID,
    course_id: Optional[UUID] = None,
    student_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[CourseEnrollment]:
    """Get enrollments with optional filters."""
    query = db.query(CourseEnrollment).filter(CourseEnrollment.tenant_id == tenant_id)
    
    if course_id:
        query = query.filter(CourseEnrollment.course_id == course_id)
    
    if student_id:
        query = query.filter(CourseEnrollment.student_id == student_id)
    
    if status:
        query = query.filter(CourseEnrollment.status == status)
    
    return query.order_by(CourseEnrollment.enrollment_date.desc()).offset(skip).limit(limit).all()


def get_enrollment(db: Session, enrollment_id: UUID, tenant_id: UUID) -> Optional[CourseEnrollment]:
    """Get a specific enrollment."""
    return db.query(CourseEnrollment).filter(
        CourseEnrollment.id == enrollment_id,
        CourseEnrollment.tenant_id == tenant_id
    ).first()


def get_student_enrollment(db: Session, course_id: UUID, student_id: UUID, tenant_id: UUID) -> Optional[CourseEnrollment]:
    """Get a student's enrollment in a course."""
    return db.query(CourseEnrollment).filter(
        CourseEnrollment.course_id == course_id,
        CourseEnrollment.student_id == student_id,
        CourseEnrollment.tenant_id == tenant_id
    ).first()


def create_enrollment(db: Session, obj_in: CourseEnrollmentCreate, tenant_id: UUID) -> CourseEnrollment:
    """Enroll a student in a course."""
    # Check if already enrolled
    existing = get_student_enrollment(db, obj_in.course_id, obj_in.student_id, tenant_id)
    if existing:
        raise ValueError("Student is already enrolled in this course")
    
    # Check course capacity
    course = get_course(db, obj_in.course_id, tenant_id)
    if not course:
        raise ValueError("Course not found")
    
    enrolled_count = db.query(func.count(CourseEnrollment.id)).filter(
        CourseEnrollment.course_id == obj_in.course_id,
        CourseEnrollment.status == "active"
    ).scalar()
    
    if enrolled_count >= course.max_students:
        raise ValueError("Course has reached maximum capacity")
    
    enrollment = CourseEnrollment(
        course_id=obj_in.course_id,
        student_id=obj_in.student_id,
        tenant_id=tenant_id,
        enrollment_date=date.today(),
        status="active"
    )
    
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


def unenroll_student(db: Session, enrollment_id: UUID, tenant_id: UUID) -> bool:
    """Unenroll a student from a course."""
    enrollment = get_enrollment(db, enrollment_id, tenant_id)
    if not enrollment:
        return False
    
    enrollment.status = "dropped"
    db.commit()
    return True


def update_enrollment_progress(db: Session, enrollment_id: UUID, tenant_id: UUID) -> CourseEnrollment:
    """Update enrollment progress based on lesson progress."""
    enrollment = get_enrollment(db, enrollment_id, tenant_id)
    if not enrollment:
        return None
    
    # Count completed lessons
    completed_count = db.query(func.count(LessonProgress.id)).filter(
        LessonProgress.enrollment_id == enrollment_id,
        LessonProgress.status == "completed"
    ).scalar()
    
    total_lessons = db.query(func.count(Lesson.id)).filter(
        Lesson.course_id == enrollment.course_id
    ).scalar()
    
    enrollment.completed_lessons = completed_count
    enrollment.progress_percentage = (completed_count / total_lessons * 100) if total_lessons > 0 else 0
    enrollment.last_accessed = date.today()
    
    # Check if course is complete
    if enrollment.progress_percentage >= 100:
        enrollment.status = "completed"
    
    db.commit()
    db.refresh(enrollment)
    return enrollment


# ─── Lesson Progress ─────────────────────────────────────────────────────────

def get_lesson_progress(
    db: Session,
    lesson_id: UUID,
    enrollment_id: UUID,
    tenant_id: UUID
) -> Optional[LessonProgress]:
    """Get progress for a specific lesson."""
    return db.query(LessonProgress).filter(
        LessonProgress.lesson_id == lesson_id,
        LessonProgress.enrollment_id == enrollment_id,
        LessonProgress.tenant_id == tenant_id
    ).first()


def update_lesson_progress(
    db: Session,
    lesson_id: UUID,
    enrollment_id: UUID,
    obj_in: LessonProgressUpdate,
    tenant_id: UUID
) -> LessonProgress:
    """Update or create lesson progress."""
    progress = get_lesson_progress(db, lesson_id, enrollment_id, tenant_id)
    
    if not progress:
        # Create new progress record
        progress = LessonProgress(
            lesson_id=lesson_id,
            enrollment_id=enrollment_id,
            tenant_id=tenant_id,
            status="in_progress",
            started_at=date.today()
        )
        db.add(progress)
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(progress, field, value)
    
    # Auto-update status based on progress
    if progress.progress_percentage >= 100:
        progress.status = "completed"
        progress.completed_at = date.today()
    elif progress.progress_percentage > 0:
        progress.status = "in_progress"
    
    db.commit()
    db.refresh(progress)
    
    # Update enrollment progress
    update_enrollment_progress(db, enrollment_id, tenant_id)
    
    return progress


def mark_lesson_complete(db: Session, lesson_id: UUID, enrollment_id: UUID, tenant_id: UUID) -> LessonProgress:
    """Mark a lesson as complete."""
    return update_lesson_progress(
        db, lesson_id, enrollment_id,
        LessonProgressUpdate(progress_percentage=100, status="completed"),
        tenant_id
    )


# ─── Homework Assignments ────────────────────────────────────────────────────

def get_assignments(
    db: Session,
    tenant_id: UUID,
    course_id: Optional[UUID] = None,
    teacher_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
) -> List[HomeworkAssignment]:
    """Get homework assignments with optional filters."""
    query = db.query(HomeworkAssignment).filter(HomeworkAssignment.tenant_id == tenant_id)
    
    if course_id:
        query = query.filter(HomeworkAssignment.course_id == course_id)
    
    if status:
        query = query.filter(HomeworkAssignment.status == status)
    
    return query.order_by(HomeworkAssignment.due_date).offset(skip).limit(limit).all()


def get_assignment(db: Session, assignment_id: UUID, tenant_id: UUID) -> Optional[HomeworkAssignment]:
    """Get a specific assignment."""
    return db.query(HomeworkAssignment).filter(
        HomeworkAssignment.id == assignment_id,
        HomeworkAssignment.tenant_id == tenant_id
    ).first()


def create_assignment(db: Session, obj_in: HomeworkAssignmentCreate, tenant_id: UUID) -> HomeworkAssignment:
    """Create a new homework assignment."""
    assignment = HomeworkAssignment(**obj_in.model_dump(), tenant_id=tenant_id)
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def update_assignment(db: Session, assignment_id: UUID, obj_in: HomeworkAssignmentUpdate, tenant_id: UUID) -> Optional[HomeworkAssignment]:
    """Update an assignment."""
    assignment = get_assignment(db, assignment_id, tenant_id)
    if not assignment:
        return None
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    
    db.commit()
    db.refresh(assignment)
    return assignment


def delete_assignment(db: Session, assignment_id: UUID, tenant_id: UUID) -> bool:
    """Delete an assignment."""
    assignment = get_assignment(db, assignment_id, tenant_id)
    if not assignment:
        return False
    db.delete(assignment)
    db.commit()
    return True


def get_upcoming_assignments(db: Session, student_id: UUID, tenant_id: UUID, days: int = 7) -> List[HomeworkAssignment]:
    """Get upcoming assignments for a student."""
    # Get enrolled courses
    enrollments = db.query(CourseEnrollment).filter(
        CourseEnrollment.student_id == student_id,
        CourseEnrollment.status == "active",
        CourseEnrollment.tenant_id == tenant_id
    ).all()
    
    course_ids = [e.course_id for e in enrollments]
    
    if not course_ids:
        return []
    
    end_date = date.today() + timedelta(days=days)
    
    return db.query(HomeworkAssignment).filter(
        HomeworkAssignment.course_id.in_(course_ids),
        HomeworkAssignment.due_date >= date.today(),
        HomeworkAssignment.due_date <= end_date,
        HomeworkAssignment.tenant_id == tenant_id
    ).order_by(HomeworkAssignment.due_date).all()


# ─── Homework Submissions ────────────────────────────────────────────────────

def get_submissions(
    db: Session,
    tenant_id: UUID,
    assignment_id: Optional[UUID] = None,
    student_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[HomeworkSubmission]:
    """Get homework submissions with optional filters."""
    query = db.query(HomeworkSubmission).filter(HomeworkSubmission.tenant_id == tenant_id)
    
    if assignment_id:
        query = query.filter(HomeworkSubmission.assignment_id == assignment_id)
    
    if student_id:
        query = query.filter(HomeworkSubmission.student_id == student_id)
    
    if status:
        query = query.filter(HomeworkSubmission.status == status)
    
    return query.order_by(HomeworkSubmission.submitted_at.desc()).offset(skip).limit(limit).all()


def get_submission(db: Session, submission_id: UUID, tenant_id: UUID) -> Optional[HomeworkSubmission]:
    """Get a specific submission."""
    return db.query(HomeworkSubmission).filter(
        HomeworkSubmission.id == submission_id,
        HomeworkSubmission.tenant_id == tenant_id
    ).first()


def get_student_submission(db: Session, assignment_id: UUID, student_id: UUID, tenant_id: UUID) -> Optional[HomeworkSubmission]:
    """Get a student's latest submission for an assignment."""
    return db.query(HomeworkSubmission).filter(
        HomeworkSubmission.assignment_id == assignment_id,
        HomeworkSubmission.student_id == student_id,
        HomeworkSubmission.tenant_id == tenant_id
    ).order_by(HomeworkSubmission.attempt_number.desc()).first()


def create_submission(db: Session, obj_in: HomeworkSubmissionCreate, tenant_id: UUID) -> HomeworkSubmission:
    """Create a new submission."""
    assignment = get_assignment(db, obj_in.assignment_id, tenant_id)
    if not assignment:
        raise ValueError("Assignment not found")
    
    # Check if late
    is_late = date.today() > assignment.due_date
    
    # Get attempt number
    previous_attempts = db.query(func.count(HomeworkSubmission.id)).filter(
        HomeworkSubmission.assignment_id == obj_in.assignment_id,
        HomeworkSubmission.student_id == obj_in.student_id
    ).scalar()
    
    if previous_attempts >= assignment.max_attempts:
        raise ValueError("Maximum attempts reached")
    
    submission = HomeworkSubmission(
        **obj_in.model_dump(),
        tenant_id=tenant_id,
        submitted_at=date.today(),
        status="late" if is_late else "submitted",
        attempt_number=previous_attempts + 1,
        is_late=is_late
    )
    
    # Update assignment submission count
    assignment.submission_count += 1
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def grade_submission(
    db: Session,
    submission_id: UUID,
    grade_data: HomeworkSubmissionGrade,
    grader_id: UUID,
    tenant_id: UUID
) -> Optional[HomeworkSubmission]:
    """Grade a submission."""
    submission = get_submission(db, submission_id, tenant_id)
    if not submission:
        return None
    
    assignment = get_assignment(db, submission.assignment_id, tenant_id)
    
    submission.score = grade_data.score
    submission.feedback = grade_data.feedback
    submission.graded_by = grader_id
    submission.graded_at = date.today()
    submission.status = "graded"
    
    # Apply late penalty if applicable
    if submission.is_late and assignment:
        submission.late_penalty_applied = assignment.late_penalty_percent
        submission.final_score = submission.score * (1 - assignment.late_penalty_percent / 100)
    else:
        submission.final_score = submission.score
    
    # Update assignment average score
    if assignment:
        avg_score = db.query(func.avg(HomeworkSubmission.final_score)).filter(
            HomeworkSubmission.assignment_id == assignment.id,
            HomeworkSubmission.status == "graded"
        ).scalar()
        assignment.average_score = avg_score
    
    db.commit()
    db.refresh(submission)
    return submission


# ─── Discussions ──────────────────────────────────────────────────────────────

def get_discussions(
    db: Session,
    course_id: UUID,
    tenant_id: UUID,
    lesson_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 20
) -> List[CourseDiscussion]:
    """Get discussions for a course."""
    query = db.query(CourseDiscussion).filter(
        CourseDiscussion.course_id == course_id,
        CourseDiscussion.tenant_id == tenant_id
    )
    
    if lesson_id:
        query = query.filter(CourseDiscussion.lesson_id == lesson_id)
    
    return query.order_by(
        CourseDiscussion.is_pinned.desc(),
        CourseDiscussion.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_discussion(db: Session, discussion_id: UUID, tenant_id: UUID) -> Optional[CourseDiscussion]:
    """Get a specific discussion."""
    return db.query(CourseDiscussion).filter(
        CourseDiscussion.id == discussion_id,
        CourseDiscussion.tenant_id == tenant_id
    ).first()


def create_discussion(db: Session, obj_in: DiscussionCreate, author_id: UUID, tenant_id: UUID) -> CourseDiscussion:
    """Create a new discussion."""
    discussion = CourseDiscussion(
        **obj_in.model_dump(),
        author_id=author_id,
        tenant_id=tenant_id
    )
    db.add(discussion)
    db.commit()
    db.refresh(discussion)
    return discussion


def increment_discussion_views(db: Session, discussion_id: UUID, tenant_id: UUID) -> bool:
    """Increment view count for a discussion."""
    discussion = get_discussion(db, discussion_id, tenant_id)
    if not discussion:
        return False
    discussion.view_count += 1
    db.commit()
    return True


def create_reply(db: Session, obj_in: DiscussionReplyCreate, author_id: UUID, tenant_id: UUID) -> DiscussionReply:
    """Create a reply to a discussion."""
    reply = DiscussionReply(
        **obj_in.model_dump(),
        author_id=author_id,
        tenant_id=tenant_id
    )
    db.add(reply)
    
    # Update discussion reply count
    discussion = get_discussion(db, obj_in.discussion_id, tenant_id)
    if discussion:
        discussion.reply_count += 1
    
    db.commit()
    db.refresh(reply)
    return reply


def get_replies(db: Session, discussion_id: UUID, tenant_id: UUID) -> List[DiscussionReply]:
    """Get replies for a discussion."""
    return db.query(DiscussionReply).filter(
        DiscussionReply.discussion_id == discussion_id,
        DiscussionReply.tenant_id == tenant_id
    ).order_by(DiscussionReply.created_at).all()


def mark_reply_as_answer(db: Session, reply_id: UUID, tenant_id: UUID) -> Optional[DiscussionReply]:
    """Mark a reply as the accepted answer."""
    reply = db.query(DiscussionReply).filter(
        DiscussionReply.id == reply_id,
        DiscussionReply.tenant_id == tenant_id
    ).first()
    
    if not reply:
        return None
    
    reply.is_answer = True
    db.commit()
    db.refresh(reply)
    return reply


# ─── Statistics ───────────────────────────────────────────────────────────────

def get_elearning_statistics(db: Session, tenant_id: UUID) -> dict:
    """Get E-Learning statistics for dashboard."""
    # Total courses
    total_courses = db.query(func.count(Course.id)).filter(
        Course.tenant_id == tenant_id
    ).scalar()
    
    # Total lessons
    total_lessons = db.query(func.count(Lesson.id)).filter(
        Lesson.tenant_id == tenant_id
    ).scalar()
    
    # Enrollments
    total_enrollments = db.query(func.count(CourseEnrollment.id)).filter(
        CourseEnrollment.tenant_id == tenant_id
    ).scalar()
    
    active_enrollments = db.query(func.count(CourseEnrollment.id)).filter(
        CourseEnrollment.tenant_id == tenant_id,
        CourseEnrollment.status == "active"
    ).scalar()
    
    completed_enrollments = db.query(func.count(CourseEnrollment.id)).filter(
        CourseEnrollment.tenant_id == tenant_id,
        CourseEnrollment.status == "completed"
    ).scalar()
    
    # Assignments
    total_assignments = db.query(func.count(HomeworkAssignment.id)).filter(
        HomeworkAssignment.tenant_id == tenant_id
    ).scalar()
    
    pending_submissions = db.query(func.count(HomeworkSubmission.id)).filter(
        HomeworkSubmission.tenant_id == tenant_id,
        HomeworkSubmission.status == "submitted"
    ).scalar()
    
    # Average completion rate
    avg_completion = db.query(func.avg(CourseEnrollment.progress_percentage)).filter(
        CourseEnrollment.tenant_id == tenant_id,
        CourseEnrollment.status == "active"
    ).scalar() or 0
    
    # By status
    by_status = db.query(
        Course.status,
        func.count(Course.id).label('count')
    ).filter(
        Course.tenant_id == tenant_id
    ).group_by(Course.status).all()
    
    # Top courses by enrollment
    top_courses = db.query(
        Course.title,
        func.count(CourseEnrollment.id).label('enrollments')
    ).join(CourseEnrollment).filter(
        Course.tenant_id == tenant_id
    ).group_by(Course.id, Course.title).order_by(
        func.count(CourseEnrollment.id).desc()
    ).limit(5).all()
    
    return {
        'total_courses': total_courses,
        'total_lessons': total_lessons,
        'total_enrollments': total_enrollments,
        'active_enrollments': active_enrollments,
        'completed_enrollments': completed_enrollments,
        'total_assignments': total_assignments,
        'pending_submissions': pending_submissions,
        'average_completion_rate': round(float(avg_completion), 2),
        'by_status': [{'status': r[0], 'count': r[1]} for r in by_status],
        'top_courses': [{'title': r[0], 'enrollments': r[1]} for r in top_courses],
    }
