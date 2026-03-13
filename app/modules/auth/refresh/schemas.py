# app/modules/auth/refresh/schemas.py
from pydantic import BaseModel, ConfigDict
from ....shared.schemas import RefreshTokenMixin, AccessTokenMixin


class RefreshRequest(RefreshTokenMixin, BaseModel):
    """Request body for rotating the current token pair."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "refresh_token": "dGhpcyBpcyBhIHJhbmRvbSBvcGFxdWUgdG9rZW4",
                }
            ]
        },
    )

class RefreshResponse(AccessTokenMixin, RefreshTokenMixin, BaseModel):
    """Response body containing the new token pair issued after successful rotation."""

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