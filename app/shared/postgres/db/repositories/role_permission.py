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

# app/shared/postgres/db/repositories/role_permission.py
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.role_permission import RolePermission
from ..models import Permission


class RolePermissionRepository:
    """
    Concrete repository for managing ``RolePermission`` association records.

    Does not extend ``BaseRepository`` because ``RolePermission`` queries
    are permission-scoped rather than ID-scoped, making the standard
    ``get(obj_id: int)`` interface inapplicable as the primary access pattern.

    Attributes
    ----------
    db : AsyncSession
        Active SQLAlchemy async session injected at construction time.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the role-permission repository with a database session.

        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy async session providing transactional context.
            Typically injected via a dependency or context manager.
        """
        self.db = db

    async def assign_permission(self, role_id: int, permission: Permission) -> RolePermission:
        """
        Assign a permission to a role.

        Parameters
        ----------
        role_id : int
            Primary key of the role receiving the permission.
        permission : Permission
            The permission to assign.

        Returns
        -------
        RolePermission
            The newly created association record with all fields populated.

        Notes
        -----
        The unique constraint on ``(role_id, permission)`` enforces
        uniqueness at the database level. Attempting to assign the same
        permission twice will raise an ``IntegrityError``. Callers should
        use ``has_permission`` to guard against duplicate assignments
        when idempotency is required.
        """
        role_permission = RolePermission(role_id=role_id, permission=permission)
        self.db.add(role_permission)
        await self.db.flush()
        await self.db.refresh(role_permission)
        return role_permission

    async def revoke_permission(self, role_id: int, permission: Permission) -> bool:
        """
        Remove a permission from a role.

        Parameters
        ----------
        role_id : int
            Primary key of the role to revoke the permission from.
        permission : Permission
            The permission to revoke.

        Returns
        -------
        bool
            ``True`` if the permission was found and removed;
            ``False`` if no such assignment exists.
        """
        
        stmt = (
            delete(RolePermission)
            .where(
                RolePermission.role_id == role_id,
                RolePermission.permission == permission,
            )
            .returning(RolePermission.id)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.fetchone() is not None

    async def has_permission(self, role_id: int, permission: Permission) -> bool:
        """
        Check whether a specific permission is already assigned to a role.

        Used before ``assign_permission`` to prevent duplicate assignments
        when idempotent behavior is required.

        Parameters
        ----------
        role_id : int
            Primary key of the role to check.
        permission : Permission
            The permission to check.

        Returns
        -------
        bool
            ``True`` if the ``(role_id, permission)`` pair exists;
            ``False`` otherwise.
        """
        stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission == permission,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None


    async def get_permissions_for_role(self, role_id: int) -> list[Permission]:
        """
        Retrieve all permissions assigned to a given role.

        Parameters
        ----------
        role_id : int
            Primary key of the role whose permissions are being fetched.

        Returns
        -------
        list[Permission]
            A list of ``Permission`` values assigned to the role.
            Returns an empty list if no permissions are assigned.
        """
        stmt = select(RolePermission.permission).where(RolePermission.role_id == role_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())