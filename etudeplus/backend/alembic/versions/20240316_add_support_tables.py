"""Add support tables for GROUP_AGENT

Revision ID: support_tables
Revises: 
Create Date: 2024-03-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'support_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create support_tickets table
    op.create_table(
        'support_tickets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('status', sa.Enum('open', 'in_progress', 'waiting', 'resolved', 'closed', name='ticket_status'), default='open'),
        sa.Column('priority', sa.Enum('low', 'medium', 'high', 'critical', name='ticket_priority'), default='medium'),
        sa.Column('category', sa.Enum('technical', 'account', 'billing', 'academic', 'feature_request', 'bug_report', 'other', name='ticket_category'), default='other'),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('assigned_to_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('first_response_at', sa.DateTime, nullable=True),
        sa.Column('resolved_at', sa.DateTime, nullable=True),
        sa.Column('closed_at', sa.DateTime, nullable=True),
        sa.Column('sla_due_at', sa.DateTime, nullable=True),
        sa.Column('sla_breached', sa.Integer, default=0),
        sa.Column('response_time_minutes', sa.Integer, nullable=True),
        sa.Column('resolution_time_minutes', sa.Integer, nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create ticket_comments table
    op.create_table(
        'ticket_comments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ticket_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('support_tickets.id'), nullable=False),
        sa.Column('author_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('is_internal', sa.Integer, default=0),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create maintenance_logs table
    op.create_table(
        'maintenance_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('maintenance_type', sa.String(50)),
        sa.Column('status', sa.String(50), default='scheduled'),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('completed_at', sa.DateTime, nullable=True),
        sa.Column('affected_services', sa.Text, nullable=True),
        sa.Column('performed_by_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes
    op.create_index('ix_support_tickets_status', 'support_tickets', ['status'])
    op.create_index('ix_support_tickets_priority', 'support_tickets', ['priority'])
    op.create_index('ix_support_tickets_tenant_id', 'support_tickets', ['tenant_id'])
    op.create_index('ix_support_tickets_assigned_to', 'support_tickets', ['assigned_to_id'])
    op.create_index('ix_ticket_comments_ticket_id', 'ticket_comments', ['ticket_id'])
    op.create_index('ix_maintenance_logs_status', 'maintenance_logs', ['status'])


def downgrade():
    op.drop_index('ix_maintenance_logs_status', 'maintenance_logs')
    op.drop_index('ix_ticket_comments_ticket_id', 'ticket_comments')
    op.drop_index('ix_support_tickets_assigned_to', 'support_tickets')
    op.drop_index('ix_support_tickets_tenant_id', 'support_tickets')
    op.drop_index('ix_support_tickets_priority', 'support_tickets')
    op.drop_index('ix_support_tickets_status', 'support_tickets')
    
    op.drop_table('maintenance_logs')
    op.drop_table('ticket_comments')
    op.drop_table('support_tickets')
    
    op.execute('DROP TYPE IF EXISTS ticket_status')
    op.execute('DROP TYPE IF EXISTS ticket_priority')
    op.execute('DROP TYPE IF EXISTS ticket_category')
