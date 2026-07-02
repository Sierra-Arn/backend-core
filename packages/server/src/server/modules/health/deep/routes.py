# Copyright (c) 2026 Ilya Snegov (aka Sierra Arn)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# packages/server/src/server/modules/health/deep/routes.py
import asyncio
from fastapi import status
from .schemas import DeepHealthResponse
from .domen import (
    check_postgres,
    check_blacklist_redis,
    check_refresh_token_redis,
    check_rate_limit_redis,
)
from ..router import health_router
from ..types import ServiceStatus
from ....config import server_config


@health_router.get(
    "/deep/",
    status_code=status.HTTP_200_OK,
    response_model=DeepHealthResponse,
    summary="Deep health check",
    description=(
        "Returns the availability status of the application and all its "
        "dependencies. Each field indicates whether the corresponding service "
        "is reachable. If the overall probe exceeds the configured timeout "
        "every dependency is marked unavailable."
    ),
)
async def deep_health_route() -> DeepHealthResponse:
    """
    Execute concurrent health probes for all external dependencies.

    Runs PostgreSQL and all three Redis database checks in parallel via
    asyncio.gather. If all probes succeed the overall status is OK; if any
    probe fails the overall status is DEGRADED so that orchestrators can
    route traffic away from the instance or trigger an alert without marking
    it fully unavailable.

    Returns
    -------
    DeepHealthResponse
        Aggregated health status for the instance and each dependency.

    Notes
    -----
    All probes must complete within server_config.deep_health_timeout seconds.
    On timeout every dependency is marked UNAVAILABLE and the overall status
    is set to UNAVAILABLE to signal orchestrators that the instance cannot
    serve traffic safely.
    """
    try:
        postgres, blacklist_redis, refresh_token_redis, rate_limit_redis = (
            await asyncio.wait_for(
                asyncio.gather(
                    check_postgres(),
                    check_blacklist_redis(),
                    check_refresh_token_redis(),
                    check_rate_limit_redis(),
                ),
                timeout=server_config.deep_health_timeout,
            )
        )
    except asyncio.TimeoutError:
        unavailable = ServiceStatus.UNAVAILABLE
        return DeepHealthResponse(
            status=unavailable,
            postgres=unavailable,
            blacklist_redis=unavailable,
            refresh_token_redis=unavailable,
            rate_limit_redis=unavailable,
        )

    overall = (
        ServiceStatus.OK
        if all(
            s == ServiceStatus.OK
            for s in (postgres, blacklist_redis, refresh_token_redis, rate_limit_redis)
        )
        else ServiceStatus.DEGRADED
    )

    return DeepHealthResponse(
        status=overall,
        postgres=postgres,
        blacklist_redis=blacklist_redis,
        refresh_token_redis=refresh_token_redis,
        rate_limit_redis=rate_limit_redis,
    )