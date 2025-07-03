"""The module responsible for pushing the redis connection to each handler."""

import logging

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from config.app import Config

logger = logging.getLogger("main.server.middlewares.config")


class ConfigMiddleware(BaseHTTPMiddleware):
    """The middleware responsible for pushing the config to the handlers."""

    def __init__(self, app: FastAPI, config: Config):
        """Initialize middleware."""
        super().__init__(app)
        self.__config = config

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Put config into the request.state.cache."""
        request.state.config = self.__config
        return await call_next(request)
