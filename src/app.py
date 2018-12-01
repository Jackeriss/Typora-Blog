import logging

from tornado import web

from src.route import ROUTE
from src.config import Config


class TornadoApplication(web.Application):
    def __init__(self):
        logging.getLogger().setLevel(Config.LOG_LEVEL)
        web.Application.__init__(
            self, ROUTE, log_function=self.log_request, **Config.SETTING
        )

    def log_request(self, handler):
        if handler.get_status() < 400:
            log_method = logging.info
        elif handler.get_status() < 500:
            log_method = logging.warning
        else:
            log_method = logging.error
        request_time = 1000.0 * handler.request.request_time()
        log_method(
            "%d %s %.2fms", handler.get_status(),
            handler._request_summary(), request_time
        )
