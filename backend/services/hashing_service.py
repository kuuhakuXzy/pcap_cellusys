import hashlib
import asyncio
from decorators import service

@service
class HashingService:
    def sha256_sync(self, path):
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(4096), b""):
                sha.update(block)
        return sha.hexdigest()

    async def sha256(self, path):
        return await asyncio.to_thread(self.sha256_sync, path)
