# app/modules/auth/router.py
from fastapi import APIRouter


# prefix: prepended to all route paths in this router (e.g., "/auth/login")
# tags: used by OpenAPI to group endpoints under a named section in Swagger UI
auth_router = APIRouter(prefix="/auth", tags=["auth"])