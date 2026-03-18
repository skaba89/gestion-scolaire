"""
E-Learning Schemas - Pydantic models for API validation
"""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime


# ─── Course Schemas ─────────────────────────────────────────────────────────

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    code: Optional[str] = None
    subject_id: Optional[UUID] = None
    level_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    classroom_id: Optional[UUID] = None
    academic_year_id: Optional[UUID] = None
    cover_image_url: Optional[str] = None
    syllabus: Optional[str] = None
    is_public: bool = False
    allow_discussions: bool = True
    allow_questions: bool = True
    max_students: int = 50


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    subject_id: Optional[UUID] = None
    level_id: Optional[UUID] = None
    teacher_id: Optional[UUID] = None
    classroom_id: Optional[UUID] = None
    cover_image_url: Optional[str] = None
    syllabus: Optional[str] = None
    is_public: Optional[bool] = None
    allow_discussions: Optional[bool] = None
    allow_questions: Optional[bool] = None
    max_students: Optional[int] = None
    status: Optional[str] = None


class Course(CourseBase):
    id: UUID
    tenant_id: UUID
    status: str
    total_lessons: int
    total_duration_hours: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Lesson Schemas ──────────────────────────────────────────────────────────

class LessonBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    order_index: int = 0
    duration_minutes: int = 30
    video_url: Optional[str] = None
    video_duration_seconds: Optional[int] = None
    is_preview: bool = False
    requires_completion: bool = True


class LessonCreate(LessonBase):
    course_id: UUID


class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    order_index: Optional[int] = None
    duration_minutes: Optional[int] = None
    video_url: Optional[str] = None
    video_duration_seconds: Optional[int] = None
    is_preview: Optional[bool] = None
    requires_completion: Optional[bool] = None
    status: Optional[str] = None


class Lesson(LessonBase):
    id: UUID
    course_id: UUID
    tenant_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Lesson Resource Schemas ─────────────────────────────────────────────────

class LessonResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    resource_type: str = "file"
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    external_url: Optional[str] = None
    is_downloadable: bool = True


class LessonResourceCreate(LessonResourceBase):
    lesson_id: UUID


class LessonResourceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    external_url: Optional[str] = None
    is_downloadable: Optional[bool] = None


class LessonResource(LessonResourceBase):
    id: UUID
    lesson_id: UUID
    tenant_id: UUID
    download_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Course Enrollment Schemas ───────────────────────────────────────────────

class CourseEnrollmentBase(BaseModel):
    course_id: UUID
    student_id: UUID


class CourseEnrollmentCreate(CourseEnrollmentBase):
    pass


class CourseEnrollmentUpdate(BaseModel):
    status: Optional[str] = None


class CourseEnrollment(CourseEnrollmentBase):
    id: UUID
    tenant_id: UUID
    enrollment_date: date
    status: str
    progress_percentage: float
    completed_lessons: int
    last_accessed: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Lesson Progress Schemas ─────────────────────────────────────────────────

class LessonProgressBase(BaseModel):
    lesson_id: UUID
    enrollment_id: UUID


class LessonProgressUpdate(BaseModel):
    progress_percentage: Optional[float] = None
    video_position_seconds: Optional[int] = None
    status: Optional[str] = None


class LessonProgress(LessonProgressBase):
    id: UUID
    tenant_id: UUID
    status: str
    progress_percentage: float
    video_position_seconds: int
    started_at: Optional[date]
    completed_at: Optional[date]
    time_spent_minutes: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Homework Assignment Schemas ─────────────────────────────────────────────

class HomeworkAssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    course_id: UUID
    lesson_id: Optional[UUID] = None
    assigned_date: date
    due_date: date
    max_score: float = 20.0
    allow_late_submission: bool = False
    late_penalty_percent: float = 10.0
    allow_resubmission: bool = True
    max_attempts: int = 3
    attachment_urls: Optional[List[str]] = None


class HomeworkAssignmentCreate(HomeworkAssignmentBase):
    pass


class HomeworkAssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    due_date: Optional[date] = None
    max_score: Optional[float] = None
    allow_late_submission: Optional[bool] = None
    late_penalty_percent: Optional[float] = None
    allow_resubmission: Optional[bool] = None
    max_attempts: Optional[int] = None
    attachment_urls: Optional[List[str]] = None


class HomeworkAssignment(HomeworkAssignmentBase):
    id: UUID
    tenant_id: UUID
    submission_count: int
    average_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Homework Submission Schemas ─────────────────────────────────────────────

class HomeworkSubmissionBase(BaseModel):
    assignment_id: UUID
    student_id: UUID
    content: Optional[str] = None
    attachment_urls: Optional[List[str]] = None


class HomeworkSubmissionCreate(HomeworkSubmissionBase):
    pass


class HomeworkSubmissionGrade(BaseModel):
    score: float
    feedback: Optional[str] = None


class HomeworkSubmission(HomeworkSubmissionBase):
    id: UUID
    tenant_id: UUID
    submitted_at: date
    status: str
    attempt_number: int
    score: Optional[float]
    feedback: Optional[str]
    graded_by: Optional[UUID]
    graded_at: Optional[date]
    is_late: bool
    late_penalty_applied: float
    final_score: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Discussion Schemas ──────────────────────────────────────────────────────

class DiscussionBase(BaseModel):
    title: str
    content: str
    course_id: UUID
    lesson_id: Optional[UUID] = None


class DiscussionCreate(DiscussionBase):
    pass


class DiscussionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None


class DiscussionReplyBase(BaseModel):
    content: str
    discussion_id: UUID
    parent_reply_id: Optional[UUID] = None


class DiscussionReplyCreate(DiscussionReplyBase):
    pass


class DiscussionReply(DiscussionReplyBase):
    id: UUID
    tenant_id: UUID
    author_id: UUID
    is_answer: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseDiscussion(DiscussionBase):
    id: UUID
    tenant_id: UUID
    author_id: UUID
    is_pinned: bool
    is_locked: bool
    view_count: int
    reply_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Statistics Schemas ──────────────────────────────────────────────────────

class ElearningStatistics(BaseModel):
    total_courses: int
    total_lessons: int
    total_enrollments: int
    active_enrollments: int
    completed_enrollments: int
    total_assignments: int
    pending_submissions: int
    average_completion_rate: float
    by_status: List[dict]
    top_courses: List[dict]
