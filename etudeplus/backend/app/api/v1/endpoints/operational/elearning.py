"""
E-Learning API Endpoints - Complete Implementation
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.elearning import (
    Course, CourseCreate, CourseUpdate,
    Lesson, LessonCreate, LessonUpdate,
    LessonResource, LessonResourceCreate, LessonResourceUpdate,
    CourseEnrollment, CourseEnrollmentCreate,
    LessonProgress, LessonProgressUpdate,
    HomeworkAssignment, HomeworkAssignmentCreate, HomeworkAssignmentUpdate,
    HomeworkSubmission, HomeworkSubmissionCreate, HomeworkSubmissionGrade,
    CourseDiscussion, DiscussionCreate, DiscussionUpdate,
    DiscussionReply, DiscussionReplyCreate,
    ElearningStatistics
)
from app.crud import elearning as crud_elearning

router = APIRouter()


# ─── Courses ─────────────────────────────────────────────────────────────────

@router.get("/courses/", response_model=List[Course])
def list_courses(
    teacher_id: Optional[UUID] = None,
    subject_id: Optional[UUID] = None,
    level_id: Optional[UUID] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List courses with optional filters."""
    return crud_elearning.get_courses(
        db,
        tenant_id=current_user.get("tenant_id"),
        teacher_id=teacher_id,
        subject_id=subject_id,
        level_id=level_id,
        status=status,
        search=search,
        skip=skip,
        limit=limit
    )


