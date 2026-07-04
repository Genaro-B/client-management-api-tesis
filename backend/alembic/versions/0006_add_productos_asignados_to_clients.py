"""add productos_asignados JSON column to clients

Revision ID: 0006
Revises: 0005
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa

revision = '0006'
down_revision = '0005'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'clients',
        sa.Column('productos_asignados', sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
    )


def downgrade():
    op.drop_column('clients', 'productos_asignados')
