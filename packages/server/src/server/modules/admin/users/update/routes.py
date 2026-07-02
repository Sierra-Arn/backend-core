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

# packages/server/src/server/modules/admin/users/update/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import UserRepository, PermissionEnum
from password_lib import PasswordService
from .schemas import UpdateUserRequest
from ..router import users_admin_router
from .....dependencies import get_async_db_session, require_permission


@users_admin_router.patch(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Partially update a user record",
    description=(
        "Applies the provided fields to the user record with the given id. "
        "Only explicitly provided fields are updated — absent fields are ignored. "
        "Returns 404 if no user exists with that id. "
        "Requires the users:update permission."
    ),
)
async def update_user_route(
    user_id: int,
    body: UpdateUserRequest,
    payload: dict = Depends(require_permission(PermissionEnum.USERS_UPDATE)),
    db: AsyncSession = Depends(get_async_db_session),
) -> None:
    """
    Partially update the record of a user identified by primary key.

    Only fields present in model_fields_set are applied. For scalar fields
    absent fields are skipped entirely. For bio, an explicit null clears
    the field.

    Parameters
    ----------
    user_id : int
        Primary key of the user to update.
    body : UpdateUserRequest
        Request payload containing the fields to update.
    payload : dict
        Decoded JWT payload injected by require_permission. Confirms the
        caller holds the users:update permission.
    db : AsyncSession
        Active async database session injected by get_async_db_session.

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

    updated_fields = {}

    if "password" in body.model_fields_set and body.password is not None:
        updated_fields["hashed_password"] = PasswordService.hash(body.password)

    if "is_verified" in body.model_fields_set and body.is_verified is not None:
        updated_fields["is_verified"] = body.is_verified

    if "bio" in body.model_fields_set:
        updated_fields["bio"] = body.bio

    if not updated_fields:
        return

    await UserRepository.update_by_id(db, obj_id=user_id, obj_data=updated_fields)
    await db.commit()