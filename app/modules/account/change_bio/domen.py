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

# app/modules/account/change_bio/domen.py
from ....shared.postgres.db import get_async_db_session
from ....shared.postgres.db.repositories import UserRepository


async def change_bio(user_id: int, bio: str | None) -> None:
    """
    Update the authenticated user's biographical text.

    Parameters
    ----------
    user_id : int
        Primary key of the authenticated user, extracted from the JWT payload.
    bio : str or None
        New biographical text to store. Pass ``None`` to clear the field.
    """
    
    async with get_async_db_session() as db:
        user_repo = UserRepository(db)
        await user_repo.update(user_id, {"bio": bio})
        await db.commit()