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

# app/shared/postgres/db/models/user.py
from typing import TYPE_CHECKING
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, IdMixin, CreatedAtMixin, UpdatedAtMixin


if TYPE_CHECKING:
    from .role import Role
    from .refresh_token import RefreshToken


class User(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    """
    Represents a registered application user.

    Attributes
    ----------
    email : Mapped[str]
        Unique email address used for authentication and communication.
    hashed_password : Mapped[str]
        Bcrypt hash of the user's password.
        The plaintext password is never stored or logged anywhere.
    is_verified : Mapped[bool]
        Whether the user has verified their identity.
        Defaults to ``False`` at registration.
    bio : Mapped[str | None]
        Optional free-form biographical text provided by the user.
        ``None`` indicates the user has not filled in their profile.
    roles : Mapped[list[Role]]
        Collection of roles assigned to this user, loaded via the
        ``user_roles`` association table. Used by the RBAC layer to
        determine what actions the user is authorized to perform.
    refresh_tokens : Mapped[list[RefreshToken]]
        Collection of all refresh tokens issued to this user.

    Notes
    -----
    ``email`` is declared with ``unique=True``, which causes PostgreSQL to
    automatically create a unique B-tree index on the column. This index
    serves two purposes:

    1. **Uniqueness enforcement.** PostgreSQL rejects any insertion or update
       that would produce a duplicate email address, guaranteeing that each
       address belongs to exactly one account.

    2. **Login lookup performance.** Every authentication attempt fetches the
       user record by email. Without the index, each login would require a
       full table scan. The B-tree index reduces each lookup to O(log n),
       keeping authentication fast regardless of how many users are registered.
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

    # Roles are loaded lazily by default. For operations that always need
    # role data (e.g., token issuance, permission checks), prefer
    # explicitly joining roles in the query rather than relying on
    # lazy loading to avoid N+1 query patterns.
    roles: Mapped[list["Role"]] = relationship(
        "Role",

        # ``secondary="user_roles"`` instructs SQLAlchemy to route the relationship
        # through the ``user_roles`` association table, enabling direct many-to-many
        # access between ``User`` and ``Role`` without manually traversing ``UserRole``
        # objects. SQLAlchemy resolves the table by name from the shared metadata,
        # so no explicit import of ``UserRole`` is required here.
        secondary="user_roles",
        back_populates="users",
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
    )