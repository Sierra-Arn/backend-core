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

# packages/server/src/server/modules/health/deep/schemas.py
from pydantic import BaseModel, ConfigDict, Field
from ..types import ServiceStatus


class DeepHealthResponse(BaseModel):
    """
    Response body for the deep health check endpoint.

    Reports the operational status of the application and each external
    dependency. Used for comprehensive readiness probes and diagnostic
    dashboards.
    """

    status: ServiceStatus = Field(
        description=(
            "Overall application status derived from dependency states. "
            "Returns ok when all critical services are reachable; "
            "degraded when one or more are unavailable; "
            "unavailable when the health check timed out entirely."
        )
    )
    postgres: ServiceStatus = Field(
        description="PostgreSQL availability. ok if a test query succeeds; unavailable otherwise."
    )
    blacklist_redis: ServiceStatus = Field(
        description="JWT blacklist Redis availability. ok if a PING command succeeds; unavailable otherwise."
    )
    refresh_token_redis: ServiceStatus = Field(
        description="Refresh token Redis availability. ok if a PING command succeeds; unavailable otherwise."
    )
    rate_limit_redis: ServiceStatus = Field(
        description="Rate limiting Redis availability. ok if a PING command succeeds; unavailable otherwise."
    )

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "status": "ok",
                    "postgres": "ok",
                    "blacklist_redis": "ok",
                    "refresh_token_redis": "ok",
                    "rate_limit_redis": "ok",
                }
            ]
        },
    )