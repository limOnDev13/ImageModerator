"""The module responsible for the implementation of the Clarifai client."""

import base64
import json
import re
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Any, Dict, Optional

import httpx
from httpx import Response

from config.app import ClarifaiConfig
from schemas.moderation import ModerationRequest, ModerationResponse

from .base import NSFWClient

logger = getLogger("main.api.clarifai")


class ClarifaiClient(NSFWClient):
    """Clarifai client (REST API)."""

    BASE_URL: str = (
        "https://api.clarifai.com/v2/users/clarifai/apps/"
        "main/models/nsfw-recognition/versions/"
        "aa47919c9a8d4d94bfa283121281bcc4/outputs"
    )

    def __init__(
        self,
        config: ClarifaiConfig,
        httpx_client: Optional[httpx.AsyncClient] = None,
    ):
        """
        Init class.

        :param config: Clarifai config.
        :param httpx_client: HTTPX client.
        If None is passed, a new client will be created before each request.
        """
        self.__client = httpx_client
        self.__headers: Dict[str, str] = {
            "Authorization": f"Key {config.access_token}",
            "Content-Type": "application/json",
        }

    @asynccontextmanager
    async def __httpx_client(self) -> AsyncGenerator[httpx.AsyncClient, None]:
        """Yield HTTPX client."""
        if self.__client is not None:
            yield self.__client
        else:
            async with httpx.AsyncClient() as client:
                yield client

    @classmethod
    def __is_url(cls, s: str) -> bool:
        """Return True, if s is abs url."""
        if re.match(r"https?://.*", s):
            return True
        return False

    @classmethod
    def __is_base64(cls, s: str) -> bool:
        """Return True, if s is base64 encoded."""
        try:
            base64.b64decode(s, validate=True)
            return True
        except ValueError:
            return False

    async def moderate(
        self, moderation_request: ModerationRequest
    ) -> ModerationResponse:
        """
        Moderate nsfw.

        :param moderation_request: Moderation request object.
        :raise ValueError: If image is not url or base64.
        :return: JSON response from Clarifai API.
        """
        try:
            image = moderation_request.image
            if self.__is_url(image):
                logger.debug("Image is URL")
                image_data: Dict[str, str] = {"url": image}
            elif self.__is_base64(image):
                logger.debug("Image is base64 encoded.")
                image_data = {"base64": image}
            else:
                raise ValueError("Unrecognized image format.")

            async with self.__httpx_client() as client:
                data: Dict[str, Any] = {
                    "inputs": [{"data": {"image": image_data}}]
                }
                resp: Response = await client.post(
                    url=self.BASE_URL,
                    headers=self.__headers,
                    json=data,
                )
                if resp.status_code != 200:
                    logger.warning(
                        "Resp status: %d. Response: %s",
                        resp.status_code,
                        str(resp.json()),
                    )

                resp_json: Dict[str, Any] = resp.json()
                logger.debug(
                    "Response json: %s", json.dumps(resp_json, indent=2)
                )

                if resp_json["status"]["code"] == 10000:
                    logger.info("Successful request to Clarifai")
                    moderation_data = resp_json["outputs"][0]["data"][
                        "concepts"
                    ]
                    if moderation_data[0]["name"] == "nsfw":
                        nsfw = moderation_data[0]["value"]
                        sfw = moderation_data[1]["value"]
                    else:
                        nsfw = moderation_data[1]["value"]
                        sfw = moderation_data[0]["value"]
                    return ModerationResponse(
                        id=moderation_request.id,
                        sfw=sfw,
                        nsfw=nsfw,
                    )
                else:
                    logger.warning(
                        "Unsuccessful request to Clarifai. "
                        "Error description: %s",
                        resp_json["status"]["description"],
                    )
                    return ModerationResponse(
                        id=moderation_request.id, status="ERROR"
                    )
        except Exception as exc:
            logger.error("Unexpected error: %s", str(exc))
            return ModerationResponse(id=moderation_request.id, status="ERROR")


if __name__ == "__main__":
    from config.app import get_config

    config = get_config()
    client = ClarifaiClient(config.clarifai)

    import asyncio

    moderation_request = ModerationRequest(
        image="https://samples.clarifai.com/metro-north.jpg"
    )
    resp: ModerationResponse = asyncio.run(client.moderate(moderation_request))

    print(json.dumps(resp, indent=4))
