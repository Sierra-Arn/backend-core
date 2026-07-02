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

# packages/shared/src/postgres_lib/models/types.py
from enum import StrEnum
from sqlalchemy import Enum as SQLEnum


class PermissionEnum(StrEnum):
    """
    Enumeration of all permissions that can be assigned to roles.

    Permissions follow the resource:action naming convention, making it
    immediately clear which resource is affected and what operation is
    being performed.

    Attributes
    ----------
    USERS_GET : PermissionEnum
        Retrieve a single user record by identifier.
    USERS_GET_ALL : PermissionEnum
        Retrieve the full list of registered users.
    USERS_UPDATE : PermissionEnum
        Modify fields on an existing user record.
    USERS_DELETE : PermissionEnum
        Permanently remove a user record from the system.
    USERS_MANAGE_ROLES : PermissionEnum
        Assign or remove roles from a user.
    ROLES_GET : PermissionEnum
        Retrieve a single role record by identifier.
    ROLES_GET_ALL : PermissionEnum
        Retrieve the full list of defined roles.
    ROLES_CREATE : PermissionEnum
        Create a new role in the system.
    ROLES_DELETE : PermissionEnum
        Permanently remove a role record from the system.
    ROLES_MANAGE_PERMISSIONS : PermissionEnum
        Assign or remove permissions from a role.

    Notes
    -----
    PermissionEnum inherits from StrEnum, meaning each member is a native str
    instance and can be used directly in any context expecting a string
    without accessing the .value attribute.

    The string values are fixed and must not be changed without a
    corresponding database migration, as they are persisted as a named
    PostgreSQL enum type.
    """

    USERS_GET                = "users:get"
    USERS_GET_ALL            = "users:get_all"
    USERS_UPDATE             = "users:update"
    USERS_DELETE             = "users:delete"
    USERS_MANAGE_ROLES       = "users:manage_roles"
    ROLES_GET                = "roles:get"
    ROLES_GET_ALL            = "roles:get_all"
    ROLES_CREATE             = "roles:create"
    ROLES_DELETE             = "roles:delete"
    ROLES_MANAGE_PERMISSIONS = "roles:manage_permissions"


class RoleEnum(StrEnum):
    """
    Enumeration of all roles available in the application.

    Attributes
    ----------
    USER : RoleEnum
        Default role assigned automatically to every newly registered account.
    ADMIN : RoleEnum
        Privileged role reserved for administrative operations.
    """

    USER = "user"
    ADMIN = "admin"


PermissionSQL = SQLEnum(
    *[e.value for e in PermissionEnum],
    name="permission",
)
"""
SQLAlchemy column type mapping the Permission enum to a named PostgreSQL enum.

Restricts column values at the database level to the predefined set of valid
permissions, ensuring data integrity independently of application-layer validation.
The named enum type appears explicitly in the schema, improving readability of
migrations and compatibility with database tooling.

Notes
-----
Changing the members or string values of Permission requires a corresponding
database migration to alter the permission enum type, as existing persisted
values must remain compatible.
"""