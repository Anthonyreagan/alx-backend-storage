#!/usr/bin/env python3
"""Writing and reading from Redis with type recovery"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def call_history(method: Callable) -> Callable:
    """Decorator to store history of inputs and outputs for a method"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key_inputs = method.__qualname__ + ":inputs"
        key_outputs = method.__qualname__ + ":outputs"

        # Store input arguments as string
        self._redis.rpush(key_inputs, str(args))

        # Call original method and get result
        result = method(self, *args, **kwargs)

        # Store output result
        self._redis.rpush(key_outputs, result)

        return result
    return wrapper


def count_calls(method: Callable) -> Callable:
    """Decorator to count how many times a method is called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Increment the Redis counter using the method's qualified name
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper



class Cache:
    def __init__(self):
        """Initialize Redis client and flush database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a random key

        Args:
            data: The data to store (str, bytes, int, or float)

        Returns:
            str: The randomly generated key
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[bytes, str, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it

        Args:
            key: Redis key
            fn: Optional function to convert the data

        Returns:
            The data as is or converted using fn, or None if key doesn't exist
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """Retrieve string value from Redis"""
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """Retrieve integer value from Redis"""
        return self.get(key, fn=int)


if __name__ == "__main__":
    cache = Cache()

    TEST_CASES = {
        b"foo": None,
        123: int,
        "bar": lambda d: d.decode("utf-8")
    }

    for value, fn in TEST_CASES.items():
        key = cache.store(value)
        assert cache.get(key, fn=fn) == value
    print("All test cases passed!")
