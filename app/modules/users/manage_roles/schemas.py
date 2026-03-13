# app/modules/users/manage_roles/schemas.py
from pydantic import BaseModel, ConfigDict, Field


class AssignRoleRequest(BaseModel):
    """Request body for assigning a role to a user."""

    role_name: str = Field(
        description="Name of the role to assign (e.g., ``'admin'``, ``'user'``).",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "role_name": "admin",
                }
            ]
        },
    )