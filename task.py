from abc import ABC, abstractmethod
from typing import Callable

from result import IResult


class ITask(ABC):
    @abstractmethod
    def set_work(self, value: Callable):
        pass

    @abstractmethod
    async def start(self, *args, **kwargs) -> IResult:
        pass


class DefaultTask(ITask):
    def __init__(self, **kwargs):
        self._work = kwargs.get('work')

    def set_work(self, value: Callable):
        self._work = value

    async def start(self, *args, **kwargs) -> IResult:
        return await self._work(*args, **kwargs)
