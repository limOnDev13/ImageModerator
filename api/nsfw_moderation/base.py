"""The module responsible for the client interface for NSFW moderation."""

from abc import ABC, abstractmethod

from schemas.moderation import ModerationRequest, ModerationResponse


class NSFWClient(ABC):
    """Base NSFW client interface."""

    @abstractmethod
    async def moderate(
        self, moderation_request: ModerationRequest
    ) -> ModerationResponse:
        """Moderate image."""
        pass
