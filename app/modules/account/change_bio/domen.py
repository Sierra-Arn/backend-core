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