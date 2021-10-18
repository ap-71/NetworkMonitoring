import asyncio
import os
from abc import ABC, abstractmethod

import aiohttp_jinja2
import jinja2
from aiohttp import web
from loguru import logger

from result import IHaveJSONResult, IHaveHTMLResult
from route import IHaveHTTPRoute, IHaveAPIRoute, APIHaveRoute, HTTPHaveRoute, DefaultRoute
from routes import api_route
from service import DefaultServiceFacade
from storage import IHaveStorage, IStorage


class IServer(DefaultServiceFacade, ABC):
    """ TODO Implementation """


class DefaultServer(IServer, IHaveStorage):
    @abstractmethod
    async def _work(self, *args, **kwargs):
        pass

    @property
    def timeout(self):
        return

    def __init__(self, **kwargs):
        self._storage: IStorage = kwargs.get('storage')
        super().__init__(**kwargs)


class IRequest(ABC):
    @abstractmethod
    def request(self, value):
        pass


class IResponse(ABC):
    @abstractmethod
    def response(self):
        pass


class IRRFacade(IRequest, IResponse, ABC):
    """ RR == ResponseRequest"""


class DefaultRRFacade(IRRFacade):
    def __init__(self):
        self._data = None

    @abstractmethod
    async def request(self, value):
        pass

    async def response(self):
        return self._data


class HTTPServer(DefaultServer, IHaveHTTPRoute, IHaveAPIRoute, IRRFacade):

    def __init__(self, **kwargs):
        super().__init__(name='HTTP Server', **kwargs)
        self._http: HTTPHaveRoute = kwargs.get('http')
        self._api: APIHaveRoute = kwargs.get('api')
        self._port = kwargs.get('port', 8080)
        self._host = kwargs.get('host', '127.0.0.1')
        self.app = web.Application()
        aiohttp_jinja2.setup(
            self.app, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                  'templates'))
        )
        for route in self._api.get_routes():
            self.app.add_routes([web.get(route.full_route, route.handle)])
            self.app.add_routes([web.get(route.full_route + '/{value}', route.handle)])
        for route in self._http.get_routes():
            self.app.add_routes([web.get(route.full_route, route.handle)])
            self.app.add_routes([web.get(route.full_route + '/{value}', route.handle)])

    def set_storage(self, storage: IStorage) -> IServer and IHaveStorage:
        self._storage = storage
        return self

    def get_storage(self) -> IStorage:
        return self._storage

    def request(self, value):
        pass

    def response(self):
        pass

    @property
    def http(self) -> HTTPHaveRoute:
        return self._http

    @property
    def api(self) -> APIHaveRoute:
        return self._api

    async def _work(self, *args, **kwargs):
        pass

    async def work(self, *args, **kwargs):
        runner_ = web.AppRunner(self.app)

        await runner_.setup()
        site_ = web.TCPSite(runner_, '127.0.0.1', self._port)
        await site_.start()
        logger.info(f"Serving up app on 127.0.0.1:{self._port}")
        return runner_, site_

    # @api_route.decorator(['w', 'r'])
    # async def handle(self, request):
    #     # value = request.match_info.get('value', "Not set value")
    #     # text = value
    #     try:
    #         storage = self.get_storage()
    #         if isinstance(storage, IHaveJSONResult):
    #             return web.Response(text=storage.get_data_json())
    #         elif isinstance(storage, IHaveHTMLResult):
    #             return web.Response(text=str(storage.get_data_html()),
    #                                 content_type='text/html')
    #         else:
    #             return web.Response(text=str(storage.get_data()))
    #     except AttributeError as ar:
    #         return web.Response(text='ERR 404 = ' + str(ar))

# if __name__ == '__main__':
#     routes = [DefaultRoute(path=[f'aaa{i}', f'ddd{i}', f'fff{i}']) for i in range(13)]
#     http_server = HTTPServer(api=APIHaveRoute(routes=routes))
#     loop = asyncio.get_event_loop()
#     runner, site = loop.run_until_complete(http_server.work())
#     try:
#         loop.run_forever()
#     except KeyboardInterrupt as err:
#         loop.run_until_complete(runner.cleanup())
