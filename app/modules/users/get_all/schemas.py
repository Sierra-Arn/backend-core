# app/modules/users/get_all/schemas.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserSchema(BaseModel):
    """Represents a single user record in the paginated response."""

    id: int = Field(description="Unique identifier of the user.")
    email: str = Field(description="Email address of the user.")
    bio: str | None = Field(description="Optional biographical text provided by the user.")
    roles: list[str] = Field(description="List of role names assigned to the user.")
    created_at: datetime = Field(description="Timestamp of when the account was created.")

    model_config = ConfigDict(from_attributes=True)


class GetAllUsersResponse(BaseModel):
    """Response body for the paginated user list."""

    users: list[UserSchema] = Field(description="List of user records for the current page.")
    total: int = Field(description="Total number of users in the database.")
    skip: int = Field(description="Number of records skipped.")
    limit: int = Field(description="Maximum number of records returned.")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "users": [
                        {
                            "id": 1,
                            "email": "user@example.com",
                            "bio": "Software engineer.",
                            "roles": ["user"],
                            "created_at": "2024-01-01T00:00:00Z",
                        }
                    ],
                    "total": 1,
                    "skip": 0,
                    "limit": 100,
                }
            ]
        }
    )