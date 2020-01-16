import logging
import functools
import asyncio
import json

from app.util import time_util
from app.util import error_util
from app.util.db_util import POOL

GLOBAL_LOCAL_CACHE = {}


def cache(expire=60, storage="redis"):
    def decorate(func):
        def get_key(func, args, kwargs):
            return f"{func.__module__}@{func.__name__}@{args}@{kwargs}"

        @functools.wraps(func)
        async def _async_wrapper(*args, **kwargs):
            key = get_key(func, args, kwargs)
            if storage == "local":
                if key not in GLOBAL_LOCAL_CACHE:
                    GLOBAL_LOCAL_CACHE[key] = {
                        "expire": expire + time_util.timestamp(),
                        "value": await func(*args, **kwargs),
                    }
                return GLOBAL_LOCAL_CACHE[key]["value"]
            value = await POOL["redis"].get(key)
            if not value:
                value = await func(*args, **kwargs)
                await POOL["redis"].set(key, json.dumps(value), expire=expire)
                return value
            return json.loads(value)

        return _async_wrapper

    return decorate
