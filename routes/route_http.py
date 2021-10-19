import asyncio

import aiohttp_jinja2
from aiohttp import FormData

from routes.loader import http_route, router


# @http_route.decorator()
@router.get('/get')
@router.get('/get/{value}')
@aiohttp_jinja2.template("index.html")
async def route(request):
    text = request.match_info.get('value', "HTTP = Not set value")
    return {
        'title': 'NetworkMonitoring',
        'result': [
            text,
            dict(request.rel_url.query)
        ],

    }


@router.get('/test')
async def upload(request):
    data = FormData()
    data.add_field('package', 'test')
    data.add_field('msg', 'test upload')
    _, response = request.get('/test', data=data)
    return response
