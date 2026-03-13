# app/modules/health/schemas.py
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field
 
 
class ServiceStatus(StrEnum):
    """
    Enumeration of possible availability states for the application
    and its dependencies.
 
    Attributes
    ----------
    OK : str
        The service is reachable and operating normally.
    DEGRADED : str
        The application is running but one or more dependencies are
        unavailable. Requests that rely on the affected dependency will fail.
    UNAVAILABLE : str
        The service could not be reached or did not respond successfully.
    """
 
    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
 
 
class HealthResponse(BaseModel):
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