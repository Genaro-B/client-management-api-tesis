"""create interactions table

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'interactions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('clientId', sa.Integer(), sa.ForeignKey('clients.id'), nullable=True),
        sa.Column('user', sa.String(length=255), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('payload', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(length=255), nullable=True),
        sa.Column('result', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )
    op.create_index('ix_interactions_client_id', 'interactions', ['clientId'])
    op.create_index('ix_interactions_timestamp', 'interactions', ['timestamp'])


def downgrade():
    op.drop_index('ix_interactions_timestamp', table_name='interactions')
    op.drop_index('ix_interactions_client_id', table_name='interactions')
    op.drop_table('interactions')
