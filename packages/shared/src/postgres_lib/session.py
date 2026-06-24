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

# packages/shared/src/postgres_lib/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .config import postgres_config


async_engine = create_async_engine(
    postgres_config.database_url,
    echo=postgres_config.echo,

    # Enables SQLAlchemy 2.0-style API semantics, ensuring forward compatibility
    # and consistent behavior across future versions.
    future=True
)
"""
Asynchronous SQLAlchemy database engine configured via application settings.
"""

async_session_factory = async_sessionmaker(
    autocommit=postgres_config.autocommit,
    autoflush=postgres_config.autoflush,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=postgres_config.expire_on_commit
)
"""
Asynchronous session factory configured according to application-wide database behavior policies.
"""

