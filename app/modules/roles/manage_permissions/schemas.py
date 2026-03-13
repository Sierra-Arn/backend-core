# app/modules/roles/manage_permissions/schemas.py
from pydantic import BaseModel, ConfigDict, Field
from ....shared.postgres.db.models import Permission


class AssignPermissionRequest(BaseModel):
    """Request body for assigning a permission to a role."""

    permission: Permission = Field(
        description="Permission to assign to the role.",
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "permission": "users:get_all",
                }
            ]
        },
    )