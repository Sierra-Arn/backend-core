# app/modules/auth/logout/routes.py
from fastapi import status
from .schemas import LogoutRequest
from .domen import logout
from ..router import auth_router


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Terminate the current session",
    description=(
        "Blacklists the provided access token and deletes the refresh token "
        "from the database. Returns ``401`` if the access token is invalid "
        "or expired."
    ),
)
async def logout_route(body: LogoutRequest) -> None:
    await logout(
        access_token=body.access_token,
        refresh_token=body.refresh_token,
    )