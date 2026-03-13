# app/shared/postgres/db/models/types.py
from enum import StrEnum
from sqlalchemy import Enum as SQLEnum


class Permission(StrEnum):
    """
    Enumeration of all permissions that can be assigned to roles.

    Permissions follow the ``resource:action`` naming convention, making
    it immediately clear which resource is affected and what operation
    is being performed.

    - ``"users:get_all"``: Retrieve the full list of registered users.
    - ``"users:manage_roles"``: Assign or remove roles from a user.
    - ``"roles:create"``: Create a new role in the system.
    - ``"roles:manage_permissions"``: Assign or remove permissions from a role.

    Notes
    -----
    - This enum inherits from `enum.StrEnum`, meaning each member is a native `str` instance.
      Therefore, it can be used directly in any context expecting a string
      without needing to access the `.value` attribute.
    - The string values are fixed and must not be changed without a corresponding
      database migration, as they are persisted in persistent storage.
    """

    USERS_GET_ALL            = "users:get_all"
    USERS_MANAGE_ROLES       = "users:manage_roles"
    ROLES_CREATE             = "roles:create"
    ROLES_MANAGE_PERMISSIONS = "roles:manage_permissions"


PermissionSQL = SQLEnum(
    Permission,
    name="permission",
    values_callable=lambda x: [e.value for e in x],
)
"""
SQLAlchemy-compatible enum type representing valid permissions in the database.

This type maps the ``Permission`` Python enum to a persistent, named ``ENUM`` type in the
underlying relational database. It ensures data integrity by restricting column values
to only the predefined set of valid permissions.

The named enum type (``permission``) appears explicitly in the database schema, improving
introspectability, readability of migrations, and compatibility with database tooling.

Notes
-----
Schema consistency: Changing the members or string values of ``Permission`` requires
a corresponding database migration to alter the ``permission`` enum, as existing data
must remain compatible.
"""