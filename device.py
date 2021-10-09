from abc import ABC, abstractmethod


class IHaveDevice(ABC):
    @abstractmethod
    def add_device(self, device: str):
        pass

    @abstractmethod
    def del_device(self, device: str):
        pass
