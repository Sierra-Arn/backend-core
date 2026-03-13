# app/modules/account/change_bio/routes.py
from fastapi import Depends, status
from .schemas import ChangeBioRequest
from .domen import change_bio
from ..router import account_router
from ....shared.auth import get_current_user


@account_router.patch(
    "/change-bio",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Update the authenticated user's bio",
    description=(
        "Replaces the user's biographical text with the provided value. "
        "Pass ``null`` to clear the field. "
        "The target user is identified by the ``sub`` claim of the Bearer token — "
        "a user can only update their own bio."
    ),
)
async def change_bio_route(
    body: ChangeBioRequest,
    payload: dict = Depends(get_current_user),
) -> None:
    await change_bio(
        user_id=int(payload["sub"]),
        bio=body.bio,
    )