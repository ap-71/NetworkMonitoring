from aiohttp import web

from routes.loader import api_route
from storage import storage


@api_route.decorator(['nmf', 'search_device'])
def route(request):
    value = request.match_info.get('value')
    if value is None:
        return web.Response(text=str(storage.storage.get_data()))
    else:
        return web.Response(text=str(storage.storage.get_data(value)))


@api_route.decorator(['nmf', 'mng', 'device'])
def route(request):
    value = request.match_info.get('value')
    if value is None:
        return web.Response(text=str(storage.storage.get_data()))
    else:
        return web.Response(text=str(storage.storage.get_data(value)))