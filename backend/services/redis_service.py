import redis
import logging
from decorators import service

@service
class RedisService:
    def __init__(self):
        self.client = None

    def init(self, host, port):
        if self.client:
            return self.client

        try:
            r = redis.Redis(host=host, port=port, decode_responses=True)
            r.ping()
            logging.info(f"Connected to Redis at {host}:{port}")
            self.client = r
        except redis.ConnectionError as e:
            logging.error(f"Redis connection failed: {e}")
            self.client = None

        return self.client
