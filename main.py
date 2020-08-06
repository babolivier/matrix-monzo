#!/usr/bin/env python3

import asyncio
import logging

from nio import (
    InviteMemberEvent,
    LoginError,
    RoomMemberEvent,
    RoomMessageText,
)

from matrix_monzo.callbacks import Callbacks
from matrix_monzo.config import Config
from matrix_monzo.http import start_http
from matrix_monzo.utils.instance import Instance

logger = logging.getLogger("matrix_monzo.main")


async def main():
    # Read config file and configure login.
    config = Config("config.yaml")

    # Initiate the instance object which will contain everything commands need to run.
    instance = Instance(config)

    # Start the aiohttp server.
    await start_http(instance)

    # Authenticate against the Matrix homeserver.
    login_resp = await instance.nio_client.login(config.password, "monzo_bot")

    # If the homeserver responded with an error, tell the client about it.
    if isinstance(login_resp, LoginError):
        logger.error("Login failed with error: %s" % login_resp.message)
        await instance.nio_client.close()
        return

    logger.info("Authenticated on the homeserver")

    # Set up event callbacks.
    callbacks = Callbacks(instance)
    instance.nio_client.add_event_callback(callbacks.message, (RoomMessageText,))
    instance.nio_client.add_event_callback(callbacks.invite, (InviteMemberEvent,))
    instance.nio_client.add_event_callback(callbacks.member, (RoomMemberEvent,))

    logger.info("Registered Matrix handlers")

    # Run the instance's main loop.
    await instance.run()

asyncio.get_event_loop().run_until_complete(main())