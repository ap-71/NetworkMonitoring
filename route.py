from abc import ABC, abstractmethod
from typing import Tuple, Union, List

from aiohttp import web

from result import IResult


# class IRoute(ABC):
#     @abstractmethod
#     def set_path(self, value):
#         pass
#
#     @abstractmethod
#     def set_action(self, value):
#         pass
#
#     @abstractmethod
#     def get_path(self):
#         pass
#
#     @abstractmethod
#     async def get(self, *args, **kwargs) -> IResult:
#         pass
#
#
# class DefaultRoute(IRoute):
#     def __init__(self, **kwargs):
#         self._path = kwargs.get('path', '/')
#         self._action = kwargs.get('action')
#
#     def set_path(self, value) -> IRoute:
#         value += '/' if value[-1] != '/' else ''
#         self._path += value
#         return self
#
#     def set_action(self, value) -> IRoute:
#         self._action = value
#         return self
#
#     def get_path(self):
#         return self._path
#
#     async def get(self, *args, **kwargs) -> IResult:
#         return await self._action(*args, **kwargs)
#
#
# class HTTPHaveRoute(DefaultRoute):
#     def __init__(self, **kwargs):
#         super().__init__(path='/', **kwargs)
#
#
# class APIHaveRoute(DefaultRoute):
#     def __init__(self, **kwargs):
#         super().__init__(path='/api/', **kwargs)

class IRoute(ABC):
    @property
    @abstractmethod
    def prefix(self):
        pass

    @prefix.setter
    @abstractmethod
    def prefix(self, value):
        pass

    @property
    @abstractmethod
    def path(self):
        pass

    @property
    @abstractmethod
    def params(self):
        pass

    @property
    @abstractmethod
    def full_route(self):
        pass

    @abstractmethod
    def handle(self, request):
        pass


class IHaveRoute(ABC):

    @abstractmethod
    def add_route(self, route):
        pass

    @abstractmethod
    def get_routes(self, path) -> Tuple[IRoute]:
        pass

    @abstractmethod
    def del_route(self, route):
        pass


class IHaveHTTPRoute(ABC):
    @property
    @abstractmethod
    def http(self):
        pass


class IHaveAPIRoute(ABC):
    @property
    @abstractmethod
    def api(self):
        pass


class DefaultRoute(IRoute):
    @abstractmethod
    def handle(self, request):
        pass

    @property
    def full_route(self):
        def dict_to_str(value: dict):
            result = str(value)
            result = result.replace('{', '')
            result = result.replace('}', '')
            result = result.replace(': ', '=')
            result = result.replace('\'', '')
            result = result.replace(' ', '')
            return result

        return self.prefix + '/' + '/'.join(self.path) + ('?' if len(self.params) != 0 else '') + dict_to_str(
            self.params)

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self._prefix = value

    @property
    def path(self):
        return self._path

    @property
    def params(self):
        return self._params

    def __init__(self, **kwargs):
        self._prefix: str = kwargs.get('prefix', '')
        self._path: list = kwargs.get('path', list())
        self._params: dict = kwargs.get('params', dict())


class APIRoute(DefaultRoute):

    def handle(self, request):
        raise


class HTTPRoute(DefaultRoute):

    def handle(self, request):
        raise


class DefaultHaveRoute(IHaveRoute):
    def __init__(self, **kwargs):
        self._prefix = kwargs.get('prefix', '')
        self._routes: List[IRoute] = list()
        self.add_route(kwargs.get('routes', list()))

    def add_route(self, route: Union[IRoute, List[IRoute]]):
        if not isinstance(route, list):
            route = [route]
        for route_ in route:
            route_.prefix = self._prefix
        self._routes += route
        return self

    def get_routes(self, path=None) -> Tuple[IRoute]:
        if path is None:
            return *self._routes,
        return *filter(lambda route: route.path == path, self._routes),

    def del_route(self, route):
        self._routes.remove(route)
        return self


class IDecorator(ABC):
    @abstractmethod
    def decorator(self, func):
        pass


class APIHaveRoute(DefaultHaveRoute, IDecorator):
    def __init__(self, **kwargs):
        self._prefix = kwargs.get('prefix', '/api')
        super().__init__(prefix=self._prefix, **kwargs)

    def decorator(self, path):
        def decorator_(func):
            def wrapper():
                route = APIRoute(prefix=self._prefix, path=path)
                route.handle = func
                self.add_route(route)
            wrapper()
        return decorator_


class HTTPHaveRoute(DefaultHaveRoute, IDecorator):
    def __init__(self, **kwargs):
        self._prefix = kwargs.get('prefix', '')
        super().__init__(prefix=self._prefix, **kwargs)

    def decorator(self, path=''):
        def decorator_(func):
            def wrapper():
                route = HTTPRoute(prefix=self._prefix, path=path)
                route.handle = func
                self.add_route(route)
            wrapper()
        return decorator_


