"""Add library and elearning tables

Revision ID: add_library_elearning
Revises: final_sync
Create Date: 2025-01-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_library_elearning'
down_revision = 'final_sync'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ─── Library Tables ───────────────────────────────────────────────────────
    
    # Library categories
    op.create_table(
        'library_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('color', sa.String(7), default='#3498db'),
        sa.Column('icon', sa.String(50)),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('library_categories.id')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Library resources (books, etc.)
    op.create_table(
        'library_resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('author', sa.String(255)),
        sa.Column('isbn', sa.String(20), unique=True),
        sa.Column('publisher', sa.String(100)),
        sa.Column('publication_year', sa.Integer),
        sa.Column('edition', sa.String(50)),
        sa.Column('description', sa.Text),
        sa.Column('resource_type', sa.String(50), default='book'),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('library_categories.id')),
        sa.Column('total_copies', sa.Integer, default=1),
        sa.Column('available_copies', sa.Integer, default=1),
        sa.Column('location', sa.String(100)),
        sa.Column('cover_image_url', sa.String(500)),
        sa.Column('status', sa.String(20), default='available'),
        sa.Column('is_borrowable', sa.Boolean, default=True),
        sa.Column('max_loan_days', sa.Integer, default=14),
        sa.Column('daily_fee', sa.Float, default=0.0),
        sa.Column('language', sa.String(50)),
        sa.Column('pages', sa.Integer),
        sa.Column('tags', sa.String(500)),
        sa.Column('times_borrowed', sa.Integer, default=0),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Library loans
    op.create_table(
        'library_loans',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('library_resources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('loan_date', sa.Date, nullable=False),
        sa.Column('due_date', sa.Date, nullable=False),
        sa.Column('return_date', sa.Date),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('late_fee', sa.Float, default=0.0),
        sa.Column('is_fee_paid', sa.Boolean, default=False),
        sa.Column('condition_at_loan', sa.String(50), default='good'),
        sa.Column('condition_at_return', sa.String(50)),
        sa.Column('notes', sa.Text),
        sa.Column('renewed_count', sa.Integer, default=0),
        sa.Column('max_renewals', sa.Integer, default=2),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Library reservations
    op.create_table(
        'library_reservations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('library_resources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reservation_date', sa.Date, nullable=False),
        sa.Column('expiry_date', sa.Date, nullable=False),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('notes', sa.Text),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Library inventory
    op.create_table(
        'library_inventory',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('library_resources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('barcode', sa.String(50), unique=True, nullable=False),
        sa.Column('serial_number', sa.String(50)),
        sa.Column('status', sa.String(20), default='available'),
        sa.Column('condition', sa.String(20), default='good'),
        sa.Column('location', sa.String(100)),
        sa.Column('acquisition_date', sa.Date),
        sa.Column('acquisition_price', sa.Float),
        sa.Column('supplier', sa.String(100)),
        sa.Column('notes', sa.Text),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # ─── E-Learning Tables ─────────────────────────────────────────────────────
    
    # Courses
    op.create_table(
        'elearning_courses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('code', sa.String(20), unique=True),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('subjects.id')),
        sa.Column('level_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('levels.id')),
        sa.Column('teacher_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('classroom_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('classrooms.id')),
        sa.Column('academic_year_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('academic_years.id')),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('cover_image_url', sa.String(500)),
        sa.Column('syllabus', sa.Text),
        sa.Column('is_public', sa.Boolean, default=False),
        sa.Column('allow_discussions', sa.Boolean, default=True),
        sa.Column('allow_questions', sa.Boolean, default=True),
        sa.Column('max_students', sa.Integer, default=50),
        sa.Column('total_lessons', sa.Integer, default=0),
        sa.Column('total_duration_hours', sa.Float, default=0.0),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Lessons
    op.create_table(
        'elearning_lessons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_courses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('content', sa.Text),
        sa.Column('order_index', sa.Integer, default=0),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('duration_minutes', sa.Integer, default=30),
        sa.Column('video_url', sa.String(500)),
        sa.Column('video_duration_seconds', sa.Integer),
        sa.Column('is_preview', sa.Boolean, default=False),
        sa.Column('requires_completion', sa.Boolean, default=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Lesson resources
    op.create_table(
        'elearning_lesson_resources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_lessons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('resource_type', sa.String(50)),
        sa.Column('file_url', sa.String(500)),
        sa.Column('file_size', sa.Integer),
        sa.Column('external_url', sa.String(500)),
        sa.Column('is_downloadable', sa.Boolean, default=True),
        sa.Column('download_count', sa.Integer, default=0),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Course enrollments
    op.create_table(
        'elearning_enrollments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_courses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('enrollment_date', sa.Date),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('progress_percentage', sa.Float, default=0.0),
        sa.Column('completed_lessons', sa.Integer, default=0),
        sa.Column('last_accessed', sa.Date),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Lesson progress
    op.create_table(
        'elearning_lesson_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_lessons.id', ondelete='CASCADE'), nullable=False),
        sa.Column('enrollment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_enrollments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), default='not_started'),
        sa.Column('progress_percentage', sa.Float, default=0.0),
        sa.Column('video_position_seconds', sa.Integer, default=0),
        sa.Column('started_at', sa.Date),
        sa.Column('completed_at', sa.Date),
        sa.Column('time_spent_minutes', sa.Integer, default=0),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Homework assignments
    op.create_table(
        'elearning_homework_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_courses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_lessons.id', ondelete='SET NULL')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('instructions', sa.Text),
        sa.Column('assigned_date', sa.Date),
        sa.Column('due_date', sa.Date, nullable=False),
        sa.Column('max_score', sa.Float, default=20.0),
        sa.Column('allow_late_submission', sa.Boolean, default=False),
        sa.Column('late_penalty_percent', sa.Float, default=10.0),
        sa.Column('allow_resubmission', sa.Boolean, default=True),
        sa.Column('max_attempts', sa.Integer, default=3),
        sa.Column('attachment_urls', postgresql.JSONB, default=[]),
        sa.Column('submission_count', sa.Integer, default=0),
        sa.Column('average_score', sa.Float),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Homework submissions
    op.create_table(
        'elearning_homework_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('assignment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_homework_assignments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('content', sa.Text),
        sa.Column('attachment_urls', postgresql.JSONB, default=[]),
        sa.Column('submitted_at', sa.Date),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('attempt_number', sa.Integer, default=1),
        sa.Column('score', sa.Float),
        sa.Column('feedback', sa.Text),
        sa.Column('graded_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('graded_at', sa.Date),
        sa.Column('is_late', sa.Boolean, default=False),
        sa.Column('late_penalty_applied', sa.Float, default=0.0),
        sa.Column('final_score', sa.Float),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Course discussions
    op.create_table(
        'elearning_discussions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('course_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_courses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('lesson_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_lessons.id', ondelete='SET NULL')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_pinned', sa.Boolean, default=False),
        sa.Column('is_locked', sa.Boolean, default=False),
        sa.Column('view_count', sa.Integer, default=0),
        sa.Column('reply_count', sa.Integer, default=0),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # Discussion replies
    op.create_table(
        'elearning_discussion_replies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('discussion_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_discussions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_reply_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('elearning_discussion_replies.id')),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_answer', sa.Boolean, default=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id'), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    
    # ─── Indexes ──────────────────────────────────────────────────────────────
    
    # Library indexes
    op.create_index('ix_library_categories_tenant', 'library_categories', ['tenant_id'])
    op.create_index('ix_library_resources_tenant', 'library_resources', ['tenant_id'])
    op.create_index('ix_library_resources_category', 'library_resources', ['category_id'])
    op.create_index('ix_library_loans_user', 'library_loans', ['user_id'])
    op.create_index('ix_library_loans_resource', 'library_loans', ['resource_id'])
    op.create_index('ix_library_reservations_user', 'library_reservations', ['user_id'])
    op.create_index('ix_library_inventory_barcode', 'library_inventory', ['barcode'])
    
    # E-Learning indexes
    op.create_index('ix_elearning_courses_tenant', 'elearning_courses', ['tenant_id'])
    op.create_index('ix_elearning_courses_teacher', 'elearning_courses', ['teacher_id'])
    op.create_index('ix_elearning_lessons_course', 'elearning_lessons', ['course_id'])
    op.create_index('ix_elearning_enrollments_student', 'elearning_enrollments', ['student_id'])
    op.create_index('ix_elearning_enrollments_course', 'elearning_enrollments', ['course_id'])
    op.create_index('ix_elearning_homework_course', 'elearning_homework_assignments', ['course_id'])
    op.create_index('ix_elearning_submissions_student', 'elearning_homework_submissions', ['student_id'])
    op.create_index('ix_elearning_discussions_course', 'elearning_discussions', ['course_id'])


def downgrade() -> None:
    # Drop E-Learning tables
    op.drop_index('ix_elearning_discussions_course', 'elearning_discussions')
    op.drop_index('ix_elearning_submissions_student', 'elearning_homework_submissions')
    op.drop_index('ix_elearning_homework_course', 'elearning_homework_assignments')
    op.drop_index('ix_elearning_enrollments_course', 'elearning_enrollments')
    op.drop_index('ix_elearning_enrollments_student', 'elearning_enrollments')
    op.drop_index('ix_elearning_lessons_course', 'elearning_lessons')
    op.drop_index('ix_elearning_courses_teacher', 'elearning_courses')
    op.drop_index('ix_elearning_courses_tenant', 'elearning_courses')
    
    op.drop_table('elearning_discussion_replies')
    op.drop_table('elearning_discussions')
    op.drop_table('elearning_homework_submissions')
    op.drop_table('elearning_homework_assignments')
    op.drop_table('elearning_lesson_progress')
    op.drop_table('elearning_enrollments')
    op.drop_table('elearning_lesson_resources')
    op.drop_table('elearning_lessons')
    op.drop_table('elearning_courses')
    
    # Drop Library tables
    op.drop_index('ix_library_inventory_barcode', 'library_inventory')
    op.drop_index('ix_library_reservations_user', 'library_reservations')
    op.drop_index('ix_library_loans_resource', 'library_loans')
    op.drop_index('ix_library_loans_user', 'library_loans')
    op.drop_index('ix_library_resources_category', 'library_resources')
    op.drop_index('ix_library_resources_tenant', 'library_resources')
    op.drop_index('ix_library_categories_tenant', 'library_categories')
    
    op.drop_table('library_inventory')
    op.drop_table('library_reservations')
    op.drop_table('library_loans')
    op.drop_table('library_resources')
    op.drop_table('library_categories')
