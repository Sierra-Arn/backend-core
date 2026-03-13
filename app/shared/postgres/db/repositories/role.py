# app/shared/postgres/db/repositories/role.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseRepository
from ..models import Role


class RoleRepository(BaseRepository[Role]):
    """
    Concrete repository for managing ``Role`` entities in the database.
    Extends the generic ``BaseRepository`` with role-specific queries
    that are not covered by the standard CRUD interface.
    Attributes
    ----------
    db : AsyncSession
        Active SQLAlchemy async session inherited from the base repository.
    model : Type[Role]
        Bound to the ``Role`` ORM class at initialization.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the role repository with a database session.
        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy async session providing transactional context.
            Typically injected via a dependency or context manager.
        """
        super().__init__(db=db, model=Role)

    async def get_by_name(self, name: str) -> Role | None:
        """
        Retrieve a role record by its unique name.
        Used during registration to look up the default role assigned
        to every new account (e.g., ``"user"``), and during authorization
        checks that resolve permissions by role name.
        Parameters
        ----------
        name : str
            The role name to look up (e.g., ``"user"``, ``"admin"``).
            Must be an exact match.
        Returns
        -------
        Role or None
            The matching role instance if found; ``None`` if no record
            exists with the given name.
        Notes
        -----
        The ``name`` column carries a unique B-tree index, so this
        query resolves in O(log n) rather than requiring a full table scan.
        """
        
        stmt = select(Role).where(Role.name == name)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()