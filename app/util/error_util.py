import functools
import logging
import asyncio
from enum import IntEnum

from tornado.web import HTTPError

from app.constant.constant import HTTPCode


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
    @functools.wraps(func)
    async def _wrapper(handler, *args, **kwargs):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(handler, *args, **kwargs)
            return func(handler, *args, **kwargs)
        except BasicException as error:
            logging.error(f"BasicException: {error.code}\nMessage: {error.message}")
            return handler.error(error.code, error.message, error.status)
        except HTTPError as error:
            return handler.error(error.status_code, "HTTP_ERROR", error.status_code)
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

    return _wrapper
