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

# packages/server/src/server/modules/admin/roles/get/schemas.py
from pydantic import BaseModel, ConfigDict
from schemas_lib import IdMixin, CreatedAtMixin, NameMixin


class RoleResponse(IdMixin, NameMixin, CreatedAtMixin, BaseModel):
    """
    Response body containing the record of a defined role.
    """

    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "admin",
                    "created_at": "2024-05-20T14:30:00Z",
                }
            ]
        },
    )