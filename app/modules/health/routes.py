# app/modules/health/routes.py
import asyncio
from fastapi import APIRouter, status
from .schemas import HealthResponse, ServiceStatus
from .domen import check_postgres, check_redis


health_router = APIRouter(prefix="/health", tags=["health"])


@health_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=HealthResponse,
    summary="Health check",
    description=(
        "Returns the availability status of the application and its "
        "dependencies. Each field is either ``ok`` or ``unavailable``."
    ),
)
async def health_route() -> HealthResponse:
    results = await asyncio.gather(
        check_postgres(),
        check_redis()
    )

    postgres_status, redis_status = results

    overall = (
        ServiceStatus.OK
        if all(s == ServiceStatus.OK for s in results)
        else ServiceStatus.DEGRADED
    )

    return HealthResponse(
        status=overall,
        postgres=postgres_status,
        redis=redis_status
    )