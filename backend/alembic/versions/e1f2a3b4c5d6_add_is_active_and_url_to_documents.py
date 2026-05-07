"""add is_active and url to documents

Revision ID: e1f2a3b4c5d6
Revises: d4e5f6a7b8c9
Create Date: 2026-05-07

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('documents', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('documents', sa.Column('url', sa.String(2048), nullable=True))


def downgrade() -> None:
    op.drop_column('documents', 'url')
    op.drop_column('documents', 'is_active')
