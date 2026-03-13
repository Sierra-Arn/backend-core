# app/shared/postgres/db/models/role.py
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, IdMixin, CreatedAtMixin

if TYPE_CHECKING:
    from .user import User
    from .role_permission import RolePermission


class Role(Base, IdMixin, CreatedAtMixin):
    """
    Represents a named role that can be assigned to users.

    Attributes
    ----------
    name : Mapped[str]
        Unique human-readable identifier for the role.
        Used during RBAC checks to determine what actions a user may perform.
    users : Mapped[list[User]]
        Back-populated collection of all users assigned this role.
        Loaded via the ``user_roles`` association table.
    permissions : Mapped[list[RolePermission]]
        Collection of permissions assigned to this role.
        Loaded via the ``role_permissions`` association table.
        Deleted automatically when the role is deleted (cascade).

    Notes
    -----
    ``name`` is declared with ``unique=True``, which causes PostgreSQL to
    automatically create a unique B-tree index on the column. This index
    serves two purposes:

    1. **Uniqueness enforcement.** PostgreSQL rejects any insertion that would
       produce a duplicate role name, guaranteeing that each role exists
       exactly once in the system regardless of how many times it is referenced.
    2. **RBAC check performance.** Permission checks fetch roles by name
       (e.g., ``"admin"``, ``"user"``). Without the index, each such
       lookup would require a full table scan. The B-tree index reduces each
       lookup to O(log n), keeping permission checks fast even as the number
       of defined roles grows.
    """

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        nullable=False,
        comment="Unique role name used in RBAC checks",
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
    )
    permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )