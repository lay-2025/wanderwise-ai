"""add user_id to sessions and source info to documents

Revision ID: d4e5f6a7b8c9
Revises: 61f148cbd169
Create Date: 2026-04-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = '61f148cbd169'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 開発環境用：user_id の NOT NULL 追加前に既存データを削除
    op.execute("TRUNCATE TABLE documents CASCADE")
    op.execute("TRUNCATE TABLE sessions CASCADE")

    # sessions.user_id (NOT NULL)
    op.add_column('sessions',
        sa.Column('user_id', UUID(as_uuid=True), nullable=False)
    )
    op.create_foreign_key(
        'fk_sessions_user_id', 'sessions', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )

    # documents.created_by_user_id (NULLABLE)
    op.add_column('documents',
        sa.Column('created_by_user_id', UUID(as_uuid=True), nullable=True)
    )
    op.create_foreign_key(
        'fk_documents_created_by_user_id', 'documents', 'users',
        ['created_by_user_id'], ['id'], ondelete='SET NULL'
    )

    # documents.source_session_id (NULLABLE)
    op.add_column('documents',
        sa.Column('source_session_id', UUID(as_uuid=True), nullable=True)
    )
    op.create_foreign_key(
        'fk_documents_source_session_id', 'documents', 'sessions',
        ['source_session_id'], ['id'], ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_documents_source_session_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'source_session_id')
    op.drop_constraint('fk_documents_created_by_user_id', 'documents', type_='foreignkey')
    op.drop_column('documents', 'created_by_user_id')
    op.drop_constraint('fk_sessions_user_id', 'sessions', type_='foreignkey')
    op.drop_column('sessions', 'user_id')
