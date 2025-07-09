#!/usr/bin/env python3
"""
Main file for testing the Cache class
"""
import redis
from exercise import Cache

def main():
    # Create an instance of the Cache class
    cache = Cache()

    # Test storing different data types
    test_data = [
        b"hello",        # bytes
        "world",         # str
        42,              # int
        3.14,            # float
        "Python is cool"  # another string
    ]

    for data in test_data:
        # Store the data and get the key
        key = cache.store(data)
        print(f"Stored data: {data} (type: {type(data)})")
        print(f"Generated key: {key}")

        # Retrieve the data from Redis using the key
        retrieved_data = redis.Redis().get(key)
        print(f"Retrieved data: {retrieved_data}")
        print("-" * 50)

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

    main()