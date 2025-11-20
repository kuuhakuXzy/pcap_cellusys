import redis
import logging

class RedisService:
    client = None

    @staticmethod
    def init(host, port):
        if RedisService.client:
            return RedisService.client

        try:
            r = redis.Redis(host=host, port=port, decode_responses=True)
            r.ping()
            logging.info(f"Connected to Redis at {host}:{port}")
            RedisService.client = r
        except redis.exceptions.ConnectionError as e:
            logging.error(f"Redis connection failed: {e}")
            RedisService.client = None

        return RedisService.client
