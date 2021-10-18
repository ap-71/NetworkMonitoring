import aiohttp_jinja2
from aiohttp import web

from routes.loader import http_route


@http_route.decorator(['test', '1'])
@aiohttp_jinja2.template("index.html")
def route(request):
    text = request.match_info.get('value', "HTTP = Not set value")
    return {
        'title': 'NetworkMonitoring',
        'result': text
    }
