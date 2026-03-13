# app/modules/account/change_bio/schemas.py
from pydantic import BaseModel, ConfigDict, Field


class ChangeBioRequest(BaseModel):
    """Request body for updating the authenticated user's biographical text."""

    bio: str | None = Field(
        description=(
            "Free-form biographical text to display on the user's profile. "
            "Pass ``null`` to clear the field."
        ),
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "bio": "Software engineer passionate about open source.",
                }
            ]
        },
    )