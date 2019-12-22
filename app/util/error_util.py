import functools
import logging
import asyncio
from enum import IntEnum

from app.config.constant import HTTPCode


class ERROR_CODE(IntEnum):
    SUCCESS = 0
    SYSTEM_ERROR = 1
    NOT_FOUND = 1000
    SCHEMA_ERROR = 1001
    JSON_PARAMS_NOT_IN_DICT = 1002
    JSON_PARAMS_FORMAT_ERROR = 1003


ERROR_MAP = {
    ERROR_CODE.SUCCESS: {"message": "SUCCESS", "status": HTTPCode.OK},
    ERROR_CODE.SYSTEM_ERROR: {
        "message": "SYSTEM_ERROR",
        "status": HTTPCode.INTERNAL_SERVER_ERROR,
    },
    ERROR_CODE.NOT_FOUND: {"message": "NOT_FOUND", "status": HTTPCode.NOT_FOUND},
    ERROR_CODE.SCHEMA_ERROR: {
        "message": "SCHEMA_ERROR",
        "status": HTTPCode.BAD_REQUEST,
    },
    ERROR_CODE.JSON_PARAMS_NOT_IN_DICT: {
        "message": "JSON_PARAMS_NOT_IN_DICT",
        "status": HTTPCode.BAD_REQUEST,
    },
    ERROR_CODE.JSON_PARAMS_FORMAT_ERROR: {
        "message": "JSON_PARAMS_FORMAT_ERROR",
        "status": HTTPCode.BAD_REQUEST,
    },
}


class BasicException(Exception):
    def __init__(self, code, message=None, status=None):
        super().__init__()
        self.code = code
        self.message = message
        self.status = status


class ResponseError(BasicException):
    def __init__(self, code):
        message = ERROR_MAP.get(code, {"message": "UNKNOWN_ERROR"})["message"]
        status = ERROR_MAP.get(code, {"status": 500})["status"]
        super(ResponseError, self).__init__(code, message, status)


def try_exception(func):
    """ 给每一个 request 加上全局异常捕获 """

    @functools.wraps(func)
    async def _async_wrapper(handler, *args, **kwargs):
        try:
            result = await func(handler, *args, **kwargs)
            return result
        except BasicException as error:
            logging.error(f"BasicException: {error.code}\nMessage: {error.message}")
            return handler.error(error.code, error.message, error.status)
        except BaseException as exception:
            try:
                url = handler.request.uri
                arg = handler.all_arguments
                basic_info = handler.basic_info_str
            except:
                url, arg, basic_info = "", "", ""
            logging.exception(
                f"SystemError:{exception}\nURL:{url}\nArguments:{arg}\nBasicInfo:{basic_info}"
            )
            return handler.error(ERROR_CODE.SYSTEM_ERROR, status=500)

    @functools.wraps(func)
    def _sync_wrapper(handler, *args, **kwargs):
        try:
            result = func(handler, *args, **kwargs)
            return result
        except BasicException as error:
            logging.error(f"BasicException: {error.code}\nMessage: {error.message}")
            return handler.error(error.code, error.message, error.status)
        except BaseException as exception:
            try:
                url = handler.request.uri
                arg = handler.all_arguments
                basic_info = handler.basic_info_str
            except:
                url, arg, basic_info = "", "", ""
            logging.exception(
                f"SystemError:{exception}\nURL:{url}\nArguments:{arg}\nBasicInfo:{basic_info}"
            )
            return handler.error(ERROR_CODE.SYSTEM_ERROR, status=500)

    if asyncio.iscoroutinefunction(func):
        return _async_wrapper
    return _sync_wrapper
