"""add image_url column to products

Revision ID: 0007
Revises: 0006
Create Date: 2026-09-16
"""
from alembic import op
import sqlalchemy as sa

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'products',
        sa.Column('image_url', sa.String(length=500), nullable=True),
    )


def downgrade():
    op.drop_column('products', 'image_url')