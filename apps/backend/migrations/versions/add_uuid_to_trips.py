"""Add uuid and updated_at to trips

Revision ID: a1b2c3d4e5f6
Revises: 0e001039b5ba
Create Date: 2026-04-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text, inspect

revision = 'a1b2c3d4e5f6'
down_revision = '0e001039b5ba'
branch_labels = None
depends_on = None


def _column_exists(conn, table, column):
    result = conn.execute(text(f"SHOW COLUMNS FROM `{table}` LIKE '{column}'"))
    return result.fetchone() is not None

def _index_exists(conn, table, index):
    result = conn.execute(text(f"SHOW INDEX FROM `{table}` WHERE Key_name = '{index}'"))
    return result.fetchone() is not None


def upgrade():
    conn = op.get_bind()

    # 컬럼이 없을 때만 추가 (이미 있으면 스킵)
    if not _column_exists(conn, 'trips', 'uuid'):
        op.add_column('trips', sa.Column('uuid', sa.String(36), nullable=True))

    if not _column_exists(conn, 'trips', 'updated_at'):
        op.add_column('trips', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # 기존 row에 UUID 채우기
    conn.execute(text("UPDATE trips SET uuid = UUID() WHERE uuid IS NULL"))

    # NOT NULL 설정
    conn.execute(text("ALTER TABLE trips MODIFY COLUMN uuid VARCHAR(36) NOT NULL"))

    # unique index (없을 때만)
    if not _index_exists(conn, 'trips', 'uq_trips_uuid'):
        conn.execute(text("ALTER TABLE trips ADD CONSTRAINT uq_trips_uuid UNIQUE (uuid)"))


def downgrade():
    conn = op.get_bind()
    if _index_exists(conn, 'trips', 'uq_trips_uuid'):
        conn.execute(text("ALTER TABLE trips DROP INDEX uq_trips_uuid"))
    if _column_exists(conn, 'trips', 'uuid'):
        op.drop_column('trips', 'uuid')
    if _column_exists(conn, 'trips', 'updated_at'):
        op.drop_column('trips', 'updated_at')
