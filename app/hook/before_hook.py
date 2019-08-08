""" 在 Application 初始化之前调用 """
import tornado
import aiotask_context

from app.util.handler_util import set_context
from app.util.error_util import try_exception


def wrap_handler(app):
    """ 给每个 request 的 handler 设置装饰器 """

    support_methods = tornado.web.RequestHandler.SUPPORTED_METHODS
    routers = app.routers

    for router in routers:
        handler = router[1]
        for method in support_methods:
            method = method.lower()
            func = getattr(handler, method)
            if func:
                func = set_context(func)
                func = try_exception(func)
                setattr(handler, method, func)

    app.loop.set_task_factory(aiotask_context.task_factory)
