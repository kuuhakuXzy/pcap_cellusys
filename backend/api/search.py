from fastapi import APIRouter, HTTPException, Query
from typing import List
import asyncio
import json

from services.redis_service import RedisService

router = APIRouter()

@router.get("/search")
async def search_pcaps(protocol: str = Query(..., description="The protocol name to search for, e.g., sip")):
    redis_client = RedisService.client
    if not redis_client:
        raise HTTPException(status_code=503, detail="Service unavailable: Redis connection failed.")

    index_key = f"pcap:index:protocol:{protocol.lower()}"

    try:
        matching_hashes = await asyncio.to_thread(redis_client.smembers, index_key)
        if not matching_hashes:
            return []

        pipe = redis_client.pipeline()
        for file_hash in matching_hashes:
            pipe.hgetall(f"pcap:file:{file_hash}")
        raw_results = await asyncio.to_thread(pipe.execute)

        results = []
        for pcap_data in raw_results:
            if pcap_data:
                counts_str = pcap_data.pop("protocol_counts", None)
                packet_count = 0
                if counts_str:
                    try:
                        counts_dict = json.loads(counts_str)
                        packet_count = counts_dict.get(protocol, 0)
                    except json.JSONDecodeError:
                        pass

                pcap_data["searched_protocol"] = protocol
                pcap_data["protocol_packet_count"] = packet_count
                results.append(pcap_data)

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while querying Redis: {e}")