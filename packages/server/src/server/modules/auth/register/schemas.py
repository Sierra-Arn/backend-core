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

# packages/server/src/server/modules/auth/register/schemas.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from schemas_lib import EmailMixin, PasswordMixin


class RegisterRequest(EmailMixin, PasswordMixin, BaseModel):
    """
    Request body for creating a new user account.

    Attributes
    ----------
    is_not_bot : bool
        Placeholder for CAPTCHA verification. Must be True to confirm the
        request originates from a human user. Rejected with a validation
        error if False.
    """

    is_not_bot: bool = Field(
        ...,
        description=(
            "Placeholder for CAPTCHA verification. "
            "Must be True to confirm the request originates from a human user."
        ),
    )

    @field_validator("is_not_bot")
    @classmethod
    def must_be_true(cls, v: bool) -> bool:
        if not v:
            raise ValueError("CAPTCHA verification failed.")
        return v

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "secret_password",
                    "is_not_bot": True,
                }
            ]
        },
    )