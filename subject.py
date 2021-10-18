from abc import ABC, abstractmethod
from typing import List

from loguru import logger

from observer import IObserver
from result import IResult, IHaveResult


class ISubject(ABC):
    @abstractmethod
    def attach(self, observer: IObserver) -> None:
        pass

    @abstractmethod
    def detach(self, observer: IObserver) -> None:
        pass

    @abstractmethod
    def notify(self) -> None:
        pass


class DefaultSubjectFacade(ISubject, IHaveResult):
    def set_result(self, value):
        if isinstance(value, IResult):
            self._result.set(value.get())
        else:
            self._result.set(value)

    def get_result(self) -> IResult:
        return self._result

    def __init__(self, **kwargs):
        self._observers: List[IObserver] = list()
        self._result: IResult = kwargs.get('result')

    def attach(self, observer: IObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: IObserver) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self.get_result())
