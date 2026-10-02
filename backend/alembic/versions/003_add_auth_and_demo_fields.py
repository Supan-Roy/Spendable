"""add auth and demo fields to user_accounts table

Revision ID: 003_auth_demo_fields
Revises: 002_application_tables
Create Date: 2026-10-03 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '003_auth_demo_fields'
down_revision: Union[str, None] = '002_application_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user_accounts', sa.Column('username', sa.String(length=64), nullable=True))
    op.add_column('user_accounts', sa.Column('password_hash', sa.String(length=255), nullable=True))
    op.add_column('user_accounts', sa.Column('is_demo_account', sa.Boolean(), nullable=False, server_default=sa.text('0')))
    op.create_index('ix_user_accounts_username', 'user_accounts', ['username'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_user_accounts_username', table_name='user_accounts')
    op.drop_column('user_accounts', 'is_demo_account')
    op.drop_column('user_accounts', 'password_hash')
    op.drop_column('user_accounts', 'username')
