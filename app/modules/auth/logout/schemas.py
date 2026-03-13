# app/modules/auth/logout/schemas.py
from pydantic import BaseModel, ConfigDict
from ....shared.schemas import AccessTokenMixin, RefreshTokenMixin


class LogoutRequest(AccessTokenMixin, RefreshTokenMixin, BaseModel):
    """Request body for terminating the current session."""
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