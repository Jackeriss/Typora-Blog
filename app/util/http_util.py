import asyncio
import functools
import logging

import aiohttp
import json

from app.util.config_util import config


def as_asyncio_task(func):
    @functools.wraps(func)
    async def _wrapper(self, *args, **kwargs):
        coro = func(self, *args, **kwargs)
        return await asyncio.ensure_future(coro)

    return _wrapper


class HTTPClient:
    _session = None

    @classmethod
    async def get_session(cls):
        if cls._session is None:
            cls._session = aiohttp.ClientSession()
        return cls._session

    @as_asyncio_task
    async def request(
        self, url, *, method="GET", response_format=None, timeout=5, retry=2, **kwargs,
    ):
        session = await self.get_session()
        func = getattr(session, method.lower())
        logging.debug(f"url: {url} params: {kwargs}")
        response = None
        while retry:
            retry -= 1
            try:
                response = await func(url, timeout=timeout, **kwargs)
                response.text_data = await response.text()
                if response_format == "json":
                    response.json_data = json.loads(response.text_data)
            except asyncio.TimeoutError:
                logging.error(
                    f"request timeout {timeout}!request url:{url} kwargs:{kwargs}"
                )
                break
            except Exception as exception:
                logging.exception(
                    "request failed. retry#{}\nurl:{}\nargs:{}\nresponse:{}\nexception:{}".format(
                        retry, url, kwargs, response, exception
                    )
                )
                continue
            else:
                if response.status != 200:
                    logging.warning(
                        "response status!=200 response:{} {}\nurl:{}\nargs:{}".format(
                            response.status, response.text_data, url, kwargs
                        )
                    )
                break
        return response

    get = functools.partialmethod(request, method="GET")
    post = functools.partialmethod(request, method="POST")
    put = functools.partialmethod(request, method="PUT")
    delete = functools.partialmethod(request, method="DELETE")
    head = functools.partialmethod(request, method="HEAD")
    option = functools.partialmethod(request, method="OPTION")


http_client = HTTPClient()
