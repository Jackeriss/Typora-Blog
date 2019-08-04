from app.model.post.service import PostService
from app.util.handler_util import BasicHandler


class IndexHandler(BasicHandler):

    def get(self):
        total_page = PostService.get_total_page()
        page_params = {
            "total_page": total_page
        }
        return self.page("index.html", **page_params)


class AchiveHandler(BasicHandler):

    def get(self):
        posts = PostService.get_posts()
        page_params = {
            "posts": posts
        }
        self.page('achive.html', **page_params)


class ProductHandler(BasicHandler):

    def get(self):
        self.page('product.html')


class LinkHandler(BasicHandler):

    def get(self):
        self.page('link.html')


class AboutHandler(BasicHandler):

    def get(self):
        self.page('about.html')