@router.post("/courses/", response_model=Course)
def create_course(
    obj_in: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new course."""
    return crud_elearning.create_course(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))


@router.get("/courses/{course_id}/", response_model=Course)
def get_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific course."""
    course = crud_elearning.get_course(db, course_id=course_id, tenant_id=current_user.get("tenant_id"))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.put("/courses/{course_id}/", response_model=Course)
def update_course(
    course_id: UUID,
    obj_in: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a course."""
    course = crud_elearning.update_course(db, course_id=course_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.delete("/courses/{course_id}/")
def delete_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a course."""
    success = crud_elearning.delete_course(db, course_id=course_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"status": "success"}


@router.post("/courses/{course_id}/publish/", response_model=Course)
def publish_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Publish a course."""
    course = crud_elearning.publish_course(db, course_id=course_id, tenant_id=current_user.get("tenant_id"))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/courses/{course_id}/archive/", response_model=Course)
def archive_course(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Archive a course."""
    course = crud_elearning.archive_course(db, course_id=course_id, tenant_id=current_user.get("tenant_id"))
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


# ─── Lessons ─────────────────────────────────────────────────────────────────

@router.get("/courses/{course_id}/lessons/", response_model=List[Lesson])
def list_lessons(
    course_id: UUID,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List lessons for a course."""
    return crud_elearning.get_lessons(db, course_id=course_id, tenant_id=current_user.get("tenant_id"), status=status)


@router.post("/lessons/", response_model=Lesson)
def create_lesson(
    obj_in: LessonCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new lesson."""
    return crud_elearning.create_lesson(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))


@router.get("/lessons/{lesson_id}/", response_model=Lesson)
def get_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific lesson."""
    lesson = crud_elearning.get_lesson(db, lesson_id=lesson_id, tenant_id=current_user.get("tenant_id"))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.put("/lessons/{lesson_id}/", response_model=Lesson)
def update_lesson(
    lesson_id: UUID,
    obj_in: LessonUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a lesson."""
    lesson = crud_elearning.update_lesson(db, lesson_id=lesson_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.delete("/lessons/{lesson_id}/")
def delete_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a lesson."""
    success = crud_elearning.delete_lesson(db, lesson_id=lesson_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"status": "success"}


@router.post("/courses/{course_id}/lessons/reorder/")
def reorder_lessons(
    course_id: UUID,
    lesson_ids: List[UUID],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Reorder lessons within a course."""
    success = crud_elearning.reorder_lessons(db, course_id=course_id, lesson_ids=lesson_ids, tenant_id=current_user.get("tenant_id"))
    return {"status": "success" if success else "failed"}


# ─── Lesson Resources ────────────────────────────────────────────────────────

@router.get("/lessons/{lesson_id}/resources/", response_model=List[LessonResource])
def list_lesson_resources(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List resources for a lesson."""
    return crud_elearning.get_lesson_resources(db, lesson_id=lesson_id, tenant_id=current_user.get("tenant_id"))


@router.post("/lesson-resources/", response_model=LessonResource)
def create_lesson_resource(
    obj_in: LessonResourceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a lesson resource."""
    return crud_elearning.create_lesson_resource(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))


@router.delete("/lesson-resources/{resource_id}/")
def delete_lesson_resource(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a lesson resource."""
    success = crud_elearning.delete_lesson_resource(db, resource_id=resource_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"status": "success"}


# ─── Enrollments ─────────────────────────────────────────────────────────────

@router.get("/enrollments/", response_model=List[CourseEnrollment])
def list_enrollments(
    course_id: Optional[UUID] = None,
    student_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List enrollments."""
    return crud_elearning.get_enrollments(
        db,
        tenant_id=current_user.get("tenant_id"),
        course_id=course_id,
        student_id=student_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.post("/enrollments/", response_model=CourseEnrollment)
def create_enrollment(
    obj_in: CourseEnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Enroll in a course."""
    try:
        return crud_elearning.create_enrollment(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/enrollments/{enrollment_id}/")
def unenroll(
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Unenroll from a course."""
    success = crud_elearning.unenroll_student(db, enrollment_id=enrollment_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"status": "success"}


# ─── Lesson Progress ─────────────────────────────────────────────────────────

@router.put("/progress/{lesson_id}/{enrollment_id}/", response_model=LessonProgress)
def update_lesson_progress(
    lesson_id: UUID,
    enrollment_id: UUID,
    obj_in: LessonProgressUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update lesson progress."""
    return crud_elearning.update_lesson_progress(
        db,
        lesson_id=lesson_id,
        enrollment_id=enrollment_id,
        obj_in=obj_in,
        tenant_id=current_user.get("tenant_id")
    )


@router.post("/progress/{lesson_id}/{enrollment_id}/complete/", response_model=LessonProgress)
def mark_lesson_complete(
    lesson_id: UUID,
    enrollment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark a lesson as complete."""
    return crud_elearning.mark_lesson_complete(
        db,
        lesson_id=lesson_id,
        enrollment_id=enrollment_id,
        tenant_id=current_user.get("tenant_id")
    )


# ─── Homework Assignments ────────────────────────────────────────────────────

@router.get("/assignments/", response_model=List[HomeworkAssignment])
def list_assignments(
    course_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List homework assignments."""
    return crud_elearning.get_assignments(
        db,
        tenant_id=current_user.get("tenant_id"),
        course_id=course_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.post("/assignments/", response_model=HomeworkAssignment)
def create_assignment(
    obj_in: HomeworkAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a homework assignment."""
    return crud_elearning.create_assignment(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))


@router.get("/assignments/{assignment_id}/", response_model=HomeworkAssignment)
def get_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific assignment."""
    assignment = crud_elearning.get_assignment(db, assignment_id=assignment_id, tenant_id=current_user.get("tenant_id"))
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.put("/assignments/{assignment_id}/", response_model=HomeworkAssignment)
def update_assignment(
    assignment_id: UUID,
    obj_in: HomeworkAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update an assignment."""
    assignment = crud_elearning.update_assignment(db, assignment_id=assignment_id, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@router.delete("/assignments/{assignment_id}/")
def delete_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete an assignment."""
    success = crud_elearning.delete_assignment(db, assignment_id=assignment_id, tenant_id=current_user.get("tenant_id"))
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"status": "success"}


@router.get("/assignments/upcoming/", response_model=List[HomeworkAssignment])
def get_upcoming_assignments(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get upcoming assignments for the current student."""
    return crud_elearning.get_upcoming_assignments(
        db,
        student_id=current_user.get("user_id"),
        tenant_id=current_user.get("tenant_id"),
        days=days
    )


# ─── Homework Submissions ─────────────────────────────────────────────────────

@router.get("/submissions/", response_model=List[HomeworkSubmission])
def list_submissions(
    assignment_id: Optional[UUID] = None,
    student_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List homework submissions."""
    return crud_elearning.get_submissions(
        db,
        tenant_id=current_user.get("tenant_id"),
        assignment_id=assignment_id,
        student_id=student_id,
        status=status,
        skip=skip,
        limit=limit
    )


@router.post("/submissions/", response_model=HomeworkSubmission)
def create_submission(
    obj_in: HomeworkSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Submit homework."""
    try:
        return crud_elearning.create_submission(db, obj_in=obj_in, tenant_id=current_user.get("tenant_id"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/submissions/{submission_id}/", response_model=HomeworkSubmission)
def get_submission(
    submission_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific submission."""
    submission = crud_elearning.get_submission(db, submission_id=submission_id, tenant_id=current_user.get("tenant_id"))
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.post("/submissions/{submission_id}/grade/", response_model=HomeworkSubmission)
def grade_submission(
    submission_id: UUID,
    grade_data: HomeworkSubmissionGrade,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Grade a submission."""
    submission = crud_elearning.grade_submission(
        db,
        submission_id=submission_id,
        grade_data=grade_data,
        grader_id=current_user.get("user_id"),
        tenant_id=current_user.get("tenant_id")
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


# ─── Discussions ──────────────────────────────────────────────────────────────

@router.get("/courses/{course_id}/discussions/", response_model=List[CourseDiscussion])
def list_discussions(
    course_id: UUID,
    lesson_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List discussions for a course."""
    return crud_elearning.get_discussions(
        db,
        course_id=course_id,
        tenant_id=current_user.get("tenant_id"),
        lesson_id=lesson_id,
        skip=skip,
        limit=limit
    )


@router.post("/discussions/", response_model=CourseDiscussion)
def create_discussion(
    obj_in: DiscussionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a discussion."""
    return crud_elearning.create_discussion(
        db,
        obj_in=obj_in,
        author_id=current_user.get("user_id"),
        tenant_id=current_user.get("tenant_id")
    )


@router.get("/discussions/{discussion_id}/", response_model=CourseDiscussion)
def get_discussion(
    discussion_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific discussion."""
    discussion = crud_elearning.get_discussion(db, discussion_id=discussion_id, tenant_id=current_user.get("tenant_id"))
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    
    # Increment view count
    crud_elearning.increment_discussion_views(db, discussion_id=discussion_id, tenant_id=current_user.get("tenant_id"))
    
    return discussion


@router.put("/discussions/{discussion_id}/", response_model=CourseDiscussion)
def update_discussion(
    discussion_id: UUID,
    obj_in: DiscussionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update a discussion."""
    discussion = crud_elearning.get_discussion(db, discussion_id=discussion_id, tenant_id=current_user.get("tenant_id"))
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(discussion, field, value)
    
    db.commit()
    db.refresh(discussion)
    return discussion


@router.get("/discussions/{discussion_id}/replies/", response_model=List[DiscussionReply])
def list_replies(
    discussion_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """List replies for a discussion."""
    return crud_elearning.get_replies(db, discussion_id=discussion_id, tenant_id=current_user.get("tenant_id"))


@router.post("/replies/", response_model=DiscussionReply)
def create_reply(
    obj_in: DiscussionReplyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a reply."""
    return crud_elearning.create_reply(
        db,
        obj_in=obj_in,
        author_id=current_user.get("user_id"),
        tenant_id=current_user.get("tenant_id")
    )


@router.post("/replies/{reply_id}/mark-answer/", response_model=DiscussionReply)
def mark_reply_as_answer(
    reply_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark a reply as the accepted answer."""
    reply = crud_elearning.mark_reply_as_answer(db, reply_id=reply_id, tenant_id=current_user.get("tenant_id"))
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    return reply


# ─── Statistics ───────────────────────────────────────────────────────────────

@router.get("/statistics/", response_model=ElearningStatistics)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get E-Learning statistics for dashboard."""
    return crud_elearning.get_library_statistics(db, tenant_id=current_user.get("tenant_id"))
