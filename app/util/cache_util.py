import logging
import functools
import asyncio

from app.util import time_util

GLOBAL_LOCAL_CACHE = {}


def local_cache(expire=60):
    """ 异步函数执行结果本地缓存
        expire: 缓存过期时间，单位（秒）
    """

    def decorate(func):
        def get_key(func, args, kwargs):
            return f"{func.__module__}@{func.__name__}@{args}@{kwargs}"

        @functools.wraps(func)
        async def _async_wrapper(*args, **kwargs):
            key = get_key(func, args, kwargs)
            if key not in GLOBAL_LOCAL_CACHE:
                GLOBAL_LOCAL_CACHE[key] = {
                    "expire": expire + time_util.timestamp(),
                    "value": await func(*args, **kwargs),
                }
            return GLOBAL_LOCAL_CACHE[key]["value"]

        @functools.wraps(func)
        def _sync_wrapper(*args, **kwargs):
            key = get_key(func, args, kwargs)
            if key not in GLOBAL_LOCAL_CACHE:
                GLOBAL_LOCAL_CACHE[key] = {
                    "expire": expire + time_util.timestamp(),
                    "value": func(*args, **kwargs),
                }
            return GLOBAL_LOCAL_CACHE[key]["value"]

        if asyncio.iscoroutinefunction(func):
            return _async_wrapper
        else:
            return _sync_wrapper

    return decorate
