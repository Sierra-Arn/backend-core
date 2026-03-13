# app/modules/account/change_password/routes.py
from fastapi import Depends, status
from .schemas import ChangePasswordRequest
from .domen import change_password
from ..router import account_router
from ....shared.auth import get_current_user


@account_router.patch(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change the authenticated user's password",
    description=(
        "Verifies the current password and replaces it with the new one. "
        "Invalidates the current session by blacklisting the access token "
        "and deleting the refresh token. Returns ``401`` if the current "
        "password is incorrect. "
        "The target user is identified by the ``sub`` claim of the Bearer token — "
        "a user can only change their own password."
    ),
)
async def change_password_route(
    body: ChangePasswordRequest,
    payload: dict = Depends(get_current_user),
) -> None:
    await change_password(
        user_id=int(payload["sub"]),
        current_password=body.password,
        new_password=body.new_password,
        refresh_token=body.refresh_token,
        access_token_jti=payload["jti"],
        access_token_exp=payload["exp"],
    )