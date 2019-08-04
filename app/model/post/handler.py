from schema import Optional, Use

from app.model.post.service import PostService
from app.util.handler_util import BasicHandler


class PostsHandler(BasicHandler):

    def get(self):
        params = self.validate_argument({
            Optional("page", default=None): Use(int)
        })
        posts = PostService.get_posts(current_page=params["page"])
        self.success(posts)


class PostHandler(BasicHandler):

    def get(self, post_id):
        post = PostService.get_post(post_id=post_id)
        if not post:
            page_params = {
                "code": 404
            }
            self.page("error.html", **page_params)
        page_params = {
            "timestamp": post['timestamp']
        }
        self.post_page(post["title"], **page_params)
