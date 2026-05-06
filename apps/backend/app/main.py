import string
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from app.config import get_settings
from app.database import get_db, init_db
from app.models import URL
from app.schemas import URLCreate, URLResponse, URLStats, HealthResponse
from app.cache import (
    get_cached_url,
    set_cached_url,
    increment_click_count,
    get_click_count,
    check_redis_health,
)

settings = get_settings()

# ── Prometheus Metrics ──────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "url_shortener_requests_total",
    "Total requests",
    ["method", "endpoint", "status"],
)
URL_CREATED = Counter(
    "url_shortener_urls_created_total",
    "Total URLs shortened",
)
REDIRECT_COUNT = Counter(
    "url_shortener_redirects_total",
    "Total redirects performed",
)
REQUEST_LATENCY = Histogram(
    "url_shortener_request_duration_seconds",
    "Request latency in seconds",
    ["endpoint"],
)


# ── App Lifespan ────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    await init_db()
    yield


# ── FastAPI App ─────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS — allow React frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ──────────────────────────────────────────────────────────
def generate_short_code(length: int = 6) -> str:
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


# ── Routes ──────────────────────────────────────────────────────────

# Health and metrics MUST be defined BEFORE the catch-all {short_code} route
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    redis_healthy = await check_redis_health()

    return HealthResponse(
        status="healthy" if redis_healthy else "degraded",
        database="connected",
        redis="connected" if redis_healthy else "disconnected",
        version=settings.APP_VERSION,
    )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain",
    )


@app.post("/api/shorten", response_model=URLResponse)
async def shorten_url(payload: URLCreate, db: AsyncSession = Depends(get_db)):
    """Create a shortened URL."""
    import time
    start = time.time()

    # Generate unique short code
    for _ in range(10):
        short_code = generate_short_code(settings.SHORT_CODE_LENGTH)
        existing = await db.execute(
            select(URL).where(URL.short_code == short_code)
        )
        if not existing.scalar_one_or_none():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique code")

    # Save to database
    url_entry = URL(
        original_url=str(payload.url),
        short_code=short_code,
    )
    db.add(url_entry)
    await db.flush()

    # Cache it
    await set_cached_url(short_code, str(payload.url))

    # Metrics
    URL_CREATED.inc()
    REQUEST_COUNT.labels("POST", "/api/shorten", "201").inc()
    REQUEST_LATENCY.labels("/api/shorten").observe(time.time() - start)

    return URLResponse(
        short_code=short_code,
        short_url=f"{settings.BASE_URL}/api/{short_code}",
        original_url=str(payload.url),
    )


@app.get("/api/{short_code}")
async def redirect_to_url(short_code: str, db: AsyncSession = Depends(get_db)):
    """Redirect to the original URL."""
    import time
    start = time.time()

    # Check cache first
    cached_url = await get_cached_url(short_code)
    if cached_url:
        await increment_click_count(short_code)
        REDIRECT_COUNT.inc()
        REQUEST_COUNT.labels("GET", "/api/{code}", "302").inc()
        REQUEST_LATENCY.labels("/api/{code}").observe(time.time() - start)
        return RedirectResponse(url=cached_url, status_code=302)

    # Cache miss — query database
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    url_entry = result.scalar_one_or_none()

    if not url_entry:
        REQUEST_COUNT.labels("GET", "/api/{code}", "404").inc()
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Update click count in DB
    url_entry.click_count += 1

    # Cache for next time
    await set_cached_url(short_code, url_entry.original_url)
    await increment_click_count(short_code)

    REDIRECT_COUNT.inc()
    REQUEST_COUNT.labels("GET", "/api/{code}", "302").inc()
    REQUEST_LATENCY.labels("/api/{code}").observe(time.time() - start)

    return RedirectResponse(url=url_entry.original_url, status_code=302)


@app.get("/api/stats/{short_code}", response_model=URLStats)
async def get_url_stats(short_code: str, db: AsyncSession = Depends(get_db)):
    """Get statistics for a shortened URL."""
    result = await db.execute(
        select(URL).where(URL.short_code == short_code)
    )
    url_entry = result.scalar_one_or_none()

    if not url_entry:
        raise HTTPException(status_code=404, detail="Short URL not found")

    # Combine DB clicks + Redis real-time clicks
    redis_clicks = await get_click_count(short_code)
    total_clicks = url_entry.click_count + redis_clicks

    REQUEST_COUNT.labels("GET", "/api/stats", "200").inc()

    return URLStats(
        short_code=url_entry.short_code,
        original_url=url_entry.original_url,
        clicks=total_clicks,
        created_at=url_entry.created_at,
    )


