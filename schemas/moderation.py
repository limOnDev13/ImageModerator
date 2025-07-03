"""The module responsible for the schemes for moderation."""

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class ModerationRequest(BaseModel):
    """Moderation request schema."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Moderation request ID",
    )
    image: str = Field(..., description="Image URL or Base64")


class ModerationResponse(BaseModel):
    """Moderation response schema."""

    id: str = Field(
        ...,
        description="Moderation response ID. The moderation response ID."
        " Is equal to the ID of the corresponding moderation request.",
    )
    sfw: float = Field(default=0.0, description="SFW coefficient.")
    nsfw: float = Field(default=0.0, description="NSFW coefficient.")
    status: Literal["OK", "ERROR"] = Field(
        default="OK", description="Response status."
    )
