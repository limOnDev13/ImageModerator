"""The module responsible for producing moderation requests."""

from typing import Optional

from redis.asyncio import Redis

from schemas import ModerationRequest
from utils.redis import RedisProdMixin


class ModerationRequestsProducer(RedisProdMixin):
    """Moderation requests producer based on Redis."""

    def __init__(
        self,
        queue_key: str,
        redis_client: Optional[Redis] = None,
        redis_url: Optional[str] = None,
    ):
        """
        Init class.

        :param redis_client: Redis client.
        :param redis_url: Redis url
        :raise ValueError: If redis_client and redis_url are None.
        """
        self.__queue_key = queue_key
        super().__init__(redis_client=redis_client, redis_url=redis_url)

    async def produce(self, moderation_request: ModerationRequest) -> None:
        """Produce moderation requests."""
        await self.rpush(self.__queue_key, moderation_request.model_dump())
