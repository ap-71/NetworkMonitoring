import json
from abc import ABC, abstractmethod


class IResult(ABC):
    @abstractmethod
    def set(self, value):
        pass

    @abstractmethod
    def get(self):
        pass


class IHaveResult(ABC):
    @abstractmethod
    def get_result(self) -> IResult:
        pass

    @abstractmethod
    def set_result(self, value):
        pass


class DefaultResult(IResult):
    def __init__(self, **kwargs):
        self._result = kwargs.get('data')

    def set(self, value) -> IResult:
        self._result = value
        return self

    def get(self):
        return self._result


class JSONResult(DefaultResult):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self):
        return json.dumps(self._result)


class HTMLResult(DefaultResult):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self):
        return f'<html lang="en"><head><style></style><title></title></head><body>{self._result}</body></html>'


class DictResult(DefaultResult):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get(self):
        result = dict()
        if isinstance(self._result, list) or isinstance(self._result, tuple):
            for i in range(0, len(self._result), 2):
                try:
                    result[self._result[i]] = self._result[i + 1]
                except IndexError:
                    result[self._result[i]] = ''

        elif isinstance(self._result, dict):
            result = self._result
        else:
            result['data'] = self._result
        return result
