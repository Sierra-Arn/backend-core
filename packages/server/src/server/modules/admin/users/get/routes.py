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

# packages/server/src/server/modules/admin/users/get/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import UserRepository, PermissionEnum
from ..router import users_admin_router
from ....account.me.routes import UserResponse
from .....dependencies import get_async_db_session, require_permission


@users_admin_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[UserResponse],
    summary="Retrieve a paginated list of all users",
    description=(
        "Returns a paginated list of all registered users ordered by primary key. "
        "Requires the users:get_all permission."
    ),
)
async def get_all_users_route(
    skip: int = 0,
    limit: int = 100,
    payload: dict = Depends(require_permission(PermissionEnum.USERS_GET_ALL)),
    db: AsyncSession = Depends(get_async_db_session),
) -> list[UserResponse]:
    """
    Return a paginated list of all registered users.

    Parameters
    ----------
    skip : int, optional
        Number of records to offset from the beginning of the result set.
        Default is 0.
    limit : int, optional
        Maximum number of records to return. Default is 100.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the users:get_all permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Returns
    -------
    list of UserResponse
        Paginated list of user records ordered by ascending primary key.
    """
    users = await UserRepository.get_all(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@users_admin_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Retrieve a single user by primary key",
    description=(
        "Returns the profile of the user with the given id. "
        "Returns 404 if no user exists with that id. "
        "Requires the users:get permission."
    ),
)
async def get_user_route(
    user_id: int,
    payload: dict = Depends(require_permission(PermissionEnum.USERS_GET)),
    db: AsyncSession = Depends(get_async_db_session),
) -> UserResponse:
    """
    Return the profile of a single user identified by primary key.

    Parameters
    ----------
    user_id : int
        Primary key of the user to retrieve.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the users:get permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

    Returns
    -------
    UserResponse
        Profile fields of the requested user.

    Raises
    ------
    HTTPException
        404 Not Found if no user exists with the given primary key.
    """
    user = await UserRepository.get_by_id(db, obj_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} does not exist.",
        )
    return UserResponse.model_validate(user)