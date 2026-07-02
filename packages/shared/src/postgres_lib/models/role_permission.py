# Copyright (c) 2026 Ilya Snegov (aka Sierra Arn)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# packages/shared/src/postgres_lib/models/role_permission.py
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, CreatedAtMixin
from .types import PermissionSQL, PermissionEnum


class RolePermission(Base, CreatedAtMixin):
    """
    Association table linking roles to their assigned permissions.

    Each record represents a single permission granted to a role.
    A role may hold multiple permissions; each (role_id, permission)
    pair is unique, preventing duplicate assignments.

    Attributes
    ----------
    id : Mapped[int]
        Surrogate primary key. Used instead of a composite primary key
        to simplify foreign key references from other tables if needed.
    role_id : Mapped[int]
        Foreign key referencing the role this permission belongs to.
        Cascades deletion when the referenced role is removed.
    permission : Mapped[PermissionEnum]
        The permission value from the Permission enum, stored as a
        native PostgreSQL enum type via PermissionSQL.

    Notes
    -----
    The composite unique constraint on (role_id, permission) enforces
    at the database level that the same permission cannot be assigned
    to the same role twice, regardless of application-layer validation.

    As a pure association table it has no independent identity — it exists
    solely to express which permissions belong to a role. For this reason
    it has no dedicated repository; all operations that write to this table
    are handled through RoleRepository, which owns the role-permission
    assignment lifecycle.
    """

    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "permission",
            name="uq_role_permissions_role_permission",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        comment="Surrogate primary key",
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key to the owning role; cascades deletion from roles table",
    )
    permission: Mapped[PermissionEnum] = mapped_column(
        PermissionSQL,
        nullable=False,
        comment="Permission value stored as a native PostgreSQL enum",
    )