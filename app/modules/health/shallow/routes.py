# app/modules/health/shallow/routes.py
from fastapi import status
from .schemas import ShallowHealthResponse, ServiceStatus
from ..router import health_router


@health_router.get(
    "/shallow/",
    status_code=status.HTTP_200_OK,
    response_model=ShallowHealthResponse,
    summary="Shallow health check",
    description="Returns the availability status of the application.",
)
async def shallow_health_route() -> ShallowHealthResponse:
    return ShallowHealthResponse(status=ServiceStatus.OK)