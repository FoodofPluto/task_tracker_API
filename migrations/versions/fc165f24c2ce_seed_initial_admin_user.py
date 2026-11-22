"""seed initial admin user

Revision ID: fc165f24c2ce
Revises: 44828115949e
Create Date: 2026-11-22 15:24:36.663487

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import sqlalchemy as sa
from alembic import op
from werkzeug.security import generate_password_hash

# revision identifiers, used by Alembic.
revision = 'fc165f24c2ce'
down_revision = '44828115949e'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    user_table = sa.table(
        "user",
        sa.column("id", sa.Integer),
        sa.column("username", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("role", sa.String),
        sa.column("created_at", sa.DateTime),
    )

    # Check if an admin user already exists so the migration is safe to re-run
    existing = bind.execute(
        sa.select(user_table.c.id).where(user_table.c.username == "admin")
    ).first()

    if existing is None:
        op.bulk_insert(
            user_table,
            [
                {
                    "username": "admin",
                    "password_hash": generate_password_hash("AdminPass123!"),
                    "role": "admin",
                    "created_at": datetime.utcnow(),
                }
            ],
        )


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("DELETE FROM user WHERE username = 'admin'"))