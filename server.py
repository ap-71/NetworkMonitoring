import os
from abc import ABC, abstractmethod

import aiohttp_jinja2
import jinja2
from aiohttp import web
from loguru import logger

import routes
from route import IHaveHTTPRoute, IHaveAPIRoute, APIHaveRoute, HTTPHaveRoute
from routes import router
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


class HTTPServer(DefaultServer, IHaveHTTPRoute, IHaveAPIRoute):

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
        # for route in [*self._api.get_routes(), *self._http.get_routes()]:
        #     self.app.add_routes([web.get(route.full_route, route.handle)])
        #     full_route_oblique_value = route.full_route + '/{value}'
        #     full_route_value = route.full_route + '{value}'
        #     for value_ in range(1, 5):
        #         self.app.router.add_route('GET', full_route_oblique_value, route.handle)
        #         self.app.router.add_route('GET', full_route_value, route.handle)
        #         full_route_oblique_value += '/{value' + str(value_) + '}'
        #         full_route_value += '/{value' + str(value_) + '}'
        self.app.router.add_routes(router)
        # for route in self._http.get_routes():
        #     self.app.add_routes([web.get(route.full_route, route.handle)])
        #     self.app.add_routes([web.get(route.full_route + '/{value}', route.handle)])
        #     self.app.add_routes([web.get(route.full_route + '{value}', route.handle)])

    def set_storage(self, storage: IStorage) -> IServer and IHaveStorage:
        self._storage = storage
        return self

    def get_storage(self) -> IStorage:
        return self._storage

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
        site_ = web.TCPSite(runner_, self._host, self._port)
        await site_.start()
        logger.info(f"Serving up app on {self._host}:{self._port}")
        return runner_, site_
