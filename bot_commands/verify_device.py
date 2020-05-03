from typing import Dict

from nio import RoomMessageText

from bot_commands import Command, runner
from messages import messages


class VerifyDeviceCommand(Command):
    PREFIX = "verify device"
    PARAMS = ["device_id"]

    @runner
    async def run(self, event: RoomMessageText) -> Dict[str, str]:
        params = self.body_to_params(event.body)

        device_id = params["device_id"]

        devices = self.instance.nio_client.store.load_device_keys()
        device = None
        for device in devices.active_user_devices(event.sender):
            if device.device_id == device_id:
                device = device
                break

        if not device:
            return messages.get_content(
                "device_unknown", user_id=event.sender, device_id=device_id,
            )

        self.instance.nio_client.verify_device(device)

        return messages.get_content("device_verified", device_id=device_id)


command_class = VerifyDeviceCommand
