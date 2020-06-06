import os

from aiohttp import web

from matrix_monzo.messages import messages
from matrix_monzo.utils.instance import Instance


class AuthCallbackHandler:
    def __init__(self, instance: Instance):
        self.instance = instance

        res_dir = os.path.join(os.path.dirname(__file__), "../../../res")
        success_html_path = os.path.join(res_dir, "login_success.html")
        failure_html_path = os.path.join(res_dir, "login_failure.html")

        with open(success_html_path) as fp:
            self.success_html = fp.read()

        with open(failure_html_path) as fp:
            self.failure_html = fp.read()

    async def handler(self, request: web.Request):
        code = request.query.get("code")
        state = request.query.get("state")
        try:
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

            return web.Response(text=self.success_html, content_type="text/html")
        except Exception:
            return web.Response(text=self.failure_html, content_type="text/html")
