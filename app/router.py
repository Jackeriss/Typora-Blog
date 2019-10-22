from app.model.post import handler as post
from app.model.static_page import handler as static_page
from app.model.health_check import handler as health_check
from app.util import handler_util as base
from app.util.config_util import config


ROUTERS = [
    (r"/ping", health_check.HealthCheckHandler),
    (r"/v1/posts", post.PostsHandler),
    (r"/i/", static_page.IndexHandler),
    (r"/i/post/(.*)", post.PostHandler),
    (r"/i/achive", static_page.AchiveHandler),
    (r"/i/project", static_page.ProjectHandler),
    (r"/i/movie", static_page.MovieHandler),
    (r"/i/about", static_page.AboutHandler),
    (r"/i/.*", base.PageNotFoundHandler),
    (r"/(.*\..*)", base.StaticHandler, {"path": config.static_path}),
    (r"/(.*)", static_page.IframeHandler),
]
