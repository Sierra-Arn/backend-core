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

# packages/server/src/server/modules/account/me/routes.py
from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib import UserRepository
from .schemas import UserResponse
from ..router import account_router
from ....dependencies import get_async_db_session, get_current_user


@account_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
    summary="Retrieve the current user profile",
    description=(
        "Returns the profile of the currently authenticated user. "
        "Requires a valid access token in the Authorization header."
    ),
)
async def me_route(
    payload: dict = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session),
) -> UserResponse:
    """
    Return the profile of the currently authenticated user.

    Parameters
    ----------
    payload : dict
        Decoded JWT payload injected by get_current_user. Provides the
        user_id via the sub claim without an additional database round-trip.
    db_session : AsyncSession
        Active async database session injected by get_async_db_session.

    Returns
    -------
    UserResponse
        Profile fields of the authenticated user.
    """
    user = await UserRepository.get_by_id(db_session, obj_id=int(payload["sub"]))
    return UserResponse.model_validate(user)