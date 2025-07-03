"""The module responsible for nsfw image moderation."""

import asyncio
from logging import getLogger

from api.nsfw_moderation.base import NSFWClient
from api.nsfw_moderation.clarifai import ClarifaiClient
from con_prod.moderation_requests.consumer import ModerationRequestsConsumer
from con_prod.moderation_responses.producer import ModerationResponsesProducer
from schemas.moderation import ModerationRequest, ModerationResponse

logger = getLogger("main.services.moderation")


class NSFWModerator(object):
    """NSFW moderator."""

    def __init__(
        self,
        nsfw_client: NSFWClient,
        request_consumer: ModerationRequestsConsumer,
        response_producer: ModerationResponsesProducer,
        delay: float = 1.0,
    ):
        """
        Init class.

        :param nsfw_client: NSFW API client.
        :param request_consumer: Moderation requests consumer.
        :param response_producer: Moderation responses producer.
        :param delay: Delay after making api request.
        """
        self.__delay = delay
        self.__api = nsfw_client
        self.__request_consumer = request_consumer
        self.__response_producer = response_producer

    async def __produce_with_min_delay(
        self, moderation_response: ModerationResponse
    ) -> None:
        """
        Make a minimum delay.

        The function minimizes the delay during sending the moderation results
        to the queue. If the sending ended before the delay,
        the function waits for the delay to end.
        If the delay ended before sending,
        the function waits for sending to complete.

        :param moderation_response: Moderation response.
        """
        produce_task = asyncio.create_task(
            self.__response_producer.produce(moderation_response)
        )

        await asyncio.sleep(self.__delay)

        if not produce_task.done():
            await produce_task

    async def run(self):
        """Run NSFW moderation."""
        logger.info("Start NSFW moderator.")
        while True:
            try:
                moderation_request: ModerationRequest = (
                    await self.__request_consumer.consume()
                )
                logger.info(
                    "Request for nsfw moderation %s", moderation_request.id
                )
                logger.debug("Image: %s", moderation_request.image)

                moderation_resp: ModerationResponse = (
                    await self.__api.moderate(moderation_request)
                )
                logger.info(
                    "Moderation results: nsfw=%.4f; sfw=%.4f",
                    moderation_resp.nsfw,
                    moderation_resp.sfw,
                )

                await self.__produce_with_min_delay(moderation_resp)
                logger.debug("Moderation result sent for consumer.")
            except Exception as exc:
                logger.critical("Unexpected error. %s", str(exc))


async def launch_moderator():
    """Launch nsfw moderator."""
    from redis.asyncio import Redis

    from config.app import MODERATION_REQUESTS_QUEUE_KEY, Config, get_config

    config: Config = get_config()

    async with Redis(config.redis.url) as redis:
        moderator = NSFWModerator(
            nsfw_client=ClarifaiClient(config=config.clarifai),
            request_consumer=ModerationRequestsConsumer(
                redis_client=redis,
                queue_key=MODERATION_REQUESTS_QUEUE_KEY,
            ),
            response_producer=ModerationResponsesProducer(redis_client=redis),
        )

        await moderator.run()


if __name__ == "__main__":
    asyncio.run(launch_moderator())
