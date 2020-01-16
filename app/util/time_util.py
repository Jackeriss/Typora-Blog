import functools
import logging
import asyncio
import time
from datetime import datetime

import pytz

from app.util.config_util import config


def str2datetime(value, default=None, time_format="%Y-%m-%d %H:%M:%S"):
    try:
        return datetime.strptime(value, time_format)
    except Exception as exception:
        logging.exception(f"str2datetime failed!value:{value} exception:{exception}")
        return default


def time_str2timestamp(time_str):
    if ":" in time_str:
        if "/" in time_str:
            return (
                time_str.split("/")[0],
                time.mktime(
                    datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S").timetuple()
                ),
            )
        return (
            time_str.split("-")[0],
            time.mktime(datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").timetuple()),
        )
    elif "/" in time_str:
        return (
            time_str.split("/")[0],
            time.mktime(datetime.strptime(time_str, "%Y/%m/%d %H-%M-%S").timetuple()),
        )
    else:
        return (
            time_str.split("-")[0],
            time.mktime(datetime.strptime(time_str, "%Y-%m-%d %H-%M-%S").timetuple()),
        )


def str2timestamp(value, default=0, time_format="%Y-%m-%d %H:%M:%S"):
    try:
        return datetime.strptime(value, time_format).timestamp() * 1000
    except Exception as exception:
        logging.exception(f"str2timestamp failed!value:{value} exception:{exception}")
        return default


def timestamp2str(value, time_format="%Y-%m-%d %H:%M:%S"):
    if not value:
        return ""
    try:
        return datetime.fromtimestamp(value, pytz.UTC).strftime(time_format)
    except Exception as exception:
        logging.exception(f"timestamp2str failed!value:{value} exception:{exception}")
        return ""


def datetime2str(value, default="", time_format="%Y-%m-%d %H:%M:%S"):
    if not isinstance(value, datetime):
        return default
    try:
        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        return value.strftime(time_format)
    except Exception as exception:
        logging.exception(f"datetime2str failed!value:{value} exception:{exception}")
        return default


def timestamp():
    return int(datetime.utcnow().timestamp())


def now():
    return datetime.utcnow()


def timeout_log(timeout=10, tag="", debug=False):
    def decorator(func):
        def _time_log(time_start, time_end, function_name):
            if not debug and config.server["debug"]:
                return
            cost = (time_end - time_start).total_seconds()
            if cost > timeout:
                logging.error(f"TIME OUT:{tag}, function:{function_name}, cost:{cost}s")

        @functools.wraps(func)
        async def _async_wrapper(*args, **kwargs):
            start = now()
            result = await func(*args, **kwargs)
            _time_log(start, now(), func.__name__)
            return result

        @functools.wraps(func)
        def _sync_wrapper(*args, **kwargs):
            start = now()
            result = func(*args, **kwargs)
            _time_log(start, now(), func.__name__)
            return result

        if asyncio.iscoroutinefunction(func):
            return _async_wrapper
        return _sync_wrapper

    return decorator
