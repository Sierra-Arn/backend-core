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

# app/modules/auth/register/domen.py
from fastapi import HTTPException, status
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import (
    UserRepository, 
    RoleRepository, 
    UserRoleRepository
)
from ....shared.auth import hash_password


async def register(email: str, password: str) -> None:
    """
    Create a new user account and assign the default ``"user"`` role.

    Parameters
    ----------
    email : str
        Email address for the new account. Must be unique.
    password : str
        Plaintext password. Hashed with bcrypt before storage.

    Raises
    ------
    HTTPException
        ``409 Conflict`` if an account with the given email already exists.
        ``500 Internal Server Error`` if the default role is not found in
        the database (indicates a missing seed step).
    """

    async with get_async_db_session() as db:
        user_repo = UserRepository(db)
        role_repo = RoleRepository(db)
        user_role_repo = UserRoleRepository(db)

        if await user_repo.get_by_email(email) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Account with email '{email}' already exists.",
            )

        default_role = await role_repo.get_by_name("user")
        if default_role is None:
            raise RuntimeError("Default role 'user' not found.")

        user = await user_repo.create({
            "email": email,
            "hashed_password": hash_password(password),
        })
        await user_role_repo.assign_role(user_id=user.id, role_id=default_role.id)
        await db.commit()