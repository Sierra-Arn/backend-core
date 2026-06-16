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

# app/shared/logging/logger.py
import logging
import sys
from pythonjsonlogger.jsonlogger import JsonFormatter
from .config import logging_config


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger configured for JSON output to stdout.

    If the logger has already been configured (i.e., it already has
    handlers attached), the existing instance is returned as-is to
    prevent duplicate log entries when the function is called multiple
    times with the same name.

    Parameters
    ----------
    name : str
        Logger name. By convention, pass ``__name__`` from the calling
        module so that log records carry the fully qualified module path
        (e.g., ``app.api.routes.auth``), making it easy to trace the
        origin of a message in aggregated logs.

    Returns
    -------
    logging.Logger
        Configured logger instance ready to emit JSON records.
    """
    
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging_config.level)

    handler = logging.StreamHandler(sys.stdout)
    json_formatter = JsonFormatter(logging_config.record_format)
    handler.setFormatter(json_formatter)

    logger.addHandler(handler)
    logger.propagate = logging_config.propagate

    return logger