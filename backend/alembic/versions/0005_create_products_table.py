"""create products table

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-03
"""
from alembic import op
import sqlalchemy as sa

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(length=200), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('precio', sa.Float(), nullable=False, server_default=sa.text('0.0')),
        sa.Column('stock', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('categoria', sa.String(length=100), nullable=True),
        sa.Column('activo', sa.Boolean(), server_default=sa.text('1'), nullable=False),
        sa.Column('fecha_registro', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table('products')
