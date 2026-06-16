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

# app/shared/postgres/db/repositories/user.py
from sqlalchemy import select, func, Select
from sqlalchemy.orm import selectinload, noload
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ..models import User, Role


class UserRepository(BaseRepository[User]):
    """
    Concrete repository for managing ``User`` entities in the database.
    Extends the generic ``BaseRepository`` with user-specific queries
    that are not covered by the standard CRUD interface.

    Attributes
    ----------
    db : AsyncSession
        Active SQLAlchemy async session inherited from the base repository.
    model : Type[User]
        Bound to the ``User`` ORM class at initialization.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the user repository with a database session.
        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy async session providing transactional context.
            Typically injected via a dependency or context manager.
        """
        super().__init__(db=db, model=User)

    def _apply_load_options(
        self,
        stmt: Select,
        load_roles: bool,
        load_permissions: bool,
    ):
        """
        Apply eager loading options to a SELECT statement for User relationships.

        Parameters
        ----------
        stmt : Select
            The base SELECT statement to apply options to.
        load_roles : bool
            If True, eagerly load roles via ``selectinload``.
            If False, roles are explicitly suppressed via ``noload``.
        load_permissions : bool
            If True, eagerly load permissions for each role via ``selectinload``.
            Ignored if ``load_roles`` is False.
            If False, permissions are explicitly suppressed via ``noload``.

        Returns
        -------
        Select
            The statement with loading options applied.
        """
        if load_roles:
            if load_permissions:
                return stmt.options(
                    selectinload(User.roles)
                    .selectinload(Role.permissions)
                )
            else:
                return stmt.options(
                    selectinload(User.roles)
                    .noload(Role.permissions)
                )
        else:
            stmt = stmt.options(noload(User.roles))

        # Always suppress refresh_tokens — never needed in API responses
        stmt = stmt.options(noload(User.refresh_tokens))
        return stmt

    async def get(
        self,
        user_id: int,
        load_roles: bool = False,
        load_permissions: bool = False,
    ) -> User | None:
        """
        Retrieve a User by ID with optional eager loading.

        Parameters
        ----------
        user_id : int
            Primary key of the user to retrieve.
        load_roles : bool, optional
            If True, eagerly load all roles. Default is False.
        load_permissions : bool, optional
            If True, eagerly load permissions for each role (requires load_roles=True).
            Default is False.

        Returns
        -------
        User | None
            User instance if found, None otherwise.
        """
        stmt = select(User).where(User.id == user_id)
        stmt = self._apply_load_options(stmt, load_roles, load_permissions)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        load_roles: bool = False,
        load_permissions: bool = False,
    ) -> list[User]:
        """
        Retrieve a paginated list of all Users with optional eager loading.

        Parameters
        ----------
        skip : int, optional
            Number of records to skip (for pagination offset). Default is 0.
        limit : int, optional
            Maximum number of records to return. Default is 100.
        load_roles : bool, optional
            If True, eagerly load all roles. Default is False.
        load_permissions : bool, optional
            If True, eagerly load permissions for each role (requires load_roles=True).
            Default is False.

        Returns
        -------
        list[User]
            A list of up to ``limit`` User instances.
        """
        stmt = select(User).offset(skip).limit(limit)
        stmt = self._apply_load_options(stmt, load_roles, load_permissions)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_email(
        self,
        email: str,
        load_roles: bool = False,
        load_permissions: bool = False,
    ) -> User | None:
        """
        Retrieve a User by email address with optional eager loading.

        Parameters
        ----------
        email : str
            The email address to look up. Must be an exact match.
        load_roles : bool, optional
            If True, eagerly load all roles. Default is False.
        load_permissions : bool, optional
            If True, eagerly load permissions for each role (requires load_roles=True).
            Default is False.

        Returns
        -------
        User | None
            User instance if found, None otherwise.
        """
        stmt = select(User).where(User.email == email)
        stmt = self._apply_load_options(stmt, load_roles, load_permissions)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_all(self) -> int:
        """
        Return the total number of user records in the database.
        Used alongside ``get_all`` to provide pagination metadata
        (e.g., total count for the client to calculate page numbers).
        
        Returns
        -------
        int
            Total number of rows in the ``users`` table.
        """
        stmt = select(func.count()).select_from(User)
        result = await self.db.execute(stmt)
        return result.scalar_one()