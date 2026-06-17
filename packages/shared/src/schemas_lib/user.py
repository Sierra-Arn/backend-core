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

# packages/shared/src/schemas_lib/user.py
from datetime import datetime
from pydantic import Field


class IdMixin:
    """
    Shared id field for response schemas that expose a surrogate primary key.
    """

    id: int = Field(
        description="Surrogate primary key of the record.",
    )


class EmailMixin:
    """
    Shared email field for request schemas that require account identification.
    """

    email: str = Field(
        description=(
            "Email address associated with the account. "
            "Must match an existing registered user."
        ),
    )


class PasswordMixin:
    """
    Shared password field for request schemas that accept plaintext credentials.
    """

    password: str = Field(
        description=(
            "Plaintext password for the account. "
            "Never stored or logged — hashed immediately via bcrypt before persistence."
        ),
    )


class IsVerifiedMixin:
    """
    Shared is_verified field for response schemas that expose account verification status.
    """

    is_verified: bool = Field(
        description="True once the user confirms their email address.",
    )


class BioMixin:
    """
    Shared bio field for response schemas that expose optional biographical text.
    """

    bio: str | None = Field(
        description="Optional free-form biographical text provided by the user.",
    )


class CreatedAtMixin:
    """
    Shared created_at field for response schemas that expose record creation timestamp.
    """

    created_at: datetime = Field(
        description="Timezone-aware timestamp of record creation in UTC.",
    )