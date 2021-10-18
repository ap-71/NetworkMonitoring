import asyncio
from abc import ABC, abstractmethod
from typing import Union, List, Tuple
import datetime

from icmplib import async_multiping

from device import IHaveDevice
from result import IResult
from status import IStatus, StopStatus, StartStatus, RestartStatus
from storage.storage import IStorage, IHaveStorage
from subject import DefaultSubjectFacade


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
    @property
    @abstractmethod
    def name(self):
        pass

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


class DefaultServiceFacade(IService, DefaultSubjectFacade, DefaultHaseTimeout):
    def __init__(self, **kwargs):
        self._name = kwargs.get('name', 'Default')
        self._result: IResult = kwargs.get('result')
        self._status_start: IStatus = StopStatus()
        self._status_stop: IStatus = StartStatus()
        self._status_restart: IStatus = RestartStatus()
        self._timeout: float = kwargs.get('timeout', 10.0)
        super().__init__(**kwargs)

    @abstractmethod
    async def _work(self, *args, **kwargs):
        pass

    @property
    def name(self):
        return self._name

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

    @property
    def timeout(self):
        return self._timeout


class SearchDeviceService(DefaultServiceFacade, IHaveDevice):
    def __init__(self, **kwargs):
        self._devices: Union[List, Tuple] = kwargs.pop('devices', list())
        super().__init__(name='NetworkManager', **kwargs)

    def add_device(self, device: str):
        self._devices.append(device)

    def del_device(self, device: str):
        self._devices.remove(device)

    async def _work(self, *args, **kwargs):
        if isinstance(self._devices, tuple):
            self._devices = list(self._devices)
        try:
            results_raw = await async_multiping(self._devices)
            raw_date = datetime.datetime.now()
            date = f'{raw_date.day}.{raw_date.month}.{raw_date.year} {raw_date.hour}.{raw_date.minute}'
            results_final = {self.name: {date: dict()}}
            results_final_with_name = results_final[self.name]
            results_final_with_name_with_date = results_final_with_name[date]

            for result_ping in results_raw:
                results_final_with_name_with_date.update({result_ping.address: result_ping.is_alive})
            self.set_result(results_final)
            await self.sleep()
        except ValueError:
            await asyncio.sleep(30)


class PrintService(DefaultServiceFacade, IHaveStorage):
    def __init__(self, storage=None, **kwargs):
        super().__init__(name='PrintService', **kwargs)
        self._storage: IStorage = storage
        self._timeout: float = kwargs.get('timeout', 60.0)

    def set_storage(self, storage: IStorage) -> IService and IHaveStorage:
        self._storage = storage
        return self

    def get_storage(self) -> IStorage:
        return self._storage

    async def _work(self, *args, **kwargs):
        data = self._storage.get_data()
        if len(data) != 0:
            print(data)
        await self.sleep()

    async def work(self, *args, **kwargs):
        while self._status_start.get_state():
            try:
                await self._work(*args, **kwargs)
            except TypeError:
                pass
