import logging

from tornado.log import access_log

logger = access_log

log_formatter = logging.Formatter(
    '[%(asctime)s] $%(levelname)s (%(filename)s:%(lineno)d) %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)


def log_request(handler):
    if handler.get_status() < 400:
        log_method = access_log.info
    elif handler.get_status() < 500:
        log_method = access_log.warning
    else:
        log_method = access_log.error
    request_time = 1000.0 * handler.request.request_time()
    log_method(
        "%d %s %.2fms", handler.get_status(),
        handler._request_summary(), request_time
    )
