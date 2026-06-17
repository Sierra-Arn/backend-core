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

# packages/shared/src/postgres_lib/models/base.py
from datetime import datetime
from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    """
    Central registry for all ORM models in the application.

    Every class that inherits from Base is automatically registered in
    Base.metadata — a collection of all Table objects in the schema.
    This metadata is later used to create or drop tables.

    Without a shared Base, SQLAlchemy has no way to know which classes
    are models, so ORM features like relationship and automatic
    Python-object mapping would not work.
    """

    pass


class IdModel(Base):
    """
    Abstract base class providing a surrogate primary key column.

    Inheriting models automatically receive the id column without
    requiring a separate mixin. No database table is created for
    this class itself.

    Attributes
    ----------
    __abstract__ : bool
        Flag indicating to SQLAlchemy that this is an abstract base
        class. No database table will be created for this class itself.
    id : Mapped[int]
        Surrogate primary key for the record. Automatically assigned
        as a monotonically increasing integer upon insertion.
    """

    __abstract__ = True

    @declared_attr
    def id(cls) -> Mapped[int]:
        """
        Define the primary key column for the inheriting model.

        Returns
        -------
        Mapped[int]
            SQLAlchemy mapped column declared as the primary key,
            dynamically commented with the inheriting class name.
        """
        return mapped_column(
            Integer,
            primary_key=True,
            autoincrement=True,
            comment=f"Primary key identifier for {cls.__name__}",
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
