# app/modules/auth/refresh/routes.py
from fastapi import status
from .schemas import RefreshRequest, RefreshResponse
from .domen import refresh
from ..router import auth_router


@auth_router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=RefreshResponse,
    summary="Rotate the token pair",
    description=(
        "Validates the provided refresh token, issues a new access/refresh "
        "token pair, and invalidates the old refresh token. Returns ``401`` "
        "if the refresh token does not exist or has expired."
    ),
)
async def refresh_route(body: RefreshRequest) -> RefreshResponse:
    tokens = await refresh(refresh_token=body.refresh_token)
    return RefreshResponse(**tokens)