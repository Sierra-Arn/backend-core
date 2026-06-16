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

# app/config.py
from typing import ClassVar
from .shared import BaseConfig


class APIConfig(BaseConfig):
    """
    Configuration for the FastAPI server.

    Attributes
    ----------
    title : str
        Human-readable title of the API. Displayed in the generated
        OpenAPI schema and `/docs` UI. Default is `"Backend Core"`.
    description : str
        Detailed description of the API's purpose. Used in documentation UI.
        Default is `"An educational project demonstrating how to build a backend server with Python, 
        covering authentication, authorization, rate limiting, access logging and global error handling."`.
    version : str
        Semantic version string of the server API. Default is `"0.1.0"`.
    docs_url : str or None
        URL path for the Swagger UI. Set to ``None`` to disable.
        Default is ``"/docs"``.
    redoc_url : str or None
        URL path for the ReDoc UI. Set to ``None`` to disable.
        Default is ``"/redoc"``.
    openapi_url : str or None
        URL path for the raw OpenAPI JSON schema. Setting this to ``None``
        also implicitly disables both ``/docs`` and ``/redoc``, as they
        depend on the schema to render. Default is ``/openapi.json``.

    Notes
    -----
    This class inherits from `app.shared.base_config.BaseConfig`.
    For details on configuration loading behavior, see its documentation.
    """

    env_prefix: ClassVar[str] = "API_"

    title: str = "Backend Core"
    description: str = (
        "An educational project demonstrating how to build a backend server with Python, "
        "covering token-based authentication, role-based authorization with permissions, "
        "rate limiting, and structured error handling."
    )
    version: str = "0.1.0"
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"
    openapi_url: str | None = "/openapi.json"


api_config = APIConfig()