"""The module responsible for the endpoints for image moderation."""

import base64
import json
from logging import getLogger
from time import time

from fastapi import APIRouter, File, Request, Response, UploadFile

from con_prod.moderation_requests.producer import ModerationRequestsProducer
from con_prod.moderation_responses.consumer import ModerationResponsesConsumer
from config.app import MODERATION_REQUESTS_QUEUE_KEY, Config
from schemas.moderation import ModerationRequest

logger = getLogger("main.server.routes.moderation")
router = APIRouter(tags=["moderation"])


@router.post(
    "/moderate/",
    status_code=200,
    responses={
        200: {
            "description": "Image was moderated.",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {"value": {"status": "OK"}},
                        "NSFW": {
                            "value": {
                                "status": "REJECTED",
                                "reason": "NSFW content",
                            },
                        },
                    },
                },
            },
        },
        202: {
            "description": "Moderation request was accepted.",
            "content": {
                "application/json": {
                    "example": {
                        "status": "ACCEPTED",
                        "request_id": "<request ID (UUID4)>",
                    },
                },
            },
        },
        400: {
            "description": "An error occurred during verification.",
            "content": {
                "application/json": {
                    "example": {"status": "ERROR"},
                },
            },
        },
    },
)
async def moderate(request: Request, image: UploadFile = File(...)):
    """
    Check the image on NSFW.

    Timeout = 5s. If the timeout is exceeded,
    the 202 code with the task id will be returned.
    """
    image_bytes = await image.read()
    image_str: str = base64.b64encode(image_bytes).decode("utf-8")
    config: Config = request.state.config

    requests_producer = ModerationRequestsProducer(
        redis_url=config.redis.url, queue_key=MODERATION_REQUESTS_QUEUE_KEY
    )
    moderation_request = ModerationRequest(image=image_str)
    await requests_producer.produce(moderation_request)

    responses_consumer = ModerationResponsesConsumer(
        redis_url=config.redis.url
    )

    start_time = time()
    moderation_response = await responses_consumer.consume(
        moderation_request.id,
        timeout=config.moderation_timeout,
    )
    logger.debug("Getting response time: %.1f", time() - start_time)

    if moderation_response is None:
        return Response(
            status_code=202,
            content=json.dumps(
                {
                    "status": "ACCEPTED",
                    "request_id": moderation_request.id,
                }
            ),
        )
    logger.debug(
        "Moderation response: %s",
        moderation_response.model_dump_json(indent=2),
    )
    if moderation_response.status == "ERROR":
        return Response(
            status_code=400, content=json.dumps({"status": "ERROR"})
        )
    if moderation_response.nsfw <= 0.7:
        return {"status": "OK"}
    else:
        return {"status": "REJECTED", "reason": "NSFW content"}


@router.get(
    "/moderation_result/{moderation_request_id}",
    status_code=200,
    responses={
        200: {
            "description": "Get moderation result",
            "content": {
                "application/json": {
                    "examples": {
                        "success": {"value": {"status": "OK"}},
                        "NSFW": {
                            "value": {
                                "status": "REJECTED",
                                "reason": "NSFW content",
                            },
                        },
                        "processing": {"value": {"status": "PROCESSING"}},
                    },
                },
            },
        },
        400: {
            "description": "An error occurred during verification.",
            "content": {
                "application/json": {
                    "example": {"status": "ERROR"},
                },
            },
        },
    },
)
async def get_moderation_result(request: Request, moderation_request_id: str):
    """Return moderation result."""
    config: Config = request.state.config
    responses_consumer = ModerationResponsesConsumer(
        redis_url=config.redis.url
    )
    moderation_response = await responses_consumer.consume(
        moderation_request_id,
        timeout=config.moderation_timeout,
    )

    if moderation_response is None:
        return {"status": "PROCESSING"}
    logger.debug(
        "Moderation response: %s",
        moderation_response.model_dump_json(indent=2),
    )
    if moderation_response.status == "ERROR":
        return Response(
            status_code=400, content=json.dumps({"status": "ERROR"})
        )
    if moderation_response.nsfw <= 0.7:
        return {"status": "OK"}
    else:
        return {"status": "REJECTED", "reason": "NSFW content"}
