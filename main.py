import asyncio

from facade import NetworkMonitoringFacade
from result import DictResult
from routes import api_route, http_route
from server import HTTPServer
from service import SearchDeviceService
from storage import storage


async def run():
    timeout = 30
    nmf = NetworkMonitoringFacade(storage_facade=storage)
    nmf.add_service([
        *[SearchDeviceService(result=DictResult(), timeout=timeout) for _ in range(15)],
        HTTPServer(http=http_route, api=api_route, port=55080)
    ])
    await nmf.add_device([f'192.168.222.{octet}' for octet in range(1, 255)]).start_services()
    # await nmf.start_services()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.run_forever()
