import hashlib
import asyncio

def sha256_sync(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(4096), b""):
            sha.update(block)
    return sha.hexdigest()

async def sha256(path):
    return await asyncio.to_thread(sha256_sync, path)
