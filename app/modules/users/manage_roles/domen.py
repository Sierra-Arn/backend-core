# app/modules/users/manage_roles/domen.py
from fastapi import HTTPException, status
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import UserRepository, RoleRepository, UserRoleRepository


async def assign_role(user_id: int, role_name: str) -> None:
    """
    Assign a role to a user.

    Parameters
    ----------
    user_id : int
        Primary key of the user receiving the role.
    role_name : str
        Name of the role to assign.

    Raises
    ------
    HTTPException
        ``404 Not Found`` if the user or role does not exist.
        ``409 Conflict`` if the user already has the role.
    """
    async with get_async_db_session() as db:
        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)
        user_role_repo = UserRoleRepository(db)

        user = await user_repo.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )

        role = await role_repo.get_by_name(role_name)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{role_name}' not found.",
            )

        if await user_role_repo.has_role(user_id=user_id, role_id=role.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User already has the role '{role_name}'.",
            )

        await user_role_repo.assign_role(user_id=user_id, role_id=role.id)
        await db.commit()


async def revoke_role(user_id: int, role_name: str) -> None:
    """
    Remove a role from a user.

    Parameters
    ----------
    user_id : int
        Primary key of the user to revoke the role from.
    role_name : str
        Name of the role to revoke.

    Raises
    ------
    HTTPException
        ``404 Not Found`` if the user or role does not exist.
        ``409 Conflict`` if the user does not have the role.
    """
    async with get_async_db_session() as db:
        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)
        user_role_repo = UserRoleRepository(db)

        user = await user_repo.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )

        role = await role_repo.get_by_name(role_name)
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{role_name}' not found.",
            )

        if not await user_role_repo.has_role(user_id=user_id, role_id=role.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User does not have the role '{role_name}'.",
            )

        await user_role_repo.revoke_role(user_id=user_id, role_id=role.id)
        await db.commit()