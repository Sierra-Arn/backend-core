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