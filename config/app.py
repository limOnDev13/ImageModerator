"""The module responsible for component configurations."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class ClarifaiConfig(object):
    """Clarifai config."""

    access_token: str
    model_url: str


@dataclass
class Config(object):
    """App config."""

    debug: bool
    clarifai: ClarifaiConfig


def get_config() -> Config:
    """Get config (from .env)."""
    load_dotenv()

    if "HOME" not in os.environ:
        os.environ["HOME"] = os.path.expanduser("~")

    return Config(
        debug=os.getenv("DEBUG", "1") == "1",
        clarifai=ClarifaiConfig(
            access_token=os.getenv("CLARIFAI_ACCESS_TOKEN", "clarifai PAT"),
            model_url=os.getenv("CLARIFAI_MODEL_URL", "clarifai model url"),
        ),
    )
