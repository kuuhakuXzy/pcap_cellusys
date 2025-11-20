from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional, List
import asyncio
import logging

from services.redis_service import RedisService
from services.scanner_service import ScannerService
from config.config_service import ConfigService

router = APIRouter()

scan_status = {"state": "idle", "indexed_files": 0, "message": "Ready"}

@router.post("/reindex")
async def reindex_pcaps(request: Request, exclude: Optional[List[str]] = Query(None)):
    if scan_status["state"] == "running":
        raise HTTPException(status_code=409, detail="A scan is already running.")

    settings = ConfigService.init()
    redis_client = RedisService.client
    base_url = settings.FULL_BASE_URL or str(request.base_url).rstrip("/")

    loop = asyncio.get_event_loop()

    def _background():
        try:
            scan_status["state"] = "running"
            scan_status["indexed_files"] = 0
            scan_status["message"] = "Scanning in progress..."

            result = asyncio.run(ScannerService.scan(redis_client, settings.PCAP_DIRECTORIES, base_url=base_url, exclude=exclude))
            scan_status["indexed_files"] = result
            scan_status["state"] = "completed"
            scan_status["message"] = f"Completed successfully. Indexed {result} files."
        except Exception as e:
            logging.exception("Scan failed")
            scan_status["state"] = "failed"
            scan_status["message"] = str(e)
        finally:
            if scan_status["state"] != "failed":
                scan_status["state"] = "idle"

    loop.run_in_executor(None, _background)
    return {"status": "started"}


@router.get("/scan-status")
async def scan_status_endpoint():
    return scan_status


@router.post("/reindex/{folder_name}")
async def reindex_specific_folder(folder_name: str, request: Request, exclude: Optional[List[str]] = Query(None)):
    settings = ConfigService.init()
    redis_client = RedisService.client
    base_url = str(request.base_url).rstrip("/")

    result = await ScannerService.scan(redis_client, settings.PCAP_DIRECTORIES, base_url=base_url, target_folder=folder_name, exclude=exclude)
    if isinstance(result, int):
        return {"status": "success", "indexed_files": result}
    else:
        raise HTTPException(status_code=500, detail="Error during scanning")