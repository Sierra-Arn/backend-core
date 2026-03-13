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