from aiohttp import web

from matrix_monzo.messages import messages
from matrix_monzo.utils.instance import Instance


class AuthCallbackHandler:
    def __init__(self, instance: Instance):
        self.instance = instance

    async def handler(self, request: web.Request):
        code = request.query.get("code")
        state = request.query.get("state")

        token, room_id = self.instance.get_monzo_access_token(code, state)

        await self.instance.nio_client.room_send(
            room_id,
            "m.room.message",
            messages.get_content("login_success"),
            ignore_unverified_devices=True,
        )

        if 'third_party_developer_app.pre_verification' in token.get('scope', []):
            await self.instance.nio_client.room_send(
                room_id,
                "m.room.message",
                messages.get_content("login_need_app_action"),
                ignore_unverified_devices=True,
            )

        return web.Response(text="yaaay")
