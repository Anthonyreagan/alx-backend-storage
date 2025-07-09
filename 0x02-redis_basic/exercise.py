import redis
import uuid
from typing import Union


class Cache:
    def __init__(self):
        """Initialize the Cache class with a Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the input data in Redis with a randomly generated key.

        Args:
            data: Data to store, can be str, bytes, int, or float

        Returns:
            str: The randomly generated key used to store the data
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key