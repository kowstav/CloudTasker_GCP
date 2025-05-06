# import json
import logging
from typing import Any, Dict

from pythonjsonlogger import jsonlogger  # type: ignore


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["severity"] = record.levelname
        log_record["logger"] = record.name


def setup_logger(name: str) -> logging.Logger:
    """Setup a JSON logger with proper formatting."""
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = CustomJsonFormatter("%(timestamp)s %(severity)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
