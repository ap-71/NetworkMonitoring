from abc import ABC, abstractmethod
from typing import List, Union

from result import IResult, IHaveResult


class IObserver(ABC):
    @abstractmethod
    def update(self, result: Union[IResult, List[IResult]]) -> None:
        pass


class DefaultObserver(IObserver, IHaveResult):

    def set_result(self, value):
        self._results.append(value)

    def get_result(self) -> List[IResult]:
        return self._results

    def update(self, result: Union[IResult, List[IResult]]) -> None:
        self._results.append(result)

    def __init__(self):
        self._results: List[IResult] = list()
