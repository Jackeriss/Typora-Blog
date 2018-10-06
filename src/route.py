from tornado import web

from src.handler import base, post
from src.config import Config

ROUTE = [
    (r'/', post.IndexHandler),
    (r'/postlist', post.PostListHandler),
    (r'/p/(.*)', post.PostHandler),
    (r'/achive', post.AchiveHandler),
    (r'/product', post.ProductHandler),
    (r'/link', post.LinkHandler),
    (r'/about', post.AboutHandler),
    (r'/((js|css|image)/.*)', web.StaticFileHandler, dict(path=Config.SETTING['static_path'])),
    (r'/(.*\.(txt|html))', web.StaticFileHandler, dict(path=Config.SETTING['static_path'])),
    (r'.*', base.PageNotFoundHandler),
    (r'/deploy', base.DeployHandler),
]

