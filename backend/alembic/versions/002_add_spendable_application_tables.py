"""add spendable application tables (user_accounts, spendable_snapshots)

Revision ID: 002_application_tables
Revises: 001_financial_activities
Create Date: 2026-10-02 23:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '002_application_tables'
down_revision: Union[str, None] = '001_financial_activities'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create user_accounts table
    op.create_table(
        'user_accounts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('account_id', sa.String(length=64), nullable=False),
        sa.Column('display_name', sa.String(length=128), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='BDT'),
        sa.Column('current_balance', sa.Numeric(precision=14, scale=2), nullable=False, server_default='0.00'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_user_accounts_account_id', 'user_accounts', ['account_id'], unique=True)

    # 2. Create spendable_snapshots table
    op.create_table(
        'spendable_snapshots',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('account_id', sa.String(length=64), nullable=False),
        sa.Column('snapshot_time', sa.String(length=32), nullable=False),
        sa.Column('current_balance', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('spendable_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('protected_amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('planning_horizon_days', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('expected_inflow', sa.Numeric(precision=14, scale=2), nullable=False, server_default='0.00'),
        sa.Column('expected_outflow', sa.Numeric(precision=14, scale=2), nullable=False, server_default='0.00'),
        sa.Column('upcoming_commitments', sa.Numeric(precision=14, scale=2), nullable=False, server_default='0.00'),
        sa.Column('forecasted_minimum_balance', sa.Numeric(precision=14, scale=2), nullable=False, server_default='0.00'),
        sa.Column('safety_reserve', sa.Numeric(precision=14, scale=2), nullable=False, server_default='0.00'),
        sa.Column('liquidity_state', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('ix_spendable_snapshots_account_id', 'spendable_snapshots', ['account_id'])
    op.create_index('ix_spendable_snapshots_snapshot_time', 'spendable_snapshots', ['snapshot_time'])


def downgrade() -> None:
    op.drop_index('ix_spendable_snapshots_snapshot_time', table_name='spendable_snapshots')
    op.drop_index('ix_spendable_snapshots_account_id', table_name='spendable_snapshots')
    op.drop_table('spendable_snapshots')

    op.drop_index('ix_user_accounts_account_id', table_name='user_accounts')
    op.drop_table('user_accounts')
