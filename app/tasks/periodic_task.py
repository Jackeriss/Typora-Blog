""" 周期任务 """
from app.util.cache_util import GLOBAL_LOCAL_CACHE
from app.util import time_util


def delete_expired_local_cache():
    """ 删除过期的本地缓存 """
    now_time = time_util.timestamp()
    delete_keys = [key for key in GLOBAL_LOCAL_CACHE if GLOBAL_LOCAL_CACHE[key]["expire"] < now_time]
    for key in delete_keys:
        GLOBAL_LOCAL_CACHE.pop(key, None)
