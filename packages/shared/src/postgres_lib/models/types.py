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
from auth_lib import PermissionEnum


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