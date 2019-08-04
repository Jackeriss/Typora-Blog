from app.util.config_util import config


redis_pool = None  # type: aioredis.Pool
pg_pool = None  # type: asyncpg.Pool


async def init_redis_pool(loop):
    import aioredis
    global redis_pool
    address, redis_config = config.redis
    redis_pool = await aioredis.create_redis_pool(address, loop=loop, **redis_config)


async def init_pg_pool(loop):
    import asyncpg
    global pg_pool
    pg_config = config.pg
    pg_pool = await asyncpg.create_pool(loop=loop, **pg_config)
    return pg_pool


async def close_pg_pool():
    pg_pool.close()
