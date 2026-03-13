# app/modules/auth/register/schemas.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from ....shared.schemas import EmailMixin, PasswordMixin


class RegisterRequest(EmailMixin, PasswordMixin, BaseModel):
    """Request body for creating a new user account."""

    # Pydantic schemas are rendered directly in Swagger UI —
    # class-level docstrings appear as endpoint descriptions and are parsed
    # as Markdown. For this reason, numpy-style docstrings are avoided here
    # in favor of concise single-line descriptions.

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