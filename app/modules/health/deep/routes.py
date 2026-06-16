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

# app/modules/health/deep/routes.py
import asyncio
from fastapi import status
from .schemas import DeepHealthResponse, ServiceStatus
from .domen import check_postgres, check_redis
from ..router import health_router


@health_router.get(
    "/deep/",
    status_code=status.HTTP_200_OK,
    response_model=DeepHealthResponse,
    summary="Deep Health check",
    description=(
        "Returns the availability status of the application and its "
        "dependencies. Each field is either ``ok`` or ``unavailable``."
    ),
)
async def deep_health_route() -> DeepHealthResponse:
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

    return DeepHealthResponse(
        status=overall,
        postgres=postgres_status,
        redis=redis_status
    )