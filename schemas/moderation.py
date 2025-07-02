"""The module responsible for the schemes for moderation."""

from pydantic import UUID4, BaseModel, Field


class ModerationRequest(BaseModel):
    """Moderation request schema."""

    id: UUID4 = Field(
        default_factory=UUID4, description="Moderation request ID"
    )
    image: str = Field(..., description="Image URL or Base64")


class ModerationResponse(BaseModel):
    """Moderation response schema."""

    id: UUID4 = Field(
        ...,
        description="Moderation response ID. The moderation response ID."
        " Is equal to the ID of the corresponding moderation request.",
    )
