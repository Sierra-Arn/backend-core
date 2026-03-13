# app/modules/roles/create/schemas.py
from pydantic import BaseModel, ConfigDict, Field


class CreateRoleRequest(BaseModel):
    """Request body for creating a new role."""

    name: str = Field(
        max_length=32,
        description="Unique name for the new role (e.g., ``'moderator'``).",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "name": "moderator",
                }
            ]
        },
    )


class CreateRoleResponse(BaseModel):
    """Response body returned after successful role creation."""

    id: int = Field(description="Auto-generated primary key of the new role.")
    name: str = Field(description="Name of the created role.")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 3,
                    "name": "moderator",
                }
            ]
        },
    )