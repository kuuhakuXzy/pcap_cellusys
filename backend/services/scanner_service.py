import os
import asyncio
import json
import logging
from services.hashing_service import sha256
from services.pcap_parser import parse_pcap

class ScannerService:

    @staticmethod
    async def scan(redis_client, directories, base_url=None, target_folder=None, exclude=None):
        if exclude is None:
            exclude = []

        seen = set()
        indexed = 0
        autocomplete_key = "pcap:protocols:autocomplete"

        for folder in directories:
            if not await asyncio.to_thread(os.path.isdir, folder):
                logging.warning(f"Skipping non-existent directory {folder}")
                continue

            for root, dirs, files in await asyncio.to_thread(os.walk, folder):
                if target_folder and os.path.basename(root) != target_folder:
                    continue

                for file in files:
                    if file in exclude or not file.endswith((".pcap", ".pcapng", ".cap")):
                        continue

                    path = os.path.join(root, file)
                    file_hash = await sha256(path)

                    if file_hash in seen:
                        continue
                    seen.add(file_hash)

                    parse = await parse_pcap(path)
                    if parse is None or not parse:
                        continue

                    size = await asyncio.to_thread(os.path.getsize, path)
                    pcap_key = f"pcap:file:{file_hash}"

                    url = f"{base_url}/pcaps/download/{file_hash}" if base_url else ""

                    pipe = redis_client.pipeline()
                    pipe.hset(pcap_key, mapping={
                        "filename": file,
                        "path": path,
                        "size_bytes": size,
                        "protocols": ",".join(parse.keys()),
                        "protocol_counts": json.dumps(parse),
                        "download_url": url,
                    })

                    payload = {proto: 0 for proto in parse.keys()}
                    pipe.zadd(autocomplete_key, payload)

                    for proto in parse.keys():
                        pipe.sadd(f"pcap:index:protocol:{proto.lower()}", file_hash)

                    await asyncio.to_thread(pipe.execute)
                    indexed += 1

        return indexed
