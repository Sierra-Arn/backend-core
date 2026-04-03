# app/modules/health/deep/domen.py
from sqlalchemy import text
from .schemas import ServiceStatus
from ....shared.postgres.db.session import engine
from ....shared.redis.db.client import async_redis_client
from ....shared.logging import get_logger


logger = get_logger(__name__)


async def check_postgres() -> ServiceStatus:
    """
    Verify that the database is reachable by executing a minimal query.

    Returns
    -------
    ServiceStatus
        ``ServiceStatus.OK`` if the connection succeeds;
        ``ServiceStatus.UNAVAILABLE`` otherwise.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return ServiceStatus.OK
    except Exception as e:
        logger.error(
            "PostgreSQL healthcheck failed",
            exc_info=e,
        )
        return ServiceStatus.UNAVAILABLE


async def check_redis() -> ServiceStatus:
    """
    Verify that Redis is reachable by sending a ``PING`` command.

    Returns
    -------
    ServiceStatus
        ``ServiceStatus.OK`` if the connection succeeds;
        ``ServiceStatus.UNAVAILABLE`` otherwise.
    """
    try:
        await async_redis_client.ping()
        return ServiceStatus.OK
    except Exception as e:
        logger.error(
            "Redis healthcheck failed",
            exc_info=e,
        )
        return ServiceStatus.UNAVAILABLE