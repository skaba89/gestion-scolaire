"""add support tickets tables

Revision ID: 20260315_support
Revises:
Create Date: 2025-03-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY, ENUM

# revision identifiers, used by Alembic.
revision = '20260315_support'
down_revision = None  # Will be set when migration is applied
branch_labels = None
depends_on = None


def upgrade():
    # Create enums
    ticket_status = ENUM('open', 'in_progress', 'pending', 'resolved', 'closed', 'reopened', name='ticket_status', create_type=False)
    ticket_priority = ENUM('low', 'medium', 'high', 'critical', 'urgent', name='ticket_priority', create_type=False)
    ticket_category = ENUM('technical', 'maintenance', 'software', 'hardware', 'network', 'user_support', 'academic', 'administrative', 'other', name='ticket_category', create_type=False)

    # Create enums if they don't exist
    op.execute("CREATE TYPE ticket_status AS ENUM ('open', 'in_progress', 'pending', 'resolved', 'closed', 'reopened')")
    op.execute("CREATE TYPE ticket_priority AS ENUM ('low', 'medium', 'high', 'critical', 'urgent')")
    op.execute("CREATE TYPE ticket_category AS ENUM ('technical', 'maintenance', 'software', 'hardware', 'network', 'user_support', 'academic', 'administrative', 'other')")

    # Create support_categories table
    op.create_table(
        'support_categories',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(20), nullable=True),
        sa.Column('default_priority', ticket_priority, nullable=False, server_default='medium'),
        sa.Column('sla_response_hours', sa.Integer, server_default='24'),
        sa.Column('sla_resolution_hours', sa.Integer, server_default='72'),
        sa.Column('auto_assign_to', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('auto_assign_department', sa.String(100), nullable=True),
        sa.Column('requires_approval', sa.Boolean, server_default='false'),
        sa.Column('approval_workflow_id', UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('sort_order', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )

    # Create support_tickets table
    op.create_table(
        'support_tickets',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('ticket_number', sa.String(50), unique=True, nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', ticket_category, nullable=False, server_default='other'),
        sa.Column('priority', ticket_priority, nullable=False, server_default='medium'),
        sa.Column('status', ticket_status, nullable=False, server_default='open', index=True),
        sa.Column('reported_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('assigned_to', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('assigned_department', sa.String(100), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('asset_id', sa.String(100), nullable=True),
        sa.Column('asset_name', sa.String(255), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text, nullable=True),
        sa.Column('resolution_time_minutes', sa.Integer, nullable=True),
        sa.Column('tags', ARRAY(sa.String), nullable=True, server_default='{}'),
        sa.Column('attachments', sa.JSON, nullable=True, server_default='[]'),
        sa.Column('custom_fields', sa.JSON, nullable=True, server_default='{}'),
        sa.Column('sla_due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sla_breached', sa.Boolean, server_default='false'),
        sa.Column('satisfaction_rating', sa.Integer, nullable=True),
        sa.Column('feedback_comment', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), index=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )

    # Create ticket_comments table
    op.create_table(
        'ticket_comments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('ticket_id', UUID(as_uuid=True), sa.ForeignKey('support_tickets.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('author_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('is_internal', sa.Boolean, server_default='false'),
        sa.Column('attachments', sa.JSON, nullable=True, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )

    # Create ticket_history table
    op.create_table(
        'ticket_history',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('ticket_id', UUID(as_uuid=True), sa.ForeignKey('support_tickets.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('changed_by', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('field_name', sa.String(100), nullable=False),
        sa.Column('old_value', sa.Text, nullable=True),
        sa.Column('new_value', sa.Text, nullable=True),
        sa.Column('change_reason', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
    )

    # Create support_knowledge_base table
    op.create_table(
        'support_knowledge_base',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('summary', sa.Text, nullable=True),
        sa.Column('category_id', UUID(as_uuid=True), sa.ForeignKey('support_categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tags', ARRAY(sa.String), nullable=True, server_default='{}'),
        sa.Column('is_published', sa.Boolean, server_default='false'),
        sa.Column('is_internal', sa.Boolean, server_default='false'),
        sa.Column('view_count', sa.Integer, server_default='0'),
        sa.Column('helpful_count', sa.Integer, server_default='0'),
        sa.Column('not_helpful_count', sa.Integer, server_default='0'),
        sa.Column('author_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
    )

    # Create indexes
    op.create_index('ix_support_tickets_status_priority', 'support_tickets', ['status', 'priority'])
    op.create_index('ix_support_tickets_assigned_created', 'support_tickets', ['assigned_to', 'created_at'])
    op.create_index('ix_support_tickets_sla_breached', 'support_tickets', ['sla_breached'])


def downgrade():
    op.drop_table('support_knowledge_base')
    op.drop_table('ticket_history')
    op.drop_table('ticket_comments')
    op.drop_table('support_tickets')
    op.drop_table('support_categories')

    op.execute('DROP TYPE IF EXISTS ticket_status')
    op.execute('DROP TYPE IF EXISTS ticket_priority')
    op.execute('DROP TYPE IF EXISTS ticket_category')
