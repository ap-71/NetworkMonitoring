from aiohttp import web

from routes.loader import api_route, router
from routes.utilities.selector import selector
from storage import storage


@router.get('/api/nmf')
@router.get('/api/nmf/{value}')
@router.get('/api/nmf/{value}/{value1}')
@router.get('/api/nmf/{value}/{value1}/{value2}')
@router.get('/api/nmf/{value}/{value1}/{value2}/{value3}')
@router.get('/api/nmf/{value}/{value1}/{value2}/{value3}/{value4}')
async def route(request):
    value = [request.match_info.get('value'),
             request.match_info.get('value1'),
             request.match_info.get('value2'),
             request.match_info.get('value3'),
             request.match_info.get('value4')]
    return web.json_response(selector(value))


@router.get('/api/nmf/mng/device')
async def route(request):
    value = request.match_info.get('value')
    if value is None:
        return web.Response(text=str(storage.storage.get_data()))
    else:
        return web.Response(text=str(storage.storage.get_data(value)))
