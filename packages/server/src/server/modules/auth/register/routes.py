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

# packages/server/src/server/modules/auth/register/routes.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from postgres_lib.repositories.user import UserRepository
from postgres_lib.repositories.role import RoleRepository
from auth_lib.repositories.password import PasswordRepository
from .schemas import RegisterRequest
from ..router import auth_router
from ....dependencies import get_async_db_session

# Route registration: decorating with @auth_router.post() alone is not enough —
# this module must be imported somewhere in the application (e.g. in
# modules/auth/__init__.py) for FastAPI to discover and register the route.
# Failure paths (409, 422, 500) are handled globally by the exception handlers
# registered in the application factory and documented via ErrorResponse.
@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description=(
        "Creates a new user account with the provided email and password. "
        "The default user role is assigned automatically. "
        "Returns 409 if the email is already registered."
    ),
)
async def register_route(
    body: RegisterRequest,
    db_session: AsyncSession = Depends(get_async_db_session),
) -> None:
    """
    Create a new user account and assign the default user role.

    Parameters
    ----------
    body : RegisterRequest
        Request payload containing the email and plaintext password.
    db_session : AsyncSession
        Active async database session injected by get_async_db_session.

    Raises
    ------
    HTTPException
        409 Conflict if an account with the given email already exists.
        500 Internal Server Error if the default role is not found in the
        database, which indicates a missing seed step.
    """
    if await UserRepository.get_by_email(db_session, email=body.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Account with email '{body.email}' already exists.",
        )

    default_role = await RoleRepository.get_by_name(db_session, name="user")
    if default_role is None:
        raise RuntimeError("Default role 'user' not found.")

    user = await UserRepository.create(db_session, obj_data={
        "email": body.email,
        "hashed_password": PasswordRepository.hash(body.password),
    })

    await UserRepository.assign_role(db_session, user_id=user.id, role_id=default_role.id)
    await db_session.commit()