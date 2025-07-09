#!/usr/bin/env python3
""" Testing get_page """
from web import get_page
import time

url = "http://slowwly.robertomurray.co.uk/delay/3000/url/http://example.com"

print(get_page(url))  # First call, slow
print(get_page(url))  # Cached, fast

time.sleep(10)        # Wait for cache to expire
print(get_page(url))  # Slow again after cache expiration
