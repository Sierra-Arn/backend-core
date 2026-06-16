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

# app/modules/account/change_password/schemas.py
from pydantic import BaseModel, ConfigDict, Field, field_validator, ValidationInfo
from ....shared.schemas import RefreshTokenMixin, PasswordMixin


class ChangePasswordRequest(PasswordMixin, RefreshTokenMixin, BaseModel):
    """Request body for changing the authenticated user's password."""

    new_password: str = Field(
        description="The user's new plaintext password to replace the current one.",
    )

    @field_validator("new_password")
    @classmethod
    def passwords_must_differ(cls, v: str, info: ValidationInfo) -> str:
        if v == info.data.get("current_password"):
            raise ValueError("New password must differ from the current password.")
        return v

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "password": "old_secret_password",
                    "new_password": "new_secret_password",
                    "refresh_token": "dGhpcyBpcyBhIHJhbmRvbSBvcGFxdWUgdG9rZW4",
                }
            ]
        },
    )