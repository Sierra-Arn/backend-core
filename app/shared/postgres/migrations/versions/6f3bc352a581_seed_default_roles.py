"""Seed default roles and assign permissions to admin role

Revision ID: 6f3bc352a581
Revises: 58dddaf607be
Create Date: 2026-03-12 16:38:56.085219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '6f3bc352a581'
down_revision: Union[str, Sequence[str], None] = '58dddaf607be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


roles_table = table(
    "roles",
    column("id", sa.Integer),
    column("name", sa.String),
)
 
role_permissions_table = table(
    "role_permissions",
    column("role_id", sa.Integer),
    column("permission", sa.String),
)


def upgrade() -> None:
    """Upgrade schema."""

    # Insert default roles.
    op.bulk_insert(roles_table, [
        {"name": "user"},
        {"name": "admin"},
    ])
 
    # Resolve inserted role IDs for use in role_permissions.
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id, name FROM roles WHERE name IN ('user', 'admin')"))
    role_ids = {row.name: row.id for row in result}
 
    # Assign all permissions to the admin role.
    admin_permissions = [
        "users:get_all",
        "users:manage_roles",
        "roles:create",
        "roles:manage_permissions",
    ]
    op.bulk_insert(role_permissions_table, [
        {"role_id": role_ids["admin"], "permission": perm}
        for perm in admin_permissions
    ])
 
    # The user role has no elevated permissions by default.
    # Permissions can be assigned later via the admin UI.


def downgrade() -> None:
    """Downgrade schema."""

    # role_permissions are deleted automatically via ON DELETE CASCADE.
    op.execute("DELETE FROM roles WHERE name IN ('user', 'admin')")