"""The module responsible for component configurations."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class ClarifaiConfig(object):
    """Clarifai config."""

    access_token: str


@dataclass
class RedisConfig(object):
    """Redis config."""

    url: str


@dataclass
class Config(object):
    """App config."""

    debug: bool
    moderation_timeout: float
    clarifai: ClarifaiConfig
    redis: RedisConfig


def get_config() -> Config:
    """Get config (from .env)."""
    load_dotenv()

    if "HOME" not in os.environ:
        os.environ["HOME"] = os.path.expanduser("~")

    return Config(
        debug=os.getenv("DEBUG", "1") == "1",
        moderation_timeout=float(os.getenv("MODERATION_TIMEOUT", 5.0)),
        clarifai=ClarifaiConfig(
            access_token=os.getenv("CLARIFAI_ACCESS_TOKEN", "clarifai PAT"),
        ),
        redis=RedisConfig(
            url=os.getenv("REDIS_URL", "redis://localhost:6379")
        ),
    )


MODERATION_REQUESTS_QUEUE_KEY: str = "moderation_requests"
