# app/shared/postgres/db/repositories/user_role.py
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import UserRole, Role


class UserRoleRepository:
    """
    Concrete repository for managing ``UserRole`` association records.

    Does not extend ``BaseRepository`` because ``UserRole`` uses a composite
    primary key ``(user_id, role_id)`` with no surrogate integer ``id``,
    making the standard ``get(obj_id: int)`` interface inapplicable.

    Attributes
    ----------
    db : AsyncSession
        Active SQLAlchemy async session injected at construction time.
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the user-role repository with a database session.

        Parameters
        ----------
        db : AsyncSession
            Active SQLAlchemy async session providing transactional context.
            Typically injected via a dependency or context manager.
        """
        self.db = db

    async def assign_role(self, user_id: int, role_id: int) -> UserRole:
        """
        Create a new association record assigning a role to a user.

        Flushes the session after insertion so that the database evaluates
        the ``created_at`` default, then refreshes the instance to reflect
        that value.

        Parameters
        ----------
        user_id : int
            Primary key of the user receiving the role.
        role_id : int
            Primary key of the role being assigned.

        Returns
        -------
        UserRole
            The newly created association record with all fields populated.

        Notes
        -----
        The composite primary key ``(user_id, role_id)`` enforces uniqueness
        at the database level. Attempting to assign the same role twice will
        raise an ``IntegrityError``. Callers should use ``has_role`` to guard
        against duplicate assignments when idempotency is required.
        """
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        await self.db.flush()
        await self.db.refresh(user_role)
        return user_role

    async def revoke_role(self, user_id: int, role_id: int) -> bool:
        """
        Delete the association record removing a role from a user.

        Parameters
        ----------
        user_id : int
            Primary key of the user to revoke the role from.
        role_id : int
            Primary key of the role to revoke.

        Returns
        -------
        bool
            ``True`` if the association was found and deleted;
            ``False`` if no such association exists.
        """
        stmt = (
            delete(UserRole)
            .where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
            .returning(UserRole.role_id)
        )
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.fetchone() is not None

    async def has_role(self, user_id: int, role_id: int) -> bool:
        """
        Check whether a specific role is already assigned to a user.

        Used before ``assign_role`` to prevent duplicate assignments
        when idempotent behavior is required.

        Parameters
        ----------
        user_id : int
            Primary key of the user to check.
        role_id : int
            Primary key of the role to check.

        Returns
        -------
        bool
            ``True`` if the ``(user_id, role_id)`` pair exists in the
            association table; ``False`` otherwise.
        """
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_roles_for_user(self, user_id: int) -> list[Role]:
        """
        Retrieve all roles currently assigned to a given user.

        Used by the authorization layer to determine what actions
        the user is permitted to perform.

        Parameters
        ----------
        user_id : int
            Primary key of the user whose roles are being fetched.

        Returns
        -------
        list[Role]
            A list of ``Role`` instances assigned to the user.
            Returns an empty list if no roles are assigned.

        Notes
        -----
        The composite index on ``(user_id, role_id)`` with ``user_id``
        as the leading column allows PostgreSQL to satisfy this query
        with an index range scan rather than a full table scan.
        """
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())