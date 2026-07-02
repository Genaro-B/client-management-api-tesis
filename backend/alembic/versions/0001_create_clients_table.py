"""create clients table

Revision ID: 0001
Revises: 
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'clients',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('apellido', sa.String(length=100), nullable=False),
        sa.Column('telefono', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('fecha_registro', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('activo', sa.Boolean(), server_default=sa.text('1'), nullable=False),
    )
    op.create_index('ix_clients_email_unique', 'clients', ['email'], unique=True)

def downgrade():
    op.drop_index('ix_clients_email_unique', table_name='clients')
    op.drop_table('clients')
