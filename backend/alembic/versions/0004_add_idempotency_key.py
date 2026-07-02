"""add idempotency_key to interactions

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-29
"""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'interactions',
        sa.Column('idempotency_key', sa.String(length=255), nullable=True),
    )
    op.create_index('ix_interactions_idempotency_key', 'interactions', ['idempotency_key'], unique=True)


def downgrade():
    op.drop_index('ix_interactions_idempotency_key', table_name='interactions')
    op.drop_column('interactions', 'idempotency_key')
