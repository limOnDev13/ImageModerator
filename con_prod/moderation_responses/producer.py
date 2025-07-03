"""The module responsible for producing the moderation results."""

from typing import Optional

from redis.asyncio import Redis

from schemas import ModerationResponse
from utils.redis import RedisProdMixin


class ModerationResponsesProducer(RedisProdMixin):
    """Moderation responses producer based on Redis."""

    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        redis_url: Optional[str] = None,
    ):
        """
        Init class.

        :param redis_client: Redis client.
        :param redis_url: Redis url
        :raise ValueError: If redis_client and redis_url are None.
        """
        super().__init__(redis_client=redis_client, redis_url=redis_url)

    async def produce(self, moderation_resp: ModerationResponse) -> None:
        """Produce moderation response."""
        await self.rpush(str(moderation_resp.id), moderation_resp.model_dump())
