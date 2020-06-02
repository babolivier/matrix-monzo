import logging

from aiohttp import web

from matrix_monzo.http.handlers.auth_callback import AuthCallbackHandler
from matrix_monzo.utils.instance import Instance

logger = logging.getLogger(__name__)


async def start_http(instance: Instance):
    app = web.Application()

    auth_callback = AuthCallbackHandler(instance)

    app.add_routes([
        web.get("/auth_callback", auth_callback.handler),
    ])

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, instance.config.http_address, instance.config.http_port)
    await site.start()

    logger.info("Started HTTP site")
