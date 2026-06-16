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

# app/shared/postgres/db/models/user_role.py
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
    role_id : Mapped[int]
        Foreign key referencing the assigned role.

    Notes
    -----
    ``(user_id, role_id)`` is declared as a composite primary key, which causes
    PostgreSQL to automatically create a unique B-tree index on the column pair.
    This index serves two purposes:

    1. **Uniqueness enforcement.** PostgreSQL rejects any insertion that would
       assign the same role to the same user twice, guaranteeing that each
       (user, role) combination exists at most once in the table.

    2. **Join performance.** Every permission check fetches all roles for a given
       user by filtering on ``user_id``. Because ``user_id`` is the leading column
       in the composite index, PostgreSQL can satisfy that query with an index
       range scan instead of a full table scan, keeping authorization fast
       regardless of how many assignments are stored.
    """

    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Foreign key to the user who holds this role; leading column of the composite PK",
    )

    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        comment="Foreign key to the assigned role; trailing column of the composite PK",
    )