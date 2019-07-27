import logging
import sys
import asyncio
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.options import options, parse_command_line
from tornado.options import define

from src.service.cache import cache
from src.app import TornadoApplication

py_version = sys.version_info


def main():
    define('port', help='run on the given port', type=int)
    parse_command_line()
    AsyncIOMainLoop().install()
    loop = asyncio.get_event_loop()
    logging.info('loading data to cache')
    cache.load()
    app = TornadoApplication()
    app.listen(options.port)
    logging.info(f'Ready to serve at http://0.0.0.0:{options.port}')
    loop.run_forever()

if __name__ == '__main__':
    main()
