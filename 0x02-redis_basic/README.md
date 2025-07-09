# Redis Caching System

A Python implementation of a Redis-based caching system that stores and retrieves data with auto-generated keys.

## Features

- **Simple API**: Store any data (str, bytes, int, float) with a single method call
- **Automatic Key Generation**: UUID-based keys ensure uniqueness
- **Redis Backed**: Built on the industry-standard Redis in-memory data store
- **Type Safe**: Full type hints for better code maintainability

## Installation

1. Ensure Redis is installed and running:
   ```bash
   # Ubuntu/Debian
   sudo apt install redis-server
   sudo systemctl start redis

   # macOS (Homebrew)
   brew install redis
   brew services start redis