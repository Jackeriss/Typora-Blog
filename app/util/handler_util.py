import functools
import orjson
import os
import asyncio

import tornado
import aiotask_context
from schema import Schema, SchemaError

from app.util import error_util
from app.util.config_util import config
from app.config import const_config


class BasicHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(BasicHandler, self).__init__(application, request, **kwargs)
        self._basic_info = None
        self._all_arguments = None
        self._json_arguments = None

    def initialize(self, **kwargs):
        self.__dict__.update(kwargs)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", config.server["allow_origin"])
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Max-Age", 3600)
        method = self.get_header("Access-Control-Request-Method")
        if method:
            self.set_header("Access-Control-Allow-Methods", method)
        headers = self.get_header("Access-Control-Request-Headers")
        if headers:
            self.set_header("Access-Control-Allow-Headers", headers)

    def get_header(self, name, default=None):
        return self.request.headers.get(name, default)

    @property
    def content_type(self):
        return self.get_header("Content-Type", "")

    @property
    def host(self):
        return self.get_header("Host", "")

    @property
    def basic_info_str(self):
        """ 客户端可将常用信息以 JSON 形式放在这个 header 中 """
        return self.get_header("Basic-Info", "{}")

    @property
    def basic_info(self):
        if self._basic_info is None:
            self._basic_info = orjson.loads(self.basic_info_str)
        return self._basic_info

    @property
    def request_body(self):
        return self.request.body.decode()

    @property
    def request_query(self):
        return self.request.query

    @property
    def request_headers(self):
        return dict(self.request.headers)

    def get_param(self, name):
        return self.get_query_arguments(name).decode()

    @property
    def json_arguments(self):
        if self._json_arguments is None:
            content_type = self.content_type
            if content_type and content_type.find(r"application/json") >= 0:
                try:
                    json_dict = orjson.loads(self.request.body)
                    if isinstance(json_dict, dict):
                        self._json_arguments = json_dict
                    else:
                        raise error_util.ResponseError(
                            error_util.ERROR_CODE.JSON_PARAMS_NOT_IN_DICT
                        )
                except orjson.JSONDecodeError:
                    raise error_util.ResponseError(
                        error_util.ERROR_CODE.JSON_PARAMS_FORMAT_ERROR
                    )
            self._json_arguments = self._json_arguments if self._json_arguments else {}
        return self._json_arguments

    @property
    def all_arguments(self):
        if self._all_arguments is None:
            self._all_arguments = {
                key: self.get_argument(key) for key in self.request.arguments.keys()
            }
            self._all_arguments.update(self.json_arguments)
        return self._all_arguments

    def validate_argument(self, schema, error=None, data=None, ignore_extra_keys=True):
        data = data if data else self.all_arguments
        try:
            return Schema(
                schema, error=error, ignore_extra_keys=ignore_extra_keys
            ).validate(data)
        except SchemaError as e:
            raise error_util.ResponseError(error_util.ERROR_CODE.SCHEMA_ERROR)

    def error(self, code, message=None, status=None):
        status = status or error_util.ERROR_MAP.get(code, {"status": 500})["status"]
        message = (
            message
            or error_util.ERROR_MAP.get(code, {"message": "UNKNOWN ERROR"})["message"]
        )
        self.set_status(status)
        response = {"code": code.value, "message": message, "body": None}
        return self.finish(orjson.dumps(response))

    def success(self, data, status=const_config.HTTPCode.OK):
        self.set_status(status)
        response = {
            "code": error_util.ERROR_CODE.SUCCESS.value,
            "message": error_util.ERROR_MAP.get(error_util.ERROR_CODE.SUCCESS)[
                "message"
            ],
            "body": data,
        }
        return self.finish(orjson.dumps(response))

    def page(self, template, **kwargs):
        return self.render(os.path.join("dist", template) if config.env != "dev" else template, **kwargs)

    def post_page(self, post, **kwargs):
        return self.render(os.path.join("post", f"{post}.html"), **kwargs)

    def write_error(self, status_code, **kwargs):
        self.error(status_code)

    def render_error(self, status_code):
        page_params = {"status_code": status_code.value}
        return self.page("error.html", **page_params)


class PageNotFoundHandler(BasicHandler):
    """ 404 页面 handler """

    def get(self):
        self.render_error(const_config.HTTPCode.NOT_FOUND)

    def post(self):
        return self.error(error_util.ERROR_CODE.NOT_FOUND)


class StaticHandler(tornado.web.StaticFileHandler, BasicHandler):
    """ 静态文件 handler """


def set_context(func, *args, **kwargs):
    """ request handler 的装饰器，给每一个 request 设置协程上下文 """

    @functools.wraps(func)
    async def _async_wrapper(handler, *args, **kwargs):
        aiotask_context.set("handler", handler)
        await func(handler, *args, **kwargs)

    @functools.wraps(func)
    def _sync_wrapper(handler, *args, **kwargs):
        aiotask_context.set("handler", handler)
        func(handler, *args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        return _async_wrapper
    return _sync_wrapper
