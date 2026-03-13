# app/shared/postgres/db/repositories/refresh_token.py
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ..models import RefreshToken


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """
    Concrete repository for managing ``RefreshToken`` entities in the database.

    Extends the generic ``BaseRepository`` with token-specific queries
    for lookup by token value, deletion on logout, and expiry-based cleanup.

    Attributes
    ----------
    db : AsyncSession
        Active SQLAlchemy async session inherited from the base repository.
    model : Type[RefreshToken]
        Bound to the ``RefreshToken`` ORM class at initialization.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the refresh token repository with a database session.

        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy async session providing transactional context.
            Typically injected via a dependency or context manager.
        """
        super().__init__(db=db, model=RefreshToken)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """
        Retrieve a refresh token record by its opaque token string.

        Called on every token refresh request to validate the incoming
        token and fetch its associated metadata (owner, expiry) before
        issuing a new token pair.

        Parameters
        ----------
        token : str
            The raw opaque token string to look up. Must be an exact match.

        Returns
        -------
        RefreshToken or None
            The matching token record if found; ``None`` if no record
            exists with the given token value.

        Notes
        -----
        The ``token`` column carries a unique B-tree index, so this
        query resolves in O(log n) rather than requiring a full table scan.
        """
        
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_token(self, token: str) -> bool:
        """
        Delete a refresh token record by its opaque token string.

        Called on logout and during token rotation to remove the previously
        issued token so it cannot be reused.

        Parameters
        ----------
        token : str
            The raw opaque token string identifying the record to delete.

        Returns
        -------
        bool
            ``True`` if the token was found and deleted;
            ``False`` if no record exists with the given token value.
        """
        
        stmt = (
            delete(RefreshToken)
            .where(RefreshToken.token == token)
            .returning(RefreshToken.id)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.fetchone() is not None

    async def purge_expired(self) -> int:
        """
        Remove all refresh token records whose expiry timestamp is in the past.

        Tokens expire naturally when their ``expires_at`` timestamp is
        reached — they will be rejected on any refresh attempt regardless.
        Purging them keeps the table compact and prevents unbounded growth.

        Intended to be called periodically (e.g., via a scheduled task).

        Returns
        -------
        int
            The total number of records deleted.

        Notes
        -----
        The ``expires_at`` column carries a B-tree index that makes the
        expiry range condition an efficient index range scan rather than
        a full table scan.
        """

        now = datetime.now(timezone.utc)
        stmt = (
            delete(RefreshToken)
            .where(RefreshToken.expires_at <= now)
            .returning(RefreshToken.id)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return len(result.fetchall())