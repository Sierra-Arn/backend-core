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

# packages/shared/src/postgres_lib/models/user.py
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import IdModel, CreatedAtMixin

if TYPE_CHECKING:
    from .role import Role


class User(IdModel, CreatedAtMixin):
    """
    Represents a registered application user.

    Attributes
    ----------
    email : Mapped[str]
        Unique email address used for authentication and communication.
    hashed_password : Mapped[str]
        Bcrypt hash of the user's password. The plaintext password is never
        stored or logged anywhere.
    is_verified : Mapped[bool]
        Whether the user has verified their identity. Defaults to False at
        registration.
    bio : Mapped[str | None]
        Optional free-form biographical text provided by the user. None
        indicates the user has not filled in their profile.
    roles : Mapped[list[Role]]
        Collection of roles assigned to this user. Never loaded implicitly —
        always controlled via selectinload or noload at the query level to
        avoid N+1 patterns.

    Notes
    -----
    email is declared with unique=True, which causes PostgreSQL to automatically
    create a unique B-tree index on the column. This index serves two purposes:
    first, it enforces uniqueness by rejecting any insertion or update that would
    produce a duplicate address, guaranteeing each address belongs to exactly one
    account; second, it accelerates login lookups — every authentication attempt
    fetches the user record by email, and the B-tree index reduces each such
    lookup from a full table scan to O(log n).
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique email address; max 254 characters per RFC 5321",
    )
    hashed_password: Mapped[str] = mapped_column(
        String(60),
        nullable=False,
        comment="Bcrypt hash of the user's password; bcrypt output is always exactly 60 characters",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="True once the user confirms their email address",
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        comment="Optional free-form biographical text provided by the user",
    )
    # secondary="user_roles" instructs SQLAlchemy to route the relationship
    # through the user_roles association table, enabling direct many-to-many
    # access between User and Role without manually traversing UserRole objects.
    # No back_populates on Role.users — that direction is never queried,
    # so there is no reason to maintain a reverse attribute on Role.
    # This is not a database construct — no JOIN happens here at definition time.
    # The JOIN is issued only when the repository explicitly requests it via
    # selectinload(User.roles), which emits a single SELECT ... WHERE user_id IN (...)
    # for the entire batch rather than one query per user.
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="user_roles",
    )