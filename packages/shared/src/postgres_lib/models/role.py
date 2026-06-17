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

# packages/shared/src/postgres_lib/models/role.py
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import IdModel, CreatedAtMixin

if TYPE_CHECKING:
    from .role_permission import RolePermission


class Role(IdModel, CreatedAtMixin):
    """
    Represents a named role that can be assigned to users.

    Attributes
    ----------
    name : Mapped[str]
        Unique human-readable identifier for the role. Used during RBAC
        checks to determine what actions a user may perform.
    permissions : Mapped[list[RolePermission]]
        Collection of permissions assigned to this role, routed through
        the role_permissions association table. Deleted automatically
        when the role is removed via cascade. Never loaded implicitly —
        always controlled via selectinload or noload at the query level
        to avoid N+1 patterns.

    Notes
    -----
    name is declared with unique=True, which causes PostgreSQL to automatically
    create a unique B-tree index on the column. This index serves two purposes:
    first, it enforces uniqueness by rejecting any insertion that would produce
    a duplicate role name, guaranteeing that each role exists exactly once in
    the system regardless of how many users reference it; second, it accelerates
    RBAC checks — permission lookups fetch roles by name, and the B-tree index
    reduces each such lookup from a full table scan to O(log n).
    """

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        comment="Unique role name used in RBAC checks",
    )
    # No back_populates on Role.users — that direction is never queried,
    # so there is no reason to maintain a reverse attribute here.
    # permissions uses cascade="all, delete-orphan" so that removing a Role
    # automatically deletes all associated RolePermission rows without
    # requiring a separate DELETE query in application code.
    permissions: Mapped[list["RolePermission"]] = relationship(
        cascade="all, delete-orphan",
    )