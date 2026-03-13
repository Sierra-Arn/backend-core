# app/shared/postgres/db/models/role_permission.py
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .types import Permission, PermissionSQL

if TYPE_CHECKING:
    from .role import Role


class RolePermission(Base):
    """
    Association table linking roles to their assigned permissions.

    Each record represents a single permission granted to a role.
    A role may have multiple permissions; each ``(role_id, permission)``
    pair is unique, preventing duplicate assignments.

    Attributes
    ----------
    id : int
        Auto-generated surrogate primary key.
    role_id : int
        Foreign key referencing the role this permission is assigned to.
    permission : Permission
        The permission value from the ``Permission`` enum
        (e.g., ``"users:delete"``).

    Notes
    -----
    The composite unique constraint on ``(role_id, permission)`` enforces
    that the same permission cannot be assigned to the same role twice
    at the database level.
    """

    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint("role_id", "permission", name="uq_role_permissions_role_permission"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        comment="Foreign key referencing the role this permission is assigned to.",
    )
    permission: Mapped[Permission] = mapped_column(
        PermissionSQL,
        nullable=False,
        comment="Permission granted to the role.",
    )

    role: Mapped["Role"] = relationship(back_populates="permissions")