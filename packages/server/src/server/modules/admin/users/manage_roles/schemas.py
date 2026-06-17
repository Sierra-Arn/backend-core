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

# packages/server/src/server/modules/admin/users/manage_roles/schemas.py
from pydantic import BaseModel, ConfigDict, Field


class AssignRoleRequest(BaseModel):
    """
    Request body for assigning a role to a user.
    """

    role_id: int = Field(
        description="Primary key of the role to assign to the user.",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "role_id": 1,
                }
            ]
        },
    )


class RevokeRoleRequest(BaseModel):
    """
    Request body for revoking a role from a user.
    """

    role_id: int = Field(
        description="Primary key of the role to revoke from the user.",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "role_id": 1,
                }
            ]
        },
    )