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