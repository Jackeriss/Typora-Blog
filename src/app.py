from tornado import web

from src.route import ROUTE
from src.service.log import log_request, logger
from src.config import Config


class TornadoApplication(web.Application):
    def __init__(self):
        logger.setLevel(Config.LOG_LEVEL)
        web.Application.__init__(
            self, ROUTE, log_function=log_request, **Config.SETTING
        )
