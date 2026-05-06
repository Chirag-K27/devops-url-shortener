from pydantic import BaseModel, HttpUrl
from datetime import datetime


class URLCreate(BaseModel):
    """Request schema for creating a short URL."""
    url: HttpUrl


class URLResponse(BaseModel):
    """Response schema after creating a short URL."""
    short_code: str
    short_url: str
    original_url: str


class URLStats(BaseModel):
    """Response schema for URL statistics."""
    short_code: str
    original_url: str
    clicks: int
    created_at: datetime


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    database: str
    redis: str
    version: str
