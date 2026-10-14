"""create sales tables and telegram identity

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-09
"""
from alembic import op
import sqlalchemy as sa

revision = '0008'
down_revision = '0007'
branch_labels = None
depends_on = None


def upgrade():
    # --- sales ---
    op.create_table(
        'sales',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('cliente_id', sa.Integer(), sa.ForeignKey('clients.id'), nullable=False),
        sa.Column('fecha', sa.DateTime(timezone=True),
                  server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('total', sa.Float(), nullable=False, server_default='0'),
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='PENDIENTE'),
        sa.Column('idempotency_key', sa.String(length=255), nullable=True),
        sa.Column('confirmado_por', sa.Integer(), sa.ForeignKey('clients.id'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_sales_cliente_id', 'sales', ['cliente_id'])
    op.create_index('ix_sales_estado', 'sales', ['estado'])
    op.create_index('ix_sales_fecha', 'sales', ['fecha'])
    op.create_index('ix_sales_idempotency_key', 'sales', ['idempotency_key'], unique=True)

    # --- sale_items ---
    op.create_table(
        'sale_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sale_id', sa.Integer(),
                  sa.ForeignKey('sales.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('precio_unitario', sa.Float(), nullable=False),
    )
    op.create_index('ix_sale_items_sale_id', 'sale_items', ['sale_id'])
    op.create_index('ix_sale_items_product_id', 'sale_items', ['product_id'])

    # --- identidad durable del bot ---
    op.add_column(
        'clients',
        sa.Column('telegram_user_id', sa.String(length=32), nullable=True),
    )
    op.create_index('ix_clients_telegram_user_id', 'clients', ['telegram_user_id'], unique=True)


def downgrade():
    op.drop_index('ix_clients_telegram_user_id', table_name='clients')
    op.drop_column('clients', 'telegram_user_id')

    op.drop_index('ix_sale_items_product_id', table_name='sale_items')
    op.drop_index('ix_sale_items_sale_id', table_name='sale_items')
    op.drop_table('sale_items')

    op.drop_index('ix_sales_idempotency_key', table_name='sales')
    op.drop_index('ix_sales_fecha', table_name='sales')
    op.drop_index('ix_sales_estado', table_name='sales')
    op.drop_index('ix_sales_cliente_id', table_name='sales')
    op.drop_table('sales')
