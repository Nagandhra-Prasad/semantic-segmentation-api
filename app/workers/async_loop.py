"""Single event loop for Celery solo worker (avoids asyncio.run() per task)."""

import asyncio

worker_loop = asyncio.new_event_loop()


def run_async(coro):
    return worker_loop.run_until_complete(coro)
