import asyncio
from abc import ABC, abstractmethod
from typing import Union, List, Tuple

from icmplib import async_ping, async_multiping

from device import IHaveDevice
from result import IResult, IHaveResult
from status import IStatus
from storage import IStorage
from subject import DefaultSubject


class IHaseTimeout(ABC):
    @abstractmethod
    async def sleep(self):
        pass

    @property
    @abstractmethod
    def timeout(self):
        pass

    @timeout.setter
    @abstractmethod
    def timeout(self, value: float):
        pass


class DefaultHaseTimeout(IHaseTimeout):

    @property
    @abstractmethod
    def timeout(self):
        return self._timeout

    def __init__(self, **kwargs):
        self._timeout: float = kwargs.get('timeout', 10.0)

    async def sleep(self):
        await asyncio.sleep(self.timeout)


class IService(ABC):
    @abstractmethod
    async def start(self, *args, **kwarg) -> IResult:
        pass

    @abstractmethod
    async def stop(self):
        pass

    @abstractmethod
    async def restart(self):
        pass

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    async def _work(self, *args, **kwargs):
        pass

    @abstractmethod
    async def work(self, *args, **kwargs) -> IResult:
        pass

    @abstractmethod
    def set_status_start(self, status: IStatus):
        pass

    @abstractmethod
    def set_status_stop(self, status: IStatus):
        pass

    @abstractmethod
    def set_status_restart(self, status: IStatus):
        pass


class DefaultService(IService, DefaultSubject, DefaultHaseTimeout):
    @abstractmethod
    async def _work(self, *args, **kwargs):
        pass

    def __init__(self, **kwargs):
        self._name = kwargs.get('name', 'Default')
        self._result: IResult = kwargs.get('result')
        self._status_start: IStatus = kwargs.get('status_start')
        self._status_stop: IStatus = kwargs.get('status_stop')
        self._status_restart: IStatus = kwargs.get('status_restart')
        super().__init__(**kwargs)

    def set_status_start(self, status: IStatus) -> IService:
        self._status_start = status
        return self

    def set_status_stop(self, status: IStatus) -> IService:
        self._status_stop = status
        return self

    def set_status_restart(self, status: IStatus) -> IService:
        self._status_restart = status
        return self

    async def work(self, *args, **kwargs):
        while self._status_start.get_state():
            try:
                await self._work(*args, **kwargs)
                self.notify()
            except TypeError:
                pass

    def get_name(self):
        return self._name

    async def start(self, *args, **kwarg):
        self._status_stop.change_state(False)
        self._status_start.change_state(True)
        await self.work(*args, **kwarg)

    async def stop(self):
        self._status_stop.change_state(True)
        self._status_start.change_state(False)

    async def restart(self, **kwargs):
        await self.stop()
        await self.start(**kwargs)


class SearchDeviceService(DefaultService, IHaveDevice):
    def add_device(self, device: str):
        self._devices.append(device)

    def del_device(self, device: str):
        self._devices.remove(device)

    @property
    def timeout(self):
        return self._timeout

    def __init__(self, **kwarg):
        self._devices: Union[List, Tuple] = kwarg.pop('devices', list())
        self._timeout: float = kwarg.get('timeout', 10.0)
        super().__init__(**kwarg)

    async def _work(self, *args, **kwargs):
        if isinstance(self._devices, tuple):
            self._devices = list(self._devices)
        result = await async_multiping(self._devices)
        results = dict()
        for result_ping in result:
            results.update({result_ping.address: result_ping.is_alive})
        self.set_result(self._result.set(results))
        await self.sleep()


class PrintService(DefaultService):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._storage: IStorage = kwargs.pop('storage')
        self._timeout: float = kwargs.get('timeout', 60.0)

    async def _work(self, *args, **kwargs):
        print(self._storage.get_data())
        await self.sleep()

    async def work(self, *args, **kwargs):
        while self._status_start.get_state():
            try:
                await self._work(*args, **kwargs)
            except TypeError:
                pass

    @property
    def timeout(self):
        return self._timeout
