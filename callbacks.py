import logging

from monzo import Monzo
from nio import AsyncClient, InviteEvent, JoinError, MatrixRoom, RoomMessageText

from commander import Commander
from config import Config
from messages import messages

logger = logging.getLogger(__name__)


class Callbacks:
    def __init__(self, config: Config, nio_client: AsyncClient, monzo_client: Monzo):
        self.config = config
        self.nio_client = nio_client
        self.monzo_client = monzo_client
        self.commander = Commander(config, nio_client, monzo_client)

    async def message(self, room: MatrixRoom, event: RoomMessageText) -> None:
        if event.sender != self.config.owner_id:
            return

        device = self.nio_client.device_store.device_from_sender_key(
            event.sender, event.sender_key,
        )
        if not self._user_has_verified_device(event.sender):
            self.nio_client.verify_device(device)
        elif not self.nio_client.store.is_device_verified(device):
            await self.nio_client.room_send(
                room.room_id,
                "m.room.message",
                messages.get_content("unverified_device", device_id=device.device_id),
            )
            return

        res = await self.commander.dispatch(event)
        await self.nio_client.room_send(
            room.room_id, "m.room.message", res, ignore_unverified_devices=True,
        )

    def _user_has_verified_device(self, user_id: str):
        devices = self.nio_client.store.load_device_keys()
        verified = False
        for device in devices.active_user_devices(user_id):
            if device.verified:
                verified = True
                break

        return verified

    async def invite(self, room: MatrixRoom, event: InviteEvent) -> None:
        """Callback for when an invite is received. Join the room specified in the invite
        """
        logger.debug(f"Got invite to {room.room_id} from {event.sender}.")

        # Only react to messages from the configured user.
        if event.sender != self.config.owner_id:
            logger.debug("Ignoring the invite")
            return

        # Attempt to join 3 times before giving up
        for attempt in range(3):
            result = await self.nio_client.join(room.room_id)
            if type(result) == JoinError:
                logger.error(
                    f"Error joining room {room.room_id} (attempt %d): %s",
                    attempt, result.message,
                )
            else:
                logger.info(f"Joined {room.room_id}")
                break

        return None
