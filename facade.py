import asyncio
from abc import ABC, abstractmethod
from typing import List, Union, Tuple

from loguru import logger

from device import IHaveDevice
from observer import DefaultObserver
from result import IResult
from server import IServer
from service import IService
from storage import IHaveStorage, IStorage


def distribution_between_consumers(src, target):
    count_devices = len(src)
    count_services = len(target)
    remains = count_devices % count_services
    if count_devices < count_services:
        quantity_for_each = 1
    elif remains == 0:
        quantity_for_each = count_devices / count_services
    else:
        quantity_for_each = int((count_devices - remains) / count_services)
    return quantity_for_each


class IFacade(ABC):
    @abstractmethod
    def start_services(self):
        pass

    @abstractmethod
    def start_servers(self):
        pass

    @abstractmethod
    def add_service(self, service: IService):
        pass

    @abstractmethod
    def del_service(self, service: IService):
        pass

    @abstractmethod
    def add_server(self, server: IServer):
        pass

    @abstractmethod
    def del_server(self, server: IServer):
        pass


class DefaultFacade(IFacade):
    def __init__(self):
        self._services: List[IService] = list()
        self._servers: List[IServer] = list()

    async def start_services(self):
        await asyncio.gather(service.start() for service in self._services)

    async def start_servers(self):
        await asyncio.gather(server.start() for server in self._servers)

    def add_service(self, service: IService):
        self._services.append(service)

    def del_service(self, service: IService):
        self._services.remove(service)

    def add_server(self, server: IServer):
        self._servers.append(server)

    def del_server(self, server: IServer):
        self._servers.remove(server)


class DefaultHaveDevice(IHaveDevice):
    def __init__(self):
        self._device = list()

    def add_device(self, device: str):
        self._device.append(device)

    def del_device(self, device: str):
        self._device.remove(device)


class NetworkMonitoringFacade(IFacade, IHaveDevice, DefaultObserver, IHaveStorage):

    async def start_servers(self):
        logger.info('Сервера запущены')
        await asyncio.gather(server.start() for server in self._servers)


    def add_service(self, service: IService):
        self._services.append(service)

    def del_service(self, service: IService):
        self._services.remove(service)

    def add_server(self, server: IServer):
        self._servers.append(server)

    def del_server(self, server: IServer):
        self._servers.remove(server)

    def add_device(self, device: str):
        self._device.append(device)

    def del_device(self, device: str):
        self._device.remove(device)

    def set_storage(self, storage: IStorage):
        self._storage = storage

    def get_storage(self) -> IStorage:
        return self._storage

    def __init__(self, **kwargs):
        super(DefaultObserver, self).__init__()
        self._services: List[IService] = list()
        self._servers: List[IServer] = list()
        self._device = list()
        self._storage: IStorage = kwargs.get('storage')

    def update(self, result: Union[IResult, List[IResult]]) -> None:
        if isinstance(result, list):
            for res in result:
                self.get_storage().add_data(res.get())
        elif isinstance(result, IResult):
            self.get_storage().add_data(result.get())

    async def start_services(self):
        services: Tuple[IHaveDevice] = (*filter(lambda d: isinstance(d, IHaveDevice), self._services),)
        quantity_for_each = distribution_between_consumers(self._device, services)

        for service in services:
            for device in range(quantity_for_each):
                try:
                    service.add_device(self._device.pop(device))
                except IndexError:
                    break

        logger.info('Службы запущены')
        await asyncio.gather(*(service.start() for service in self._services))
