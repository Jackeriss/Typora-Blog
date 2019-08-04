import asyncio
from functools import partial

from concurrent.futures import ThreadPoolExecutor


class ThreadPool(object):
    @classmethod
    def init_thread_pool(cls, loop=None, workers=None):
        cls.loop = loop or asyncio.get_event_loop()
        cls.thread_pool = ThreadPoolExecutor(max_workers=workers)

    @classmethod
    def async_func(cls, sync_func, *args, **kwargs):
        wrap_func = partial(sync_func, *args, **kwargs)
        return cls.loop.run_in_executor(cls.thread_pool, wrap_func)
