"""The module responsible for configuring and launching the application."""

import logging.config

from fastapi import FastAPI

from config.app import Config, get_config
from config.log import get_log_config

from .middlewares.config_middleware import ConfigMiddleware
from .routes.healthcheck import router as healthcheck_router
from .routes.moderation import router as moderation_router

tags_metadata = [
    {
        "name": "Moderation",
        "description": "Operations with images moderation.",
    },
]


def create_app() -> FastAPI:
    """Configure and create the FastAPI app."""
    config: Config = get_config()
    logging.config.dictConfig(get_log_config(config.debug))
    logger = logging.getLogger("main.server")

    logger.info("Creating FastAPI app...")
    app_ = FastAPI(
        openapi_tags=tags_metadata,
    )

    # register routers
    app_.include_router(moderation_router)
    app_.include_router(healthcheck_router)

    # register middlewares
    app_.add_middleware(ConfigMiddleware, config)

    return app_


app: FastAPI = create_app()
