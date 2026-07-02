"""add role column to clients, set id=8 as admin

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        'clients',
        sa.Column('role', sa.String(length=20), server_default=sa.text("'user'"), nullable=False),
    )
    # Set client ID 8 as admin
    op.execute("UPDATE clients SET role = 'admin' WHERE id = 8")

def downgrade():
    op.drop_column('clients', 'role')
