import logging

from nio import InviteMemberEvent, JoinError, MatrixRoom, RoomMemberEvent, RoomMessageText

from matrix_monzo.commander import Commander
from matrix_monzo.messages import messages
from matrix_monzo.utils.instance import Instance

logger = logging.getLogger(__name__)


class Callbacks:
    def __init__(self, instance: Instance):
        self.instance = instance
        self.commander = Commander(instance)

        # Workaround to https://github.com/matrix-org/synapse/issues/3769
        # Stores the IDs of the rooms we've sent the welcome message to, to prevent them
        # being sent twice.
        self.welcomed = []

    async def message(self, room: MatrixRoom, event: RoomMessageText) -> None:
        if event.sender != self.instance.config.owner_id:
            return

        try:
            await self.instance.nio_client.room_typing(room.room_id)

            device = self.instance.nio_client.device_store.device_from_sender_key(
                event.sender, event.sender_key,
            )
            if not self._user_has_verified_device(event.sender):
                self.instance.nio_client.verify_device(device)
            elif not self.instance.nio_client.store.is_device_verified(device):
                await self.instance.nio_client.room_send(
                    room.room_id,
                    "m.room.message",
                    messages.get_content("unverified_device", device_id=device.device_id),
                )
                return

            res = await self.commander.dispatch(event, room)
        except Exception as e:
            logger.exception(e)
            res = messages.get_content("unknown_error")
        finally:
            await self.instance.nio_client.room_typing(room.room_id, typing_state=False)

        await self.instance.nio_client.room_send(
            room.room_id, "m.room.message", res, ignore_unverified_devices=True,
        )

    def _user_has_verified_device(self, user_id: str):
        devices = self.instance.nio_client.store.load_device_keys()
        verified = False
        for device in devices.active_user_devices(user_id):
            if device.verified:
                verified = True
                break

        return verified

    async def invite(self, room: MatrixRoom, event: InviteMemberEvent) -> None:
        """Callback for when an invite is received. Join the room specified in the invite
        """
        # Only react to invites to us from the configured user.
        if (
            event.membership != "invite"
            or event.sender != self.instance.config.owner_id
            or event.state_key != self.instance.config.user_id
        ):
            return

        logger.info(f"Got invite to {room.room_id} from {event.sender}.")

        # Attempt to join 3 times before giving up
        for attempt in range(3):
            result = await self.instance.nio_client.join(room.room_id)
            if type(result) == JoinError:
                logger.error(
                    f"Error joining room {room.room_id} (attempt %d): %s",
                    attempt, result.message,
                )
            else:
                logger.info(f"Joined {room.room_id}")
                break

    async def member(self, room: MatrixRoom, event: RoomMemberEvent):
        if event.membership != "join" or event.state_key != self.instance.config.user_id:
            return

        if room.room_id in self.welcomed:
            return

        self.welcomed.append(room.room_id)

        await self.instance.nio_client.room_send(
            room.room_id,
            "m.room.message",
            messages.get_content("welcome_message_p1", format_markdown=True),
            ignore_unverified_devices=True,
        )

        await self.instance.nio_client.room_send(
            room.room_id,
            "m.room.message",
            messages.get_content("welcome_message_p2"),
            ignore_unverified_devices=True,
        )

        if not self.instance.is_logged_in():
            await self.instance.nio_client.room_send(
                room.room_id,
                "m.room.message",
                messages.get_content("welcome_message_p3"),
                ignore_unverified_devices=True,
            )
