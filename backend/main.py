import logging
import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor

from config.config_service import ConfigService
from services.redis_service import RedisService
from api import search, scan, download, health, errors
from utils.logging import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Load config
settings = ConfigService.init()

# Init Redis
REDIS_HOST = settings.get("redis_host", "localhost")
REDIS_PORT = settings.get("redis_internal_port", 6379)
redis_client = RedisService.init(REDIS_HOST, int(REDIS_PORT))

# Create app
app = FastAPI(title="Pcap Catalog Service")

# CORS (if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
errors.register_exception_handlers(app)

# Include routers
app.include_router(search.router)
app.include_router(scan.router)
app.include_router(download.router)
app.include_router(health.router)

# Executor for background tasks
executor = ThreadPoolExecutor()


@app.on_event("startup")
async def startup_event():
    # Optionally check Redis and kick off initial scan
    if redis_client:
        try:
            keys = await asyncio.to_thread(redis_client.keys, "pcap:file:*")
            if not keys:
                logger.info("No indexed pcaps found. Starting initial scan in background.")
                loop = asyncio.get_event_loop()
                loop.run_in_executor(executor, lambda: asyncio.run(scan.ScannerService.scan(redis_client, settings.PCAP_DIRECTORIES, base_url=settings.FULL_BASE_URL)))
            else:
                logger.info(f"Found {len(keys)} indexed pcaps. Skipping initial full scan.")
        except Exception as e:
            logger.exception("Failed to check Redis during startup")
    else:
        logger.error("Redis client not available at startup")