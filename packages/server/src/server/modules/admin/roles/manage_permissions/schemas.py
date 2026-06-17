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

# packages/server/src/server/modules/admin/roles/manage_permissions/schemas.py
from pydantic import BaseModel, ConfigDict, Field
from auth_lib import PermissionEnum


class AssignPermissionRequest(BaseModel):
    """
    Request body for assigning a permission to a role.
    """

    permission: PermissionEnum = Field(
        description="Permission value to assign to the role.",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "permission": "users:get_all",
                }
            ]
        },
    )


class RevokePermissionRequest(BaseModel):
    """
    Request body for revoking a permission from a role.
    """

    permission: PermissionEnum = Field(
        description="Permission value to revoke from the role.",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "permission": "users:get_all",
                }
            ]
        },
    )