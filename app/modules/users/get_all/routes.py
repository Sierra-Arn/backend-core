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

# app/modules/users/get_all/routes.py
from fastapi import Depends, Query, status
from .schemas import GetAllUsersResponse
from .domen import get_all_users
from ..router import users_router
from ....shared.auth import require_permission


@users_router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    response_model=GetAllUsersResponse,
    summary="Retrieve a paginated list of all users",
    description=(
        "Returns all registered users with pagination support. "
        "Restricted to users with the ``users:get_all`` permission."
    ),
)
async def get_all_route(
    skip: int = Query(default=0, ge=0, description="Number of records to skip."),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records to return."),
    payload: dict = Depends(require_permission("users:get_all")),
) -> GetAllUsersResponse:
    return await get_all_users(skip=skip, limit=limit)