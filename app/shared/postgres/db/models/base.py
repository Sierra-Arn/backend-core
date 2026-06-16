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

# app/shared/postgres/db/models/base.py
from datetime import datetime
from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Central registry for all ORM models in the application.

    Every class that inherits from Base is automatically registered in
    Base.metadata — a collection of all Table objects in the schema.
    This metadata is later used to create or drop tables.

    Without a shared Base, SQLAlchemy has no way to know which classes
    are models, so ORM features like Column, relationship, and automatic
    Python-object mapping simply would not work.
    """
    pass


class IdMixin:
    """
    Surrogate primary key mixin.

    Attributes
    ----------
    id : Mapped[int]
        Surrogate primary key for the record.
        Automatically assigned as a monotonically increasing integer upon insertion.

    Notes
    -----
    ``id`` is declared as ``primary_key=True``, which causes PostgreSQL to
    automatically create a unique B-tree index on the column. This index
    serves two purposes:

    1. **Uniqueness enforcement.** PostgreSQL rejects any insertion that would
       produce a duplicate ``id`` value, guaranteeing that every record is
       uniquely identifiable.

    2. **Foreign key lookup performance.** Every foreign key in the schema
       (e.g., ``user_id`` in ``refresh_tokens``, ``user_id`` in ``user_roles``)
       references this column. Without the index, resolving such a reference
       would require a full table scan on every join or cascaded operation.
       The B-tree index reduces each lookup to O(log n).
    """

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="Primary key identifier",
    )


class CreatedAtMixin:
    """
    Creation timestamp mixin.

    Attributes
    ----------
    created_at : Mapped[datetime]
        Timezone-aware timestamp indicating when the record was first inserted.
        Set automatically by the database using the current UTC time at insert
        time. Value remains immutable after creation.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="Record creation timestamp",
    )


class UpdatedAtMixin:
    """
    Last-update timestamp mixin.

    Attributes
    ----------
    updated_at : Mapped[datetime]
        Timezone-aware timestamp indicating the last time the record was
        modified. Automatically updated to the current UTC time on every
        ``UPDATE`` operation via SQLAlchemy's ``onupdate`` column default.
    """

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="Last update timestamp",
    )