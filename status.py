from abc import ABC, abstractmethod


class IStatus(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_state(self) -> bool:
        pass

    @abstractmethod
    def change_state(self, value: bool = None):
        pass


class DefaultStatus(IStatus):
    def __init__(self, **kwargs):
        self._name: str = kwargs.get('name', 'Default')
        self._state: bool = False

    def get_name(self) -> str:
        return self._name

    def get_state(self) -> bool:
        return self._state

    def change_state(self, value: bool = None) -> IStatus:
        if value is None:
            self._state = not self._state
        else:
            self._state = value
        return self


class StartStatus(DefaultStatus):
    def __init__(self):
        super().__init__(name='Start')


class StopStatus(DefaultStatus):
    def __init__(self):
        super().__init__(name='Stop')


class RestartStatus(DefaultStatus):
    def __init__(self):
        super().__init__(name='Restart')
