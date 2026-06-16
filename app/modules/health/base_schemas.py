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

# app/modules/health/base_schemas.py
from enum import StrEnum
 
 
class ServiceStatus(StrEnum):
    """
    Enumeration of possible availability states for the application
    and its dependencies.
 
    Attributes
    ----------
    OK : str
        The service is reachable and operating normally.
    DEGRADED : str
        The application is running but one or more dependencies are
        unavailable. Requests that rely on the affected dependency will fail.
    UNAVAILABLE : str
        The service could not be reached or did not respond successfully.
    """
 
    OK = "ok"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"