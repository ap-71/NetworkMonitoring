import asyncio
from abc import ABC, abstractmethod
from typing import List, Union, Tuple

from loguru import logger

from device import IHaveDevice
from observer import DefaultObserver
from result import IResult
from server import IServer
from service import IService
from storage import IHaveStorage, IStorageFacade, IHaveStorageFacade
from subject import ISubject


def distribution_between_consumers(src, target):
    """ SRC distribution between TARGET """
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
    def add_service(self, service: IService or List[IService]):
        pass

    @abstractmethod
    def del_service(self, service: IService):
        pass

    @abstractmethod
    def add_server(self, server: IServer or List[IServer]):
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


class NetworkMonitoringFacade(IFacade, IHaveDevice, DefaultObserver, IHaveStorageFacade):

    def set_storage_facade(self, storage_facade: IStorageFacade):
        self._storage_facade = storage_facade
        return self

    def get_storage_facade(self) -> IStorageFacade:
        return self._storage_facade

    async def start_servers(self):
        logger.info('Сервера запущены')
        await asyncio.gather(server.start() for server in self._servers)

    def add_service(self, service: Union[IService, List[IService]]):
        storage_facade = self.get_storage_facade()
        if isinstance(service, IService):
            services = [service]
        elif isinstance(service, list):
            services = service
        else:
            raise TypeError(IService or List[IService])

        for _service in services:
            if isinstance(_service, IHaveStorage):
                _service.set_storage(storage_facade.storage)
            if isinstance(_service, ISubject):
                _service.attach(storage_facade.observer)
            self._services.append(_service)

    def del_service(self, service: IService):
        self._services.remove(service)

    def add_server(self, server: IServer or List[IServer]):
        if isinstance(server, IServer):
            servers = [server]
        elif isinstance(server, list):
            servers = server
        else:
            raise TypeError(IServer or List[IServer])

        storage_facade = self.get_storage_facade()
        for _server in servers:
            if isinstance(_server, IHaveStorage):
                _server.set_storage(storage_facade.storage)
            if isinstance(_server, ISubject):
                _server.attach(storage_facade.observer)
            self._servers.append(_server)

    def del_server(self, server: IServer):
        self._servers.remove(server)

    def add_device(self, device: Union[str, List[str]]):
        if isinstance(device, str):
            device = [device]
        for _device in device:
            self._device.append(_device)
        return self

    def del_device(self, device: str):
        self._device.remove(device)

    def __init__(self, **kwargs):
        super(DefaultObserver, self).__init__()
        self._services: List[IService] = list()
        self._servers: List[IServer] = list()
        self._device = list()
        self._storage_facade = kwargs.get('storage_facade')

    def update(self, result: Union[IResult, List[IResult]]) -> None:
        storage_facade = self.get_storage_facade()
        if isinstance(result, list):
            for res in result:
                storage_facade.storage.add_data(res.get())
        elif isinstance(result, IResult):
            storage_facade.storage.add_data(result.get())

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
