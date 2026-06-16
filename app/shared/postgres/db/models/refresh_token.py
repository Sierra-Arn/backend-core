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

# app/shared/postgres/db/models/refresh_token.py
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, IdMixin, CreatedAtMixin

if TYPE_CHECKING:
    from .user import User


class RefreshToken(Base, IdMixin, CreatedAtMixin):
    """
    Database model representing an opaque refresh token issued to a user.

    Attributes
    ----------
    user_id : Mapped[int]
        Foreign key referencing the user who owns this token.
        Deleted automatically when the user record is removed (CASCADE).
    token : Mapped[str]
        Cryptographically random opaque string that serves as the token value.
        Never decoded or interpreted by the server — looked up by exact match only.
    expires_at : Mapped[datetime]
        UTC timestamp after which the token is no longer valid.
        Must always be compared against ``datetime.now(timezone.utc)``.
    user : Mapped["User"]
        ORM relationship to the owning user record.

    Notes
    -----
    Two columns carry indexes that serve distinct purposes:

    ``token`` is declared with ``unique=True``, which causes PostgreSQL to
    automatically create a unique B-tree index on the column. This index
    serves two purposes:

    1. **Uniqueness enforcement.** PostgreSQL rejects any insertion that would
       produce a duplicate token value, guaranteeing that each issued token
       is globally unique and cannot be replayed via a colliding value.

    2. **Refresh request performance.** Every token refresh fetches the record
       by raw token value. Without the index, each request would require a
       full table scan. The B-tree index reduces each lookup to O(log n).

    ``expires_at`` carries an explicit B-tree index via ``index=True``.
    Its sole purpose is to support efficient cleanup queries that purge 
    expired records from the table.

    Without the index, such a query would scan every row in the table.
    With it, PostgreSQL can jump directly to the relevant range, keeping
    cleanup fast even as the table accumulates a large number of records.
    """

    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Owner of this token; cascades deletion from users table",
    )

    token: Mapped[str] = mapped_column(
        String(512),
        unique=True,
        nullable=False,
        comment="Opaque random string; looked up by exact match on every refresh request",
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="UTC expiry timestamp; token is invalid at or after this moment",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens",
    )