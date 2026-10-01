"""create financial activities table

Revision ID: 001_financial_activities
Revises: 
Create Date: 2026-10-02 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_financial_activities'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'financial_activities',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('account_id', sa.String(length=64), nullable=False),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='BDT'),
        sa.Column('direction', sa.String(length=32), nullable=False),
        sa.Column('activity_type', sa.String(length=64), nullable=False),
        sa.Column('timestamp_utc', sa.DateTime(timezone=True), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=True),
        sa.Column('channel', sa.String(length=32), nullable=True),
        sa.Column('counterparty_name', sa.String(length=128), nullable=True),
        sa.Column('reference_id', sa.String(length=128), nullable=True),
        sa.Column('balance_after', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('provenance', sa.String(length=32), nullable=False, server_default='SYNTHETIC'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('ix_financial_activities_account_id', 'financial_activities', ['account_id'])
    op.create_index('ix_financial_activities_timestamp_utc', 'financial_activities', ['timestamp_utc'])


def downgrade() -> None:
    op.drop_index('ix_financial_activities_timestamp_utc', table_name='financial_activities')
    op.drop_index('ix_financial_activities_account_id', table_name='financial_activities')
    op.drop_table('financial_activities')
