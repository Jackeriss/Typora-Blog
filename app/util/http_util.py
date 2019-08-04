import asyncio
import functools
import logging

import aiohttp


def as_asyncio_task(func):
    """ aiohttp 的超时机制需要在 asyncio task 中执行 """

    @functools.wraps(func)
    async def _wrapper(self, *args, **kwargs):
        coro = func(self, *args, **kwargs)
        return await asyncio.ensure_future(coro)

    return _wrapper


class HTTPClient:
    """ HTTP 客户端 """
    _session = None

    @classmethod
    async def get_session(cls):
        if cls._session is None:
            cls._session = aiohttp.ClientSession()
        return cls._session

    @as_asyncio_task
    async def request(self, url, *, method="GET", format=None, timeout=3, retry=3, **kwargs):
        session = await self.get_session()
        func = getattr(session, method.lower())
        logging.debug(f"url: {url} params: {kwargs}")
        response = None
        while retry:
            retry -= 1
            try:
                response = await func(url, timeout=timeout, **kwargs)
                response.text_data = await response.text()
                if format == "json":
                    response.json_data = await response.json(content_type=None)
            except asyncio.TimeoutError:
                logging.error(
                    f"request timeout {timeout}!request url:{url} kwargs:{kwargs}")
                break
            except Exception as exception:
                logging.exception("request failed. retry#{}\nurl:{}\nargs:{}\nresponse:{}\nexception:{}".format(
                    retry, url, kwargs, response, exception))
                continue
            else:
                if response.status != 200:
                    logging.warning("response status!=200 response:{} {}\nurl:{}\nargs:{}".format(
                        response.status, response.text_data, url, kwargs))
                break
        return response

    get = functools.partialmethod(request, method="GET")
    post = functools.partialmethod(request, method="POST")
    put = functools.partialmethod(request, method="PUT")
    delete = functools.partialmethod(request, method="DELETE")
    head = functools.partialmethod(request, method="HEAD")
    option = functools.partialmethod(request, method="OPTION")


http_client = HTTPClient()
