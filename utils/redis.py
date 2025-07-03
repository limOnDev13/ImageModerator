"""The module responsible for working with redis."""

from contextlib import asynccontextmanager
from functools import wraps
from logging import getLogger
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Optional,
    TypeVar,
    overload,
)

from redis.asyncio import Redis

logger = getLogger("total.utils.redis")

T = TypeVar("T")


@asynccontextmanager
async def redis_conn(
    redis_url: str,
) -> AsyncGenerator[Redis, None]:
    """
    Yield redis client.

    Async context manager.
    """
    redis_client = Redis.from_url(redis_url)
    try:
        yield redis_client
    finally:
        await redis_client.close()


def redis_decorator(redis_url: str):
    """Decorate func and add redis client in kwargs."""

    def wrapper(
        func: Callable[..., Coroutine[Any, Any, T]],
    ) -> Callable[..., Coroutine[Any, Any, T]]:
        """Wrap func."""

        @wraps(func)
        async def wrapped(*args: Any, **kwargs: Any) -> T:
            """Return func with redis client."""
            async with redis_conn(redis_url) as redis_client:
                return await func(*args, redis_client=redis_client, **kwargs)

        return wrapped

    return wrapper


class RedisMixin(object):
    """Redis client mixin."""

    @overload
    def __init__(self, redis_client: Redis, redis_url: None = None): ...

    @overload
    def __init__(self, redis_client: None, redis_url: str): ...

    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        redis_url: Optional[str] = None,
    ):
        """
        Init class.

        :param redis_client: Redis client.
        :param redis_url: Redis url
        """
        if redis_client is None and redis_url is None:
            raise ValueError(
                "You need either a redis client or a url to create it."
            )
        self.__redis_client = redis_client
        self.__redis_url = redis_url

    @asynccontextmanager
    async def get_redis_conn(self) -> AsyncGenerator[Redis, None]:
        """Yield redis connection."""
        if self.__redis_client:
            yield self.__redis_client
        else:
            async with redis_conn(self.__redis_url) as redis_client:
                yield redis_client


class RedisProdMixin(RedisMixin):
    """Redis publisher mixin."""

    async def rpush(self, key: str, value: str):
        """RPUSH value in list with key value."""
        async with self.get_redis_conn() as redis_client:
            logger.debug("RPUSH value %s to key %s", value, key)
            await redis_client.rpush(key, value)


class RedisConMixin(RedisMixin):
    """Redis subscriber mixin."""

    async def blpop(self, key: str) -> str:
        """BLPOP value from list with key."""
        async with self.get_redis_conn() as redis_client:
            _, value = await redis_client.blpop([key])
            logger.debug("BLPOP from key %s value %s", key, str(value))
            return value
