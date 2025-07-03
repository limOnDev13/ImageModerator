"""Module responsible for implementing the producer of moderation results."""

from typing import Optional

from redis.asyncio import Redis

from schemas import ModerationResponse
from utils.redis import RedisConMixin


class ModerationResponsesConsumer(RedisConMixin):
    """Moderation responses consumer based on redis."""

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

    async def consume(
        self, moderation_request_id, timeout: Optional[float] = None
    ) -> Optional[ModerationResponse]:
        """Consume moderation responses."""
        response_str = await self.blpop(moderation_request_id, timeout=timeout)
        if response_str is None:
            return None
        return ModerationResponse.model_validate_json(response_str)
