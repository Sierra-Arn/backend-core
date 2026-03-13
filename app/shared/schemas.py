# app/shared/schemas.py
from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    """
    Uniform error response body returned for all handled exceptions.

    The status_code field intentionally mirrors the HTTP response status code.
    Although the code is already present in the response headers, including it
    in the body makes the payload self-contained: clients that log or forward
    only the JSON body retain the full context without needing to inspect
    headers separately.
    """

    status_code: int = Field(
        description="HTTP status code of the response (e.g., 404, 422, 500).",
    )
    error: str = Field(
        description=(
            "Short human-readable name for the error, derived from the HTTP "
            "status phrase (e.g., 'Not Found', 'Unprocessable Entity')."
        )
    )
    detail: str = Field(
        description=(
            "Specific description of what went wrong. Should be informative "
            "enough for the client to understand the cause without exposing "
            "internal implementation details."
        )
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "status_code": 404,
                    "error": "Not Found",
                    "detail": "User with id 42 does not exist",
                }
            ]
        }
    )


class EmailMixin:
    email: str = Field(
        ...,
        description=(
            "Email address associated with the account. "
            "Must match an existing registered user."
        ),
    )


class PasswordMixin:
    password: str = Field(
        ...,
        description=(
            "Plaintext password for the account. "
            "Never stored or logged — hashed immediately via bcrypt before persistence."
        ),
    )


class AccessTokenMixin:
    access_token: str = Field(
        ...,
        description=(
            "Short-lived JWT access token. "
            "Include in the Authorization header as: Bearer <token>."
        ),
    )


class RefreshTokenMixin:
    refresh_token: str = Field(
        ...,
        description=(
            "Long-lived opaque refresh token. "
            "Use to obtain a new access token when the current one expires."
        ),
    )