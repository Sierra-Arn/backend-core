"""Seed roles and admin

Revision ID: 54db352ab472
Revises: d167769d594a
Create Date: 2026-06-17 13:51:27.965329

"""
import os
from datetime import datetime, timezone
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from dotenv import load_dotenv
from sqlalchemy.sql import column, table
from sqlalchemy.dialects.postgresql import ENUM
from postgres_lib import PermissionEnum
from password_lib import PasswordService

load_dotenv()

# revision identifiers, used by Alembic.
revision: str = '54db352ab472'
down_revision: Union[str, Sequence[str], None] = 'd167769d594a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL")
_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD")


def upgrade() -> None:
    """Seed default roles, permissions, and admin user."""

    roles_table = table(
        "roles",
        column("name", sa.String),
        column("created_at", sa.DateTime(timezone=True)),
    )
    role_permissions_table = table(
        "role_permissions",
        column("role_id", sa.Integer),
        column("permission", ENUM(name="permission", create_type=False)),
        column("created_at", sa.DateTime(timezone=True)),
    )
    users_table = table(
        "users",
        column("email", sa.String),
        column("hashed_password", sa.String),
        column("is_verified", sa.Boolean),
        column("created_at", sa.DateTime(timezone=True)),
    )
    user_roles_table = table(
        "user_roles",
        column("user_id", sa.Integer),
        column("role_id", sa.Integer),
        column("created_at", sa.DateTime(timezone=True)),
    )

    now = datetime.now(timezone.utc)
    bind = op.get_bind()

    bind.execute(roles_table.insert().values([
        {"name": "user", "created_at": now},
        {"name": "admin", "created_at": now},
    ]))

    admin_role_id = bind.execute(
        sa.text("SELECT id FROM roles WHERE name = 'admin'")
    ).scalar_one()

    bind.execute(role_permissions_table.insert().values([
        {"role_id": admin_role_id, "permission": p.value, "created_at": now}
        for p in PermissionEnum
    ]))

    hashed_password = PasswordService.hash(_ADMIN_PASSWORD)

    bind.execute(users_table.insert().values([
        {
            "email": _ADMIN_EMAIL,
            "hashed_password": hashed_password,
            "is_verified": True,
            "created_at": now,
        }
    ]))

    admin_user_id = bind.execute(
        sa.text(f"SELECT id FROM users WHERE email = '{_ADMIN_EMAIL}'")
    ).scalar_one()

    bind.execute(user_roles_table.insert().values([
        {"user_id": admin_user_id, "role_id": admin_role_id, "created_at": now}
    ]))


def downgrade() -> None:
    """Remove seeded roles, permissions, and admin user."""
    bind = op.get_bind()
    bind.execute(sa.text(f"DELETE FROM users WHERE email = '{_ADMIN_EMAIL}'"))
    bind.execute(sa.text("DELETE FROM roles WHERE name IN ('user', 'admin')"))