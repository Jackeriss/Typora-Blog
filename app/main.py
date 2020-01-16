import os
import logging
import sys
import asyncio

from tornado import httpserver
from tornado.log import enable_pretty_logging
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.process import fork_processes
from tornado.netutil import bind_sockets

from app import application, router
from app.hook import before_hook, after_hook
from app.tasks import delay_task, periodic_task
from app.util.config_util import config
from app.util.thread_pool_util import ThreadPool


enable_pretty_logging()
debug = config.server["debug"]
root_logger = logging.getLogger()
if debug:
    root_logger.setLevel(logging.DEBUG)
else:
    root_logger.setLevel(logging.WARNING)


BEFORE_HOOKS = [before_hook.wrap_handler]

AFTER_HOOKS = [
    after_hook.init_redis_pool
]

DELAY_TASKS = []

PERIODIC_TASKS = [
    {"callback": periodic_task.delete_expired_local_cache, "callback_time": 1000}
]

MODEL_ROUTERS = [{"routers": router.ROUTERS, "prefix": ""}]


def main():
    settings = config.server
    settings["static_path"] = config.static_path
    settings["template_path"] = config.template_path
    port = settings.pop("port")
    address = settings.pop("host")
    sockets = bind_sockets(port, address=address)

    if sys.platform != "win32":
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    AsyncIOMainLoop().install()
    loop = asyncio.get_event_loop()
    ThreadPool.init_thread_pool(workers=config.server["thread_worker"])

    app = application.Application(
        settings=settings,
        loop=loop,
        model_routers=MODEL_ROUTERS,
        before_hooks=BEFORE_HOOKS,
        after_hooks=AFTER_HOOKS,
        delay_tasks=DELAY_TASKS,
        periodic_tasks=PERIODIC_TASKS,
    )

    app.start_periodic_tasks()
    app.start_delay_tasks()
    server = httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    logging.debug(f"🚀 Server ready at http://{address}:{port}")
    loop.run_forever()


if __name__ == "__main__":
    main()
