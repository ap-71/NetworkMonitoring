from abc import ABC, abstractmethod

from result import IResult


class IRoute(ABC):
    @abstractmethod
    def set_path(self, value):
        pass

    @abstractmethod
    def set_action(self, value):
        pass

    @abstractmethod
    def get_path(self):
        pass

    @abstractmethod
    async def get(self, *args, **kwargs) -> IResult:
        pass


class DefaultRoute(IRoute):
    def __init__(self, **kwargs):
        self._path = kwargs.get('path', '/')
        self._action = kwargs.get('action')

    def set_path(self, value) -> IRoute:
        value += '/' if value[-1] != '/' else ''
        self._path += value
        return self

    def set_action(self, value) -> IRoute:
        self._action = value
        return self

    def get_path(self):
        return self._path

    async def get(self, *args, **kwargs) -> IResult:
        return await self._action(*args, **kwargs)


class HTTPRoute(DefaultRoute):
    def __init__(self, **kwargs):
        super().__init__(path='/', **kwargs)


class APIRoute(DefaultRoute):
    def __init__(self, **kwargs):
        super().__init__(path='/api/', **kwargs)
