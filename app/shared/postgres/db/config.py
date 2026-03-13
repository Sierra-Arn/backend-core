# app/shared/postgres/db/config.py
from typing import ClassVar
from urllib.parse import quote_plus
from pydantic import Field
from ...base_config import BaseConfig


class PostgresConfig(BaseConfig):
    """
    Configuration schema for PostgreSQL database.

    Attributes
    ----------
    host : str
        Hostname or IP address of the PostgreSQL server. Default is `"127.0.0.1"`.
    external_port : int
        TCP port the server listens on. Must be in the range 1-65535.
        Default is `5432` (standard PostgreSQL port).
    user_name : str
        Database user name.
    user_password : str
        Database user password.
    user_db_name : str
        Name of the PostgreSQL database to connect to.
    echo : bool, optional
        Enables or disables SQL statement logging to stdout.
        Useful for debugging during development; should be `False` in production.
        Default is `False`.
    autocommit : bool, optional
        Controls whether SQLAlchemy sessions automatically commit transactions.
        When `False` (recommended), explicit `commit()` calls are required.
        Default is `False`.
    autoflush : bool, optional
        Controls whether pending ORM changes are automatically flushed before queries.
        When `False` (recommended), flushing is manual, giving full control over side effects.
        Default is `False`.
    expire_on_commit : bool, optional
        Determines whether ORM objects are expired (i.e., their attributes detached from the session)
        immediately after a transaction is committed. Default is `False`.
        
    Notes
    -----
    This class inherits from `app.base_config.BaseConfig`.
    For details on configuration loading behavior, see its documentation.
    """

    env_prefix: ClassVar[str] = "POSTGRES_"

    host: str = "127.0.0.1"
    external_port: int = Field(default=5432, ge=1, le=65535)
    user_name: str
    user_password: str
    user_db_name: str
    echo: bool = False
    autocommit: bool = False
    autoflush: bool = False
    expire_on_commit: bool = False

    @property
    def sync_database_url(self) -> str:
        """
        Build synchronous PostgreSQL database connection URL from configuration settings.

        This property is intended **exclusively for use by Alembic migrations**, 
        which require a synchronous SQLAlchemy engine and do not support async drivers.
        
        In all other parts of the application, the asynchronous connection URL 
        (`async_database_url`) must be used instead.

        Returns
        -------
        str
            Complete PostgreSQL connection URL with credentials in the format:
            postgresql+psycopg2://username:password@host:port/db_name
        
        Notes
        -----
        The password is URL-encoded using `quote_plus` to safely handle
        special characters that might be present in the password string.
        """

        return (
            f"postgresql+psycopg2://{self.user_name}:{quote_plus(self.user_password)}"
            f"@{self.host}:{self.external_port}/{self.user_db_name}"
        )
    
    @property
    def async_database_url(self) -> str:
        """
        Build asynchronous PostgreSQL database connection URL from configuration settings.

        Returns
        -------
        str
            Complete PostgreSQL connection URL with credentials in the format:
            postgresql+asyncpg://username:password@host:port/db_name
        
        Notes
        -----
        The password is URL-encoded using `quote_plus` to safely handle
        special characters that might be present in the password string.
        """

        return (
            f"postgresql+asyncpg://{self.user_name}:{quote_plus(self.user_password)}"
            f"@{self.host}:{self.external_port}/{self.user_db_name}"
        )


# Initialize PostgreSQL configuration singleton
# Since PostgreSQL database settings are static for the application's lifetime
# and any configuration changes require a full application restart,
# it is safe to instantiate the config once at module level and reuse
# it throughout the application as a singleton.
postgres_config = PostgresConfig()