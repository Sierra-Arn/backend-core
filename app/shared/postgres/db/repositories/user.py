# app/shared/postgres/db/repositories/user.py
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ..models import User, Role


class UserRepository(BaseRepository[User]):
    """
    Concrete repository for managing ``User`` entities in the database.
    Extends the generic ``BaseRepository`` with user-specific queries
    that are not covered by the standard CRUD interface.
    Attributes
    ----------
    db : AsyncSession
        Active SQLAlchemy async session inherited from the base repository.
    model : Type[User]
        Bound to the ``User`` ORM class at initialization.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the user repository with a database session.
        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy async session providing transactional context.
            Typically injected via a dependency or context manager.
        """
        super().__init__(db=db, model=User)

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user record by its unique email address.
        Used during registration to detect duplicate accounts before
        insertion, and during login to fetch the user record for
        credential verification.
        
        Parameters
        ----------
        email : str
            The email address to look up. Must be an exact match.
        
        Returns
        -------
        User or None
            The matching user instance if found; ``None`` if no record
            exists with the given email address.
        
        Notes
        -----
        The ``email`` column carries a unique B-tree index, so this
        query resolves in O(log n) rather than requiring a full table scan.
        """

        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: int) -> User | None:
        """
        Retrieve a user record by primary key with roles and permissions
        eagerly loaded.

        Used wherever the caller needs to access ``user.roles`` or
        ``role.permissions`` — for example, when building the JWT payload
        during login or token refresh. Eager loading via ``selectinload``
        avoids the ``MissingGreenlet`` error that occurs when lazy loading
        is attempted outside an active async session.

        Parameters
        ----------
        user_id : int
            Primary key of the user to retrieve.

        Returns
        -------
        User or None
            The matching user instance with ``roles`` and
            ``role.permissions`` populated, or ``None`` if no record
            exists with the given ID.
        """

        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email_with_roles(self, email: str) -> User | None:
        """
        Retrieve a user record by email address with roles and permissions
        eagerly loaded.

        Used during login where both credential verification and JWT payload
        construction require access to ``user.roles`` and
        ``role.permissions`` within the same request.

        Parameters
        ----------
        email : str
            The email address to look up. Must be an exact match.

        Returns
        -------
        User or None
            The matching user instance with ``roles`` and
            ``role.permissions`` populated, or ``None`` if no record
            exists with the given email address.
        """

        stmt = (
            select(User)
            .where(User.email == email)
            .options(
                selectinload(User.roles).selectinload(Role.permissions)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_roles(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Retrieve a paginated list of all users with roles eagerly loaded.

        Used in ``get_all`` to avoid ``DetachedInstanceError`` when accessing
        ``user.roles`` outside the session context.

        Parameters
        ----------
        skip : int, optional
            Number of records to skip (for pagination offset). Default is ``0``.
        limit : int, optional
            Maximum number of records to return. Default is ``100``.

        Returns
        -------
        list[User]
            A list of up to ``limit`` user instances with ``roles`` populated.
        """

        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        """
        Return the total number of user records in the database.
        Used alongside ``get_all`` to provide pagination metadata
        (e.g., total count for the client to calculate page numbers).
        
        Returns
        -------
        int
            Total number of rows in the ``users`` table.
        """

        stmt = select(func.count()).select_from(User)
        result = await self.db.execute(stmt)
        return result.scalar_one()