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

# packages/shared/src/postgres_lib/repositories/role.py
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ..models import Role, RolePermission, PermissionEnum


class RoleRepository(BaseRepository):
    """
    Concrete repository for managing Role entities in the database.

    Extends BaseRepository with role-specific queries and permission
    assignment operations. Permission assignment methods are colocated
    here rather than in a separate repository because permissions are
    always managed in the context of a specific role and share the same
    transactional session.

    Attributes
    ----------
    model_class : ClassVar[type[Role]]
        Bound to the Role ORM class at class definition time.
    """

    model_class = Role

    @classmethod
    async def get_by_name(
        cls,
        session: AsyncSession,
        name: str,
    ) -> Role | None:
        """
        Fetch a Role by its unique name.

        Used during registration to look up the default role assigned
        to every new account, and during authorization checks that
        resolve permissions by role name.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        name : str
            Role name to look up. Must be an exact match.

        Returns
        -------
        Role or None
            Matching Role instance, or None if not found.

        Notes
        -----
        The name column carries a unique B-tree index, so this query
        resolves in O(log n) rather than requiring a full table scan.
        """
        stmt = select(Role).where(Role.name == name)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def assign_permission(
        cls,
        session: AsyncSession,
        role_id: int,
        permission: PermissionEnum,
    ) -> RolePermission:
        """
        Create an association record assigning a permission to a role.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        role_id : int
            Primary key of the role receiving the permission.
        permission : PermissionEnum
            Permission value to assign.

        Returns
        -------
        RolePermission
            Newly created association record with all fields populated,
            including the surrogate primary key.

        Notes
        -----
        The unique constraint on (role_id, permission) enforces uniqueness
        at the database level. Attempting to assign the same permission
        twice raises an IntegrityError. Callers should use has_permission
        to guard against duplicate assignments when idempotency is required.
        """
        role_permission = RolePermission(role_id=role_id, permission=permission)
        session.add(role_permission)
        await session.flush()
        await session.refresh(role_permission)
        return role_permission

    @classmethod
    async def revoke_permission(
        cls,
        session: AsyncSession,
        role_id: int,
        permission: PermissionEnum,
    ) -> bool:
        """
        Delete the association record removing a permission from a role.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        role_id : int
            Primary key of the role to revoke the permission from.
        permission : PermissionEnum
            Permission value to revoke.

        Returns
        -------
        bool
            True if the association was found and deleted,
            False if no such association exists.
        """
        stmt = (
            delete(RolePermission)
            .where(
                RolePermission.role_id == role_id,
                RolePermission.permission == permission,
            )
            .returning(RolePermission.id)
        )
        result = await session.execute(stmt)
        await session.flush()
        return result.fetchone() is not None

    @classmethod
    async def has_permission(
        cls,
        session: AsyncSession,
        role_id: int,
        permission: PermissionEnum,
    ) -> bool:
        """
        Check whether a specific permission is already assigned to a role.

        Used before assign_permission to prevent duplicate assignments
        when idempotent behavior is required.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        role_id : int
            Primary key of the role to check.
        permission : PermissionEnum
            Permission value to check.

        Returns
        -------
        bool
            True if the (role_id, permission) pair exists in the association
            table, False otherwise.
        """
        stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission == permission,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    @classmethod
    async def get_permissions_for_role(
        cls,
        session: AsyncSession,
        role_id: int,
    ) -> list[PermissionEnum]:
        """
        Retrieve all permissions currently assigned to a given role.

        Parameters
        ----------
        session : AsyncSession
            Active async database session bound to the transaction.
        role_id : int
            Primary key of the role whose permissions are being fetched.

        Returns
        -------
        list of PermissionEnum
            List of Permission values assigned to the role. Returns an
            empty list if no permissions are assigned.
        """
        stmt = select(RolePermission.permission).where(
            RolePermission.role_id == role_id,
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())