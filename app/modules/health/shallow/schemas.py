# app/modules/health/shallow/schemas.py
from pydantic import BaseModel, ConfigDict, Field
from ..base_schemas import ServiceStatus


class ShallowHealthResponse(BaseModel):
    """Response body describing the availability of the application."""

    status: ServiceStatus = Field(
        description="Overall application status. ``ok`` if the application is running and accepting requests.",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "status": "ok",
                }
            ]
        },
    )