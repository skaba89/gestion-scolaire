"""
E-Learning Models - Courses, Lessons, Homework, Resources, and Progress Tracking
"""
from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, Boolean, Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import date, datetime
import enum

from app.models.base import Base, TimestampMixin, UUIDMixin, TenantMixin


class CourseStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class LessonStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class HomeworkStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    GRADED = "graded"
    LATE = "late"


# ─── Courses ─────────────────────────────────────────────────────────────────

class Course(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """A course is a collection of lessons and resources."""
    __tablename__ = "elearning_courses"
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    code = Column(String(20), unique=True)  # e.g., "MATH101"
    
    # Relationships
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"))
    level_id = Column(UUID(as_uuid=True), ForeignKey("levels.id"))
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    classroom_id = Column(UUID(as_uuid=True), ForeignKey("classrooms.id"))
    academic_year_id = Column(UUID(as_uuid=True), ForeignKey("academic_years.id"))
    
    # Course details
    status = Column(String(20), default="draft")
    cover_image_url = Column(String(500))
    syllabus = Column(Text)
    
    # Settings
    is_public = Column(Boolean, default=False)
    allow_discussions = Column(Boolean, default=True)
    allow_questions = Column(Boolean, default=True)
    max_students = Column(Integer, default=50)
    
    # Progress tracking
    total_lessons = Column(Integer, default=0)
    total_duration_hours = Column(Float, default=0.0)
    
    # Relationships
    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")
    homework_assignments = relationship("HomeworkAssignment", back_populates="course", cascade="all, delete-orphan")


class CourseEnrollment(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Student enrollment in a course."""
    __tablename__ = "elearning_enrollments"
    
    course_id = Column(UUID(as_uuid=True), ForeignKey("elearning_courses.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    enrollment_date = Column(Date, default=date.today)
    status = Column(String(20), default="active")  # active, completed, dropped
    
    # Progress
    progress_percentage = Column(Float, default=0.0)
    completed_lessons = Column(Integer, default=0)
    last_accessed = Column(Date)
    
    # Relationships
    course = relationship("Course", back_populates="enrollments")
    progress_records = relationship("LessonProgress", back_populates="enrollment", cascade="all, delete-orphan")


# ─── Lessons ────────────────────────────────────────────────────────────────

class Lesson(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """A lesson within a course."""
    __tablename__ = "elearning_lessons"
    
    course_id = Column(UUID(as_uuid=True), ForeignKey("elearning_courses.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text)  # HTML or Markdown content
    
    # Ordering
    order_index = Column(Integer, default=0)
    
    # Details
    status = Column(String(20), default="draft")
    duration_minutes = Column(Integer, default=30)
    
    # Media
    video_url = Column(String(500))
    video_duration_seconds = Column(Integer)
    
    # Settings
    is_preview = Column(Boolean, default=False)  # Can be previewed without enrollment
    requires_completion = Column(Boolean, default=True)  # Must complete to progress
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    resources = relationship("LessonResource", back_populates="lesson", cascade="all, delete-orphan")
    progress_records = relationship("LessonProgress", back_populates="lesson", cascade="all, delete-orphan")


class LessonResource(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Resources attached to a lesson (files, links, etc.)."""
    __tablename__ = "elearning_lesson_resources"
    
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("elearning_lessons.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    resource_type = Column(String(50))  # file, link, video, document, etc.
    file_url = Column(String(500))
    file_size = Column(Integer)  # in bytes
    
    # For external links
    external_url = Column(String(500))
    
    # Settings
    is_downloadable = Column(Boolean, default=True)
    download_count = Column(Integer, default=0)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="resources")


class LessonProgress(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Track student progress on lessons."""
    __tablename__ = "elearning_lesson_progress"
    
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("elearning_lessons.id", ondelete="CASCADE"), nullable=False)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("elearning_enrollments.id", ondelete="CASCADE"), nullable=False)
    
    # Progress
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed
    progress_percentage = Column(Float, default=0.0)
    
    # Video tracking
    video_position_seconds = Column(Integer, default=0)
    
    # Completion
    started_at = Column(Date)
    completed_at = Column(Date)
    time_spent_minutes = Column(Integer, default=0)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="progress_records")
    enrollment = relationship("CourseEnrollment", back_populates="progress_records")


# ─── Homework ───────────────────────────────────────────────────────────────

class HomeworkAssignment(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Homework assignment created by teacher."""
    __tablename__ = "elearning_homework_assignments"
    
    course_id = Column(UUID(as_uuid=True), ForeignKey("elearning_courses.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("elearning_lessons.id", ondelete="SET NULL"))
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    instructions = Column(Text)
    
    # Dates
    assigned_date = Column(Date, default=date.today)
    due_date = Column(Date, nullable=False)
    
    # Settings
    max_score = Column(Float, default=20.0)
    allow_late_submission = Column(Boolean, default=False)
    late_penalty_percent = Column(Float, default=10.0)
    allow_resubmission = Column(Boolean, default=True)
    max_attempts = Column(Integer, default=3)
    
    # Attachments
    attachment_urls = Column(JSONB, default=list)
    
    # Statistics
    submission_count = Column(Integer, default=0)
    average_score = Column(Float)
    
    # Relationships
    course = relationship("Course", back_populates="homework_assignments")
    submissions = relationship("HomeworkSubmission", back_populates="assignment", cascade="all, delete-orphan")


class HomeworkSubmission(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Student submission for homework."""
    __tablename__ = "elearning_homework_submissions"
    
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("elearning_homework_assignments.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Submission
    content = Column(Text)  # Text submission
    attachment_urls = Column(JSONB, default=list)
    submitted_at = Column(Date, default=date.today)
    
    # Status
    status = Column(String(20), default="pending")
    attempt_number = Column(Integer, default=1)
    
    # Grading
    score = Column(Float)
    feedback = Column(Text)
    graded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    graded_at = Column(Date)
    
    # For late submissions
    is_late = Column(Boolean, default=False)
    late_penalty_applied = Column(Float, default=0.0)
    final_score = Column(Float)
    
    # Relationships
    assignment = relationship("HomeworkAssignment", back_populates="submissions")


# ─── Questions & Discussions ────────────────────────────────────────────────

class CourseDiscussion(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Discussion forum for a course."""
    __tablename__ = "elearning_discussions"
    
    course_id = Column(UUID(as_uuid=True), ForeignKey("elearning_courses.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("elearning_lessons.id", ondelete="SET NULL"))
    
    title = Column(String(255), nullable=False)
    content = Column(Text)
    
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    
    view_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    # Relationships
    replies = relationship("DiscussionReply", back_populates="discussion", cascade="all, delete-orphan")


class DiscussionReply(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Reply to a discussion."""
    __tablename__ = "elearning_discussion_replies"
    
    discussion_id = Column(UUID(as_uuid=True), ForeignKey("elearning_discussions.id", ondelete="CASCADE"), nullable=False)
    parent_reply_id = Column(UUID(as_uuid=True), ForeignKey("elearning_discussion_replies.id"))
    
    content = Column(Text, nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    is_answer = Column(Boolean, default=False)  # Marked as answer by teacher
    
    # Relationships
    discussion = relationship("CourseDiscussion", back_populates="replies")
    replies = relationship("DiscussionReply", backref="parent", remote_side="DiscussionReply.id")
