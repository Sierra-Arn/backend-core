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

# packages/shared/src/postgres_lib/models/user_role.py
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, CreatedAtMixin


class UserRole(Base, CreatedAtMixin):
    """
    Association table representing the many-to-many relationship
    between users and roles.

    Attributes
    ----------
    user_id : Mapped[int]
        Foreign key referencing the user who holds this role.
        Cascades deletion when the referenced user is removed.
    role_id : Mapped[int]
        Foreign key referencing the assigned role.
        Cascades deletion when the referenced role is removed.

    Notes
    -----
    (user_id, role_id) is declared as a composite primary key, which causes
    PostgreSQL to automatically create a unique B-tree index on the column pair.
    This index serves two purposes: first, it enforces uniqueness by rejecting
    any insertion that would assign the same role to the same user twice,
    guaranteeing that each (user, role) combination exists at most once in the
    table; second, it accelerates permission checks — every authorization
    request filters on user_id, and because it is the leading column of the
    composite index, PostgreSQL satisfies that query with an index range scan
    rather than a full table scan.

    This model is never instantiated directly in application code. SQLAlchemy
    references it by table name via secondary="user_roles" on User.roles and
    handles all insertion and deletion automatically when the roles collection
    on a User instance is modified. As a pure association table it has no
    independent identity — it exists solely to link users to roles. For this
    reason it has no dedicated repository; all operations that write to this
    table are handled through UserRepository, which owns the user-role
    assignment lifecycle.
    """

    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Foreign key to the user who holds this role; leading column of the composite PK index",
    )
    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Foreign key to the assigned role; trailing column of the composite PK index",
    )