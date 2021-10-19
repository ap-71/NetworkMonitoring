from abc import ABC, abstractmethod
from typing import Any, Union, List

from observer import IObserver
from result import IResult, IHaveJSONResult, HTMLResult, JSONResult


class IStorage(ABC):
    @abstractmethod
    def add_data(self, value: dict, key: str = None):
        pass

    @abstractmethod
    def remove_data(self, key):
        pass

    @abstractmethod
    def get_data(self, key=None):
        pass

    @abstractmethod
    def add_key(self, name_key):
        pass


class IHaveStorage(ABC):
    @abstractmethod
    def set_storage(self, storage: IStorage):
        pass

    @abstractmethod
    def get_storage(self) -> IStorage:
        pass


class RAMMemoryStorage(IStorage, IHaveJSONResult):
    def add_key(self, name_key):
        if name_key not in self._storage.keys():
            self._storage[name_key] = dict()

    def __init__(self, **kwargs):
        self._storage = dict()

    def get_data_html(self):
        return HTMLResult(data=self._storage).get()

    def get_data_json(self):
        return JSONResult(data=self._storage).get()

    def add_data(self, value: dict, key: str = None):
        if key is None:
            for key_, value_ in value.items():
                if key_ not in self._storage.keys():
                    self._storage[key_] = value_
                else:
                    for key__, value__ in value_.items():
                        if key__ not in self._storage[key_].keys():
                            self._storage[key_][key__] = value__
                        else:
                            self._storage[key_][key__].update(value__)
        elif key not in self._storage.keys():
            self._storage[key] = value
        else:
            self._storage[key].update(value)

    def remove_data(self, key):
        self._storage.__delitem__(key)

    def get_data(self, key=None) -> Union[dict, Any]:
        try:
            key = key.replace('\'', '')
        except AttributeError:
            pass
        if key is not None:
            def find_key(key_, collection: dict):
                for k, v in collection.items():
                    result = None
                    if k == key_:
                        return v
                    elif isinstance(v, dict):
                        result = find_key(key_, v)
                    if result is not None:
                        return result

            return find_key(key, self._storage)
        else:
            return self._storage


class IStorageFacade(ABC):
    @property
    @abstractmethod
    def storage(self) -> IStorage:
        pass

    @property
    @abstractmethod
    def observer(self) -> IObserver:
        pass


class IHaveStorageFacade(ABC):
    @abstractmethod
    def set_storage_facade(self, storage_facade: IStorageFacade):
        pass

    @abstractmethod
    def get_storage_facade(self) -> IStorageFacade:
        pass


class StorageFacade(IStorageFacade):
    @property
    def storage(self) -> IStorage:
        return self._storage

    @property
    def observer(self) -> IObserver:
        return self._observer

    def __init__(self, storage: IStorage, observer: IObserver = None, **kwargs):
        self._storage: IStorage = storage
        self._observer: IObserver = observer
        if self._observer is not None:
            self._observer.update = self._update
        super().__init__()

    def _update(self, result: Union[IResult, List[IResult]]) -> None:
        if isinstance(result, list):
            for res in result:
                self.storage.add_data(res.get())
        elif isinstance(result, IResult):
            self.storage.add_data(result.get())
