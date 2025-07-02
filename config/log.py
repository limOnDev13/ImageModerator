"""The module responsible for configuring logging."""

from copy import deepcopy
from typing import Any, Dict

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "base": {
            "format": "[%(levelname)s] [%(asctime)s] | %(name)s - %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "base",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "base",
            "filename": "bot_logfile.log",
            "backupCount": 3,
            "when": "d",
            "interval": 10,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "main": {
            "level": "DEBUG",
            "handlers": ["file", "console"],
            "propagate": False,
        },
    },
}


def get_log_config(debug: bool = True) -> Dict[str, Any]:
    """Return config for logging."""
    if not debug:
        log_config: Dict[str, Any] = deepcopy(LOG_CONFIG)
        log_config["handlers"]["console"]["level"] = "INFO"
        log_config["loggers"]["main"]["level"] = "INFO"
        return log_config
    return LOG_CONFIG
