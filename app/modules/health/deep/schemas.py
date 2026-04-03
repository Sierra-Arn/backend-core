# app/modules/health/deep/schemas.py
from pydantic import BaseModel, ConfigDict, Field
from ..base_schemas import ServiceStatus
 
 
class DeepHealthResponse(BaseModel):
    """Response body describing the availability of the application and its dependencies."""
 
    status: ServiceStatus = Field(
        description=(
            "Overall application status. ``ok`` if all dependencies are reachable; "
            "``degraded`` if one or more are unavailable."
        ),
    )
    postgres: ServiceStatus = Field(
        description="PostgreSQL availability. ``ok`` if a test query succeeds; ``unavailable`` otherwise.",
    )
    redis: ServiceStatus = Field(
        description="Redis availability. ``ok`` if a PING command succeeds; ``unavailable`` otherwise.",
    )
 
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "status": "ok",
                    "postgres": "ok",
                    "redis": "ok",
                }
            ]
        },
    )