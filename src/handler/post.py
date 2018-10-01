import os
from tornado import web, gen, escape

from src.service.cache import cache
from src.handler.base import BaseHandler
from src.config import Config


class IndexHandler(BaseHandler):
    def get(self):
        self.render(os.path.join(Config.ENV, 'index.html'), page_num=int((
            len(cache.posts) + 4) / Config.PAGE_LIMIT))


class PostListHandler(BaseHandler):
    def get(self):
        current_page = abs(int(self.get_argument('page', 1)))
        total_page = int((len(cache.posts) + 4) / Config.PAGE_LIMIT)
        if current_page < total_page:
            posts = cache.posts[(current_page - 1) * Config.PAGE_LIMIT:
                                            current_page * Config.PAGE_LIMIT]
        elif current_page == total_page:
            posts = cache.posts[(current_page - 1) * Config.PAGE_LIMIT:
                                            len(cache.posts)]
        else:
            posts = []
        respon_json = escape.json_encode(posts)
        self.write(respon_json)


class PostHandler(BaseHandler):
    def get(self, url):
        found_post = False
        for post in cache.posts:
            if url == post['id']:
                found_post = True
                break
        if found_post:
            self.render(os.path.join('post/' + post['title'] +
                        '.html'), timestamp=post['timestamp'])
        else:
            self.render(os.path.join(Config.ENV, 'error.html'), code='404')


class AchiveHandler(BaseHandler):
    def get(self):
        self.render(os.path.join(Config.ENV, 'achive.html'), posts=cache.posts)


class ProductHandler(BaseHandler):
    def get(self):
        self.render(os.path.join(Config.ENV, 'product.html'))


class LinkHandler(BaseHandler):
    def get(self):
        self.render(os.path.join(Config.ENV, 'link.html'))


class AboutHandler(BaseHandler):
    def get(self):
        self.render(os.path.join(Config.ENV, 'about.html'))
