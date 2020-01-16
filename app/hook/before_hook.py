import tornado

from app.util.error_util import try_exception


def wrap_handler(app):

    support_methods = tornado.web.RequestHandler.SUPPORTED_METHODS
    routers = app.routers

    for router in routers:
        handler = router[1]
        for method in support_methods:
            method = method.lower()
            func = getattr(handler, method)
            if func:
                func = try_exception(func)
                setattr(handler, method, func)
