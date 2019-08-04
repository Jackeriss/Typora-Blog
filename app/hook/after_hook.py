"""在 Application 初始化之后调用"""
from app.util import db_util


def init_redis_pool(app):
    """初始化 redis 连接池"""

    async def init_redis_pool():
        await db_util.init_redis_pool(app.loop)

    app.loop.run_until_complete(init_redis_pool())


def init_pg_pool(app):
    """初始化 pg 连接池"""

    async def init_pg_pool():
        await db_util.init_pg_pool(app.loop)

    app.loop.run_until_complete(init_pg_pool())
