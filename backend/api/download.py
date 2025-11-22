from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import asyncio

from services.redis_service import RedisService
from config.config_service import ConfigService
from container import container

router = APIRouter()

@router.get("/pcaps/download/{file_hash}")
async def download_pcap_by_hash(file_hash: str):
    redis_client = container.get(RedisService).client
    settings = container.get(ConfigService).init()
    if not redis_client:
        raise HTTPException(status_code=503, detail="Service unavailable: Redis connection failed.")

    file_metadata = await asyncio.to_thread(redis_client.hgetall, f"pcap:file:{file_hash}")
    if not file_metadata:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = file_metadata.get("path")
    filename = file_metadata.get("filename")

    abs_path = await asyncio.to_thread(os.path.abspath, file_path)
    allowed_abs_dir = await asyncio.to_thread(os.path.abspath, settings.PCAP_DIRECTORY)
    if not abs_path.startswith(allowed_abs_dir):
        raise HTTPException(status_code=403, detail="Forbidden: Access is denied.")

    return FileResponse(abs_path, media_type='application/vnd.tcpdump.pcap', filename=filename)