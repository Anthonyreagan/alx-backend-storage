#!/usr/bin/env python3
""" Expiring web cache and tracker """
import redis
import requests
from typing import Callable
from functools import wraps

# Create a Redis instance
r = redis.Redis()

def count_access(method: Callable) -> Callable:
    """Decorator to count access to a URL"""
    @wraps(method)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        return method(url)
    return wrapper

def cache_page(method: Callable) -> Callable:
    """Decorator to cache a URL's response for 10 seconds"""
    @wraps(method)
    def wrapper(url: str) -> str:
        cached = r.get(url)
        if cached:
            return cached.decode('utf-8')

        # If not cached, fetch and store with expiration
        result = method(url)
        r.setex(url, 10, result)
        return result
    return wrapper

@count_access
@cache_page
def get_page(url: str) -> str:
    """Fetch HTML content of a URL and return it"""
    response = requests.get(url)
    return response.text
