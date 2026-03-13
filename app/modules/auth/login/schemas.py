# app/modules/auth/login/schemas.py
from pydantic import BaseModel, ConfigDict
from ....shared.schemas import EmailMixin, PasswordMixin, AccessTokenMixin, RefreshTokenMixin


class LoginRequest(EmailMixin, PasswordMixin, BaseModel):
    """Request body for authenticating an existing user."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "secret_password",
                }
            ]
        },
    )

class LoginResponse(AccessTokenMixin, RefreshTokenMixin, BaseModel):
    """Response body containing the token pair issued after successful login."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "dGhpcyBpcyBhIHJhbmRvbSBvcGFxdWUgdG9rZW4",
                }
            ]
        },
    )