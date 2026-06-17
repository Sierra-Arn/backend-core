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

# packages/shared/src/postgres_lib/repositories/user.py
from sqlalchemy import select, func, delete, Select
from sqlalchemy.orm import selectinload, noload
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ..models import User, Role, UserRole


class UserRepository(BaseRepository):
    """
    Concrete repository for managing User entities in the database.

    Extends BaseRepository with user-specific queries and role assignment
    operations. Role assignment methods are colocated here rather than in
    a separate repository because roles are always managed in the context
    of a specific user and share the same transactional session.

    Attributes
    ----------
    model_class : ClassVar[type[User]]
        Bound to the User ORM class at class definition time.
    """

    model_class = User

    @classmethod
    def _apply_load_options(
        cls,
        stmt: Select,
        load_roles: bool,
        load_permissions: bool,
    ) -> Select:
        """
        Apply eager loading options to a SELECT statement for User relationships.

        Parameters
        ----------
        stmt : Select
            Base SELECT statement to decorate with loading options.
        load_roles : bool
            If True, eagerly load roles via selectinload. If False, roles
            are explicitly suppressed via noload.
        load_permissions : bool
            If True, eagerly load permissions for each role via selectinload.
            Ignored when load_roles is False. If False, permissions are
            explicitly suppressed via noload.

        Returns
        -------
        Select
            The statement with all loading options applied.

        Notes
        -----
        Every relationship is explicitly controlled — either loaded or
        suppressed — to prevent SQLAlchemy from issuing implicit queries
        when relationship attributes are accessed after the session closes.
        """
        if load_roles:
            if load_permissions:
                stmt = stmt.options(
                    selectinload(User.roles).selectinload(Role.permissions)
                )
            else:
                stmt = stmt.options(
                    selectinload(User.roles).noload(Role.permissions)
                )
        else:
            stmt = stmt.options(noload(User.roles))
        return stmt

    @classmethod
    async def get_by_id(
        cls,
        session: AsyncSession,
        obj_id: int,
        load_roles: bool = False,
        load_permissions: bool = False,
    ) -> User | None:
        """
        Fetch a User by primary key with optional eager loading.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        obj_id : int
            Primary key of the user to retrieve.
        load_roles : bool, optional
            If True, eagerly load all roles. Default is False.
        load_permissions : bool, optional
            If True, eagerly load permissions for each role. Requires
            load_roles to be True. Default is False.

        Returns
        -------
        User or None
            Matching User instance, or None if not found.
        """
        stmt = select(User).where(User.id == obj_id)
        stmt = cls._apply_load_options(stmt, load_roles, load_permissions)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        load_roles: bool = False,
        load_permissions: bool = False,
    ) -> list[User]:
        """
        Fetch a paginated list of Users ordered by primary key.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        skip : int, optional
            Number of records to offset from the beginning of the result
            set. Default is 0.
        limit : int, optional
            Maximum number of records to return. Default is 100.
        load_roles : bool, optional
            If True, eagerly load all roles. Default is False.
        load_permissions : bool, optional
            If True, eagerly load permissions for each role. Requires
            load_roles to be True. Default is False.

        Returns
        -------
        list of User
            List of User instances ordered by ascending primary key.
            Returns an empty list if no records match the pagination window.
        """
        stmt = select(User).order_by(User.id).offset(skip).limit(limit)
        stmt = cls._apply_load_options(stmt, load_roles, load_permissions)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def get_by_email(
        cls,
        session: AsyncSession,
        email: str,
        load_roles: bool = False,
        load_permissions: bool = False,
    ) -> User | None:
        """
        Fetch a User by email address with optional eager loading.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        email : str
            Email address to look up. Must be an exact match.
        load_roles : bool, optional
            If True, eagerly load all roles. Default is False.
        load_permissions : bool, optional
            If True, eagerly load permissions for each role. Requires
            load_roles to be True. Default is False.

        Returns
        -------
        User or None
            Matching User instance, or None if not found.
        """
        stmt = select(User).where(User.email == email)
        stmt = cls._apply_load_options(stmt, load_roles, load_permissions)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def count_all(cls, session: AsyncSession) -> int:
        """
        Return the total number of User records in the database.

        Used alongside get_all to provide pagination metadata so the
        client can calculate total page count without fetching all rows.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.

        Returns
        -------
        int
            Total number of rows in the users table.
        """
        stmt = select(func.count()).select_from(User)
        result = await session.execute(stmt)
        return result.scalar_one()

    @classmethod
    async def assign_role(
        cls,
        session: AsyncSession,
        user_id: int,
        role_id: int,
    ) -> UserRole:
        """
        Create an association record assigning a role to a user.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        user_id : int
            Primary key of the user receiving the role.
        role_id : int
            Primary key of the role being assigned.

        Returns
        -------
        UserRole
            Newly created association record with all fields populated,
            including the server-generated created_at timestamp.

        Notes
        -----
        The composite primary key (user_id, role_id) enforces uniqueness
        at the database level. Attempting to assign the same role twice
        raises an IntegrityError. Callers should use has_role to guard
        against duplicate assignments when idempotency is required.
        """
        user_role = UserRole(user_id=user_id, role_id=role_id)
        session.add(user_role)
        await session.flush()
        await session.refresh(user_role)
        return user_role

    @classmethod
    async def revoke_role(
        cls,
        session: AsyncSession,
        user_id: int,
        role_id: int,
    ) -> bool:
        """
        Delete the association record removing a role from a user.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        user_id : int
            Primary key of the user to revoke the role from.
        role_id : int
            Primary key of the role to revoke.

        Returns
        -------
        bool
            True if the association was found and deleted,
            False if no such association exists.
        """
        stmt = (
            delete(UserRole)
            .where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
            .returning(UserRole.role_id)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.fetchone() is not None

    @classmethod
    async def has_role(
        cls,
        session: AsyncSession,
        user_id: int,
        role_id: int,
    ) -> bool:
        """
        Check whether a specific role is already assigned to a user.

        Used before assign_role to prevent duplicate assignments when
        idempotent behavior is required.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        user_id : int
            Primary key of the user to check.
        role_id : int
            Primary key of the role to check.

        Returns
        -------
        bool
            True if the (user_id, role_id) pair exists in the association
            table, False otherwise.
        """
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @classmethod
    async def get_roles_for_user(
        cls,
        session: AsyncSession,
        user_id: int,
    ) -> list[Role]:
        """
        Retrieve all roles currently assigned to a given user.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        user_id : int
            Primary key of the user whose roles are being fetched.

        Returns
        -------
        list of Role
            List of Role instances assigned to the user. Returns an
            empty list if no roles are assigned.

        Notes
        -----
        The composite index on (user_id, role_id) with user_id as the
        leading column allows PostgreSQL to satisfy this query with an
        index range scan rather than a full table scan.
        """
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())