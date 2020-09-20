from app.model.post import handler as post
from app.model.static_page import handler as static_page
from app.model.health_check import handler as health_check
from app.util import handler_util as base
from app.util.config_util import config


ROUTERS = [
    (r"/ping", health_check.HealthCheckHandler),
    (r"/v1/posts", post.PostsHandler),
    (r"/", static_page.IndexHandler),
    (r"/post/(.*)", post.PostHandler),
    (r"/achive", static_page.AchiveHandler),
    (r"/project", static_page.ProjectHandler),
    (r"/movie", static_page.MovieHandler),
    (r"/about", static_page.AboutHandler),
    (r"/(.*\..*)", base.StaticHandler, {"path": config.static_path}),
    (r".*", base.PageNotFoundHandler),
]
