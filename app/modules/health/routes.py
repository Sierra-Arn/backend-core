# app/modules/health/routes.py
from fastapi import APIRouter, status
from .schemas import HealthResponse, ServiceStatus
from .domen import check_postgres, check_redis


health_router = APIRouter()


@health_router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Returns the availability status of the application and its "
        "dependencies. Each field is either ``ok`` or ``unavailable``."
    ),
)
async def health_route() -> HealthResponse:
    postgres_status = await check_postgres()
    redis_status = await check_redis()

    overall = (
        ServiceStatus.OK
        if postgres_status == ServiceStatus.OK and redis_status == ServiceStatus.OK
        else ServiceStatus.DEGRADED
    )

    return HealthResponse(
        status=overall,
        postgres=postgres_status,
        redis=redis_status,
    )