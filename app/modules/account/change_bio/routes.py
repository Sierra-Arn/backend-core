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