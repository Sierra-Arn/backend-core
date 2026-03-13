# app/modules/roles/manage_permissions/domen.py
from fastapi import HTTPException, status
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import RoleRepository, RolePermissionRepository
from ....shared.postgres.db.models import Permission


async def assign_permission(role_id: int, permission: Permission) -> None:
    """
    Assign a permission to a role.

    Parameters
    ----------
    role_id : int
        Primary key of the role receiving the permission.
    permission : Permission
        The permission to assign.

    Raises
    ------
    HTTPException
        ``404 Not Found`` if the role does not exist.
        ``409 Conflict`` if the role already has the permission.
    """
    async with get_async_db_session() as db:
        role_repo = RoleRepository(db)
        role_permission_repo = RolePermissionRepository(db)

        role = await role_repo.get(role_id)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with id {role_id} not found.",
            )

        if await role_permission_repo.has_permission(role_id=role_id, permission=permission):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role already has the permission '{permission}'.",
            )

        await role_permission_repo.assign_permission(role_id=role_id, permission=permission)
        await db.commit()


async def revoke_permission(role_id: int, permission: Permission) -> None:
    """
    Remove a permission from a role.

    Parameters
    ----------
    role_id : int
        Primary key of the role to revoke the permission from.
    permission : Permission
        The permission to revoke.

    Raises
    ------
    HTTPException
        ``404 Not Found`` if the role does not exist.
        ``409 Conflict`` if the role does not have the permission.
    """
    async with get_async_db_session() as db:
        role_repo = RoleRepository(db)
        role_permission_repo = RolePermissionRepository(db)

        role = await role_repo.get(role_id)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with id {role_id} not found.",
            )

        if not await role_permission_repo.has_permission(role_id=role_id, permission=permission):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role does not have the permission '{permission}'.",
            )

        await role_permission_repo.revoke_permission(role_id=role_id, permission=permission)
        await db.commit()