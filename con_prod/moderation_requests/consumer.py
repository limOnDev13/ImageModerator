"""The module responsible for the consumer of moderation requests."""

from typing import Optional

from redis.asyncio import Redis

from schemas import ModerationRequest
from utils.redis import RedisConMixin


class ModerationRequestsConsumer(RedisConMixin):
    """Moderation requests consumer based on Redis."""

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

    async def consume(self) -> ModerationRequest:
        """Consume moderation requests."""
        request_str = await self.blpop(self.__queue_key)
        return ModerationRequest.model_validate_json(request_str)
