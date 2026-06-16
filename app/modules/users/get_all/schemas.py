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

# app/modules/users/get_all/schemas.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    """Represents a single user record in the paginated response."""

    id: int = Field(description="Unique identifier of the user.")
    email: str = Field(description="Email address of the user.")
    bio: str | None = Field(description="Optional biographical text provided by the user.")
    roles: list[RoleSchema] = Field(description="List of role names assigned to the user.")
    created_at: datetime = Field(description="Timestamp of when the account was created.")

    model_config = ConfigDict(from_attributes=True)

class RoleSchema(BaseModel):
    """Represents a single role assigned to a user."""

    id: int = Field(description="Unique identifier of the role.")
    name: str = Field(description="Unique role name used in RBAC checks.")
    created_at: datetime = Field(description="Timestamp of when the role was created.")

    model_config = ConfigDict(from_attributes=True)

class GetAllUsersResponse(BaseModel):
    """Response body for the paginated user list."""

    users: list[UserSchema] = Field(description="List of user records for the current page.")
    total: int = Field(description="Total number of users in the database.")
    skip: int = Field(description="Number of records skipped.")
    limit: int = Field(description="Maximum number of records returned.")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "users": [
                        {
                            "id": 1,
                            "email": "user@example.com",
                            "bio": "Software engineer.",
                            "roles": [
                                {
                                    "id": 1,
                                    "name": "user",
                                    "created_at": "2024-01-01T00:00:00Z",
                                }
                            ],
                            "created_at": "2024-01-01T00:00:00Z",
                        }
                    ],
                    "total": 1,
                    "skip": 0,
                    "limit": 100,
                }
            ]
        }
    )