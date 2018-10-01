import os

from tornado import web

from src.config import Config


class BaseHandler(web.RequestHandler):
    def __init__(self, *args, **kwargs):
        web.RequestHandler.__init__(self, *args, **kwargs)
        self.extra = {}
    def write_error(self, status_code, **kwargs):
        if status_code == 404:
            self.render(os.path.join(Config.ENV, 'error.html'), code='404')
        else:
            self.render(os.path.join(Config.ENV, 'error.html'), code='500')


class PageNotFoundHandler(BaseHandler):
    def get(self):
        self.write_error(404)