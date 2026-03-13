# app/modules/roles/create/domen.py
from fastapi import HTTPException, status
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import RoleRepository
from .schemas import CreateRoleResponse


async def create_role(name: str) -> CreateRoleResponse:
    """
    Create a new role with the given name.

    Parameters
    ----------
    name : str
        Unique name for the new role.

    Returns
    -------
    CreateRoleResponse
        The newly created role with its auto-generated id.

    Raises
    ------
    HTTPException
        ``409 Conflict`` if a role with the given name already exists.
    """
    
    async with get_async_db_session() as db:
        role_repo = RoleRepository(db)

        if await role_repo.get_by_name(name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Role '{name}' already exists.",
            )

        role = await role_repo.create({"name": name})
        await db.commit()

    return CreateRoleResponse(id=role.id, name=role.name)