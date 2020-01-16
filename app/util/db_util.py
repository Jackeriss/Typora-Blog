from app.util.config_util import config


POOL = {"redis": None}


async def init_redis_pool(loop):
    import aioredis

    address, redis_config = config.redis
    POOL["redis"] = await aioredis.create_redis_pool(address, loop=loop, **redis_config)
