# app/modules/users/get_all/domen.py
from .schemas import GetAllUsersResponse, UserSchema
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import UserRepository


async def get_all_users(skip: int, limit: int) -> GetAllUsersResponse:
    """
    Retrieve a paginated list of all registered users.

    Parameters
    ----------
    skip : int
        Number of records to skip (pagination offset).
    limit : int
        Maximum number of records to return.

    Returns
    -------
    GetAllUsersResponse
        Paginated response containing the user list and pagination metadata.
    """
    async with get_async_db_session() as db:
        user_repo = UserRepository(db)
        users = await user_repo.get_all(
            skip=skip,
            limit=limit,
            load_roles=True,
            load_permissions=False,
        )
        total = await user_repo.count_all()

        return GetAllUsersResponse(
            users=[UserSchema.model_validate(user) for user in users],
            total=total,
            skip=skip,
            limit=limit,
        )