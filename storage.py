from abc import ABC, abstractmethod
import datetime
from typing import Any, Union, List

from observer import IObserver
from result import IResult


class IStorage(ABC):
    @abstractmethod
    def add_data(self, value: dict):
        pass

    @abstractmethod
    def remove_data(self, key):
        pass

    @abstractmethod
    def update_data(self, value: dict):
        pass

    @abstractmethod
    def get_data(self, key=None):
        pass


class IHaveStorage(ABC):
    @abstractmethod
    def set_storage(self, storage: IStorage):
        pass

    @abstractmethod
    def get_storage(self) -> IStorage:
        pass


class RAMMemoryStorage(IStorage):
    def add_data(self, value: dict):
        self.update_data(value)

    def remove_data(self, key):
        self._storage.__delitem__(key)

    def update_data(self, value: dict):
        raw_date = datetime.datetime.now()
        date = f'{raw_date.day}.{raw_date.month}.{raw_date.year} {raw_date.hour}.{raw_date.minute}'
        if date not in self._storage:
            self._storage[date] = value
        else:
            if isinstance(self._storage[date], dict):
                self._storage[date].update(value)

    def get_data(self, key=None) -> Union[dict, Any]:
        if key is not None:
            return self._storage.get(key)
        else:
            return self._storage

    def __init__(self):
        self._storage = dict()


class IStorageFacade(ABC):
    @property
    @abstractmethod
    def storage(self):
        pass

    @property
    @abstractmethod
    def observer(self):
        pass


class StorageFacade(IStorageFacade):
    @property
    def storage(self) -> IStorage:
        return self._storage

    @property
    def observer(self) -> IObserver:
        return self._observer

    def __init__(self, **kwargs):
        self._storage: IStorage = kwargs.pop('storage')
        self._observer: IObserver = kwargs.pop('observer')
        self._observer.update = self._update
        super().__init__()

    def _update(self, result: Union[IResult, List[IResult]]) -> None:
        if isinstance(result, list):
            for res in result:
                self.storage.add_data(res.get())
        elif isinstance(result, IResult):
            self.storage.add_data(result.get())
