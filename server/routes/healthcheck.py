"""The module responsible for the endpoints for image moderation."""

from fastapi import APIRouter

router = APIRouter(tags=["healthcheck"])


@router.get("/health/", status_code=200)
async def health():
    """Check health."""
    return {"status": "OK"}
