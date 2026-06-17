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

# packages/server/src/server/modules/admin/users/update/schemas.py
from pydantic import BaseModel, ConfigDict, Field


class UpdateUserRequest(BaseModel):
    """
    Request body for partially updating a user record.

    All fields are optional. Only fields explicitly provided in the request
    body are applied — absent fields are ignored and leave the current value
    unchanged. This is determined via model_fields_set after validation.

    Passing null for bio explicitly clears the field. Passing null for
    password or is_verified is treated as absent and ignored.
    """

    password: str | None = Field(
        default=None,
        description=(
            "New plaintext password to replace the current one. "
            "Hashed immediately via bcrypt before persistence. "
            "Omit to leave the current password unchanged."
        ),
    )
    is_verified: bool | None = Field(
        default=None,
        description=(
            "Verification status to set on the account. "
            "Omit to leave the current value unchanged."
        ),
    )
    bio: str | None = Field(
        default=None,
        max_length=512,
        description=(
            "New biographical text to store. "
            "Pass null explicitly to clear the field. "
            "Omit to leave the current value unchanged."
        ),
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "password": "new_secret_password",
                    "is_verified": True,
                    "bio": "Updated bio text.",
                },
                {
                    "password": "new_secret_password",
                },
                {
                    "is_verified": True,
                    "bio": None,
                },
            ]
        },
    )