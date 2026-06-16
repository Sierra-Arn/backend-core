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

# app/modules/roles/create/schemas.py
from pydantic import BaseModel, ConfigDict, Field


class CreateRoleRequest(BaseModel):
    """Request body for creating a new role."""

    name: str = Field(
        max_length=32,
        description="Unique name for the new role (e.g., ``'moderator'``).",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "moderator",
                }
            ]
        },
    )


class CreateRoleResponse(BaseModel):
    """Response body returned after successful role creation."""

    id: int = Field(description="Auto-generated primary key of the new role.")
    name: str = Field(description="Name of the created role.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 3,
                    "name": "moderator",
                }
            ]
        },
    )