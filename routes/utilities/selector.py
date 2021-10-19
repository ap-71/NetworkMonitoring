from aiohttp import web

from storage import storage


def selector(values: list):
    if len(list(filter(lambda v: v is not None, values))) == 0:
        return storage.storage.get_data()
    elif values[4] is not None:
        return storage.storage.get_data(values[4])
    elif values[3] is not None:
        return storage.storage.get_data(values[3])
    elif values[2] is not None:
        return storage.storage.get_data(values[2])
    elif values[1] is not None:
        return storage.storage.get_data(values[1])
    elif values[0] is not None:
        return storage.storage.get_data(values[0])
