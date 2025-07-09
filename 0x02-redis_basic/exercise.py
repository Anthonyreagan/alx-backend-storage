#!/usr/bin/env python3
"""Writing and reading from Redis with type recovery and call history"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count how many times a method is called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store history of inputs and outputs for a method"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        inputs_key = f"{method.__qualname__}:inputs"
        outputs_key = f"{method.__qualname__}:outputs"

        # Store input arguments
        self._redis.rpush(inputs_key, str(args))

        # Execute the wrapped function
        output = method(self, *args, **kwargs)

        # Store the output
        self._redis.rpush(outputs_key, output)

        return output
    return wrapper


def replay(method: Callable) -> None:
    """Display the history of calls of a particular function"""
    if not hasattr(method, '__self__'):
        print("Error: Can only replay bound methods")
        return

    cache = method.__self__
    method_name = method.__qualname__
    inputs_key = f"{method_name}:inputs"
    outputs_key = f"{method_name}:outputs"

    # Get the count
    count = cache._redis.get(method_name)
    count = int(count) if count else 0

    print(f"{method_name} was called {count} times:")

    # Get all inputs and outputs
    inputs = cache._redis.lrange(inputs_key, 0, -1)
    outputs = cache._redis.lrange(outputs_key, 0, -1)

    for args, output in zip(inputs, outputs):
        print(f"{method_name}{args.decode('utf-8')} -> {output.decode('utf-8')}")


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