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

# app/shared/logging/config.py
import logging
from enum import StrEnum
from typing import ClassVar
from pydantic import field_validator
from ..base_config import BaseConfig


class LogLevel(StrEnum):
    """
    Enumeration of supported log levels in ascending order of severity.

    Attributes
    ----------
    DEBUG : str
        Fine-grained diagnostic information: variable values, control flow,
        internal state. Development use only — too verbose for production.
    INFO : str
        General operational events confirming the application is working
        as expected (e.g., server started, request handled, job completed).
    WARNING : str
        Unexpected situations that do not interrupt normal operation but
        may indicate misconfiguration or a future failure.
    ERROR : str
        Failures that prevented a specific operation from completing
        (e.g., database query failed, external service unreachable).
    CRITICAL : str
        Severe failures threatening the stability of the entire application
        (e.g., unable to connect to the database on startup, data loss risk).
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingConfig(BaseConfig):
    """
    Configuration schema for the logging service.

    Attributes
    ----------
    level : LogLevel
        Minimum log level to emit. All messages below this level are
        silently discarded. Default is ``LogLevel.INFO``.
    record_format : str
        Format string passed to the JSON formatter. Controls which
        standard ``logging.LogRecord`` fields are included in every
        JSON record. Default includes timestamp, level, logger name,
        and message.
    propagate : bool
        Whether log records are passed to the handlers of parent loggers
        in the hierarchy. Default is ``False``.

    Notes
    -----
    This class inherits from `app.shared.base_config.BaseConfig`.
    For details on configuration loading behavior, see its documentation.
    """

    env_prefix: ClassVar[str] = "LOGGING_"

    level: LogLevel = LogLevel.INFO
    record_format: str = "%(asctime)s %(levelname)s %(name)s %(message)s"
    propagate: bool = False

    @field_validator("record_format")
    @classmethod
    def validate_record_format(cls, v: str) -> str:
        """
        Ensure the format string references only valid ``logging.LogRecord``
        fields.

        Constructs a ``Formatter`` and a dummy ``LogRecord``, then runs the
        full formatting pipeline against them. This catches unknown field
        references at startup — before the application begins accepting
        requests — rather than at the moment a log entry is emitted.

        Parameters
        ----------
        v : str
            The format string to validate.

        Returns
        -------
        str
            The original format string, unchanged, if valid.

        Raises
        ------
        ValueError
            If the format string contains an unknown or malformed field
            reference.
        """

        try:
            formatter = logging.Formatter(fmt=v)
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="",
                lineno=0, msg="test", args=(), exc_info=None,
            )
            formatter.format(record)
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid record_format: {e}") from e
        return v

    @property
    def format(self) -> str:
        """
        Return the log record format.

        Returns
        -------
        str
            Always ``"json"``.

        Notes
        -----
        JSON is the only supported format because it is machine-readable
        by default — any log aggregation system (Elasticsearch, Grafana
        Loki, CloudWatch, etc.) can ingest and query it without custom
        parsing rules. Plain text requires fragile regex parsers that
        break whenever the message template changes.
        """

        return "json"

    @property
    def handler(self) -> str:
        """
        Return the log output destination.

        Returns
        -------
        str
            Always ``"console"``.

        Notes
        -----
        Console (stdout) is the only supported handler because writing logs 
        to a file introduces operational overhead with no real benefit: 
        log files grow unboundedly and require a rotation strategy
        (e.g., ``logrotate``, ``RotatingFileHandler``) to prevent disk
        exhaustion. In a containerized environment the problem is worse —
        any file written inside a container is destroyed when the container
        stops, so logs would need to be forwarded to external storage anyway.

        Writing to stdout sidesteps both problems: the container runtime
        captures it automatically and pipes it to whatever log aggregation
        infrastructure is in place, without any extra configuration inside
        the application.
        """

        return "console"


# Initialize logging configuration singleton.
# Since logging settings are static for the application's lifetime
# and any configuration changes require a full application restart,
# it is safe to instantiate the config once at module level and reuse
# it throughout the application as a singleton.
logging_config = LoggingConfig()