from app.util import db_util


def init_redis_pool(app):
    async def init_redis_pool():
        await db_util.init_redis_pool(app.loop)

    app.loop.run_until_complete(init_redis_pool())
