from abc import ABC, abstractproperty
from asyncio import create_task, sleep
from types import SimpleNamespace
from typing import Any, Optional, cast

from mintchoco.client import Mintchoco
from multidict import CIMultiDict
from nacl.exceptions import BadSignatureError  # type: ignore
from nacl.signing import VerifyKey  # type: ignore
from sanic import HTTPResponse, Request
from sanic.app import Sanic
from sanic.exceptions import Unauthorized
from sanic.response import json

from hiyobot.discord.embeds import Embed
from hiyobot.discord.interactions import Interaction
from hiyobot.discord.types.interactions import (
    ApplicationCommandInteractionData,
    ComponentInteractionData,
)
from hiyobot.handler.http import BaseHTTP, DiscordBaseHTTP
from hiyobot.handler.register import RegisterCommand, RegisterdInfo
from hiyobot.handler.types import CORO


class Component(ABC):
    def __init__(self) -> None:
        self._timeout = 60
        self.start_check_timeout = False

    @abstractproperty
    def raw(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractproperty
    def mapping(self) -> dict[str, Any]:
        raise NotImplementedError

    async def timeout_manager(self, hiyobot: "Hiyobot"):
        self.start_check_timeout = True
        while True:
            await sleep(1)
            self._timeout -= 1

            if self._timeout <= 0:
                break

        hiyobot.components = {k: v for k, v in hiyobot.components.items() if v != self}

    async def interaction_check(self, request: "HiyobotRequest") -> bool:
        return True

    async def execute(self, custom_id: str, request: "HiyobotRequest"):
        self._timeout = 60
        if await self.interaction_check(request):
            await self.mapping[custom_id](request)


class Response:
    def __init__(self, request: "HiyobotRequest") -> None:
        self.request = request

    def make_res(
        self,
        type: int,
        content: Optional[str] = None,
        embed: Optional[Embed] = None,
        ephemeral: bool = False,
        component: Optional[Component] = None,
    ):
        res: dict[str, Any] = {"type": type, "data": {}}

        if content:
            res["data"]["content"] = content
        if embed:
            res["data"]["embeds"] = [embed.to_dict()]

        if ephemeral:
            res["data"].update({"flags": 1 << 6})

        if component:
            if type == 4:
                self.request.app.ctx.handler.component_register(component)
            res["data"].update(component.raw)
        return res

    async def delete(self):
        interaction = self.request.ctx.interaction
        await self.request.respond(json({"type": 6}))
        path = f"/webhooks/{interaction.application_id}/{interaction.token}/messages/@original"
        create_task(self.request.app.ctx.http.delete(path))

    async def follow_up_send(
        self,
        content: Optional[str] = None,
        embed: Optional[Embed] = None,
        ephemeral: bool = False,
        component: Optional[Component] = None,
    ):
        interaction = self.request.ctx.interaction
        res = self.make_res(4, content, embed, ephemeral, component)
        path = f"/webhooks/{interaction.application_id}/{interaction.token}"
        await self.request.app.ctx.http.post(path, json=res["data"])

    async def wait(self, callback: CORO):
        await self.request.respond(json({"type": 5}))
        create_task(callback())

    async def edit(
        self,
        content: Optional[str] = None,
        *,
        embed: Optional[Embed] = None,
        ephemeral: bool = False,
        component: Optional[Component] = None,
    ) -> HTTPResponse:
        res = self.make_res(7, content, embed, ephemeral, component)
        respond: HTTPResponse = await self.request.respond(json(res))
        return respond

    async def send(
        self,
        content: Optional[str] = None,
        *,
        embed: Optional[Embed] = None,
        ephemeral: bool = False,
        component: Optional[Component] = None,
    ) -> HTTPResponse:
        res = self.make_res(4, content, embed, ephemeral, component)
        respond: HTTPResponse = await self.request.respond(json(res))
        return respond


class HiyobotContext(SimpleNamespace):
    mintchoco: Mintchoco
    http: DiscordBaseHTTP
    handler: "Hiyobot"
    request: BaseHTTP


class HiyobotRequestContext(SimpleNamespace):
    interaction: Interaction
    response: Response


class HiyobotSanic(Sanic):
    ctx: HiyobotContext


class HiyobotRequest(Request):
    app: HiyobotSanic
    headers: CIMultiDict[Any]
    json: Any
    body: bytes
    ctx: HiyobotRequestContext


class Hiyobot:
    commands: dict[str, RegisterdInfo] = {}
    components: dict[str, Component] = {}

    def __init__(
        self,
        client_public_key: str,
        token: str,
        uri: str = "discord_interaction",
        production: bool = False,
    ) -> None:
        self.sanic = Sanic("hiyobot")
        self.uri = uri
        self.token = token
        self.client_public_key = client_public_key

        self.__setup()

    def __setup(self):
        self.sanic.add_route(self.__handler, self.uri, ["POST"])

        # Injection
        self.sanic.ctx.http = DiscordBaseHTTP(self.token)
        self.sanic.ctx.mintchoco = Mintchoco()
        self.sanic.ctx.handler = self
        self.sanic.ctx.request = BaseHTTP()

    def command_register(self, info: RegisterCommand):
        self.commands.update({info.registerd_info.name: info.registerd_info})

    def component_register(self, component: Component):
        for k in component.mapping.keys():
            self.components[k] = component

        if not component.start_check_timeout:
            create_task(component.timeout_manager(self))

    @staticmethod
    def verify_signiture(
        raw_body: bytes, signature: str, timestamp: str, client_public_key: str
    ):
        message = timestamp.encode() + raw_body
        try:
            vk = VerifyKey(bytes.fromhex(client_public_key))
            vk.verify(message, bytes.fromhex(signature))  # type: ignore
            return True
        except BadSignatureError:
            return False

    async def __handler(self, request: HiyobotRequest):
        request.ctx.response = Response(request)
        request.ctx.interaction = Interaction(request.json)
        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")
        if (
            signature
            and timestamp
            and self.verify_signiture(
                request.body, signature, timestamp, self.client_public_key
            )
        ):
            if request.json["type"] == 1:
                return json({"type": 1})

            if request.json["type"] == 2:
                return await self.dispatch_application_command(request)

            if request.json["type"] == 3:
                return await self.dispatch_message_component(request)

        raise Unauthorized("not_verified", 401)

    async def dispatch_application_command(self, request: HiyobotRequest):
        if request.ctx.interaction.data:
            interaction_data = cast(
                ApplicationCommandInteractionData, request.ctx.interaction.data
            )

            if interaction_data.get("type") == 1:
                if interaction_data["name"] in self.commands:
                    command = self.commands[interaction_data["name"]]
                    if interaction_options := interaction_data.get("options"):
                        option = interaction_options[0]
                        # Handle Subcommand
                        if option["type"] == 1:
                            if option["name"] in command.sub_command:
                                sub_command_func = command.sub_command[option["name"]]
                                await sub_command_func(
                                    request,
                                    *tuple(map(lambda x: x["value"], option["options"])),  # type: ignore
                                )
                        # Handle Single Command
                        else:
                            if interaction_data["name"] in command.single_command:
                                single_command_func = command.single_command[
                                    interaction_data["name"]
                                ]
                                await single_command_func(
                                    request,
                                    *tuple(
                                        map(lambda x: x["value"], option["options"])  # type: ignore
                                    ),
                                )

            # TODO: Handle Subcommand Group

    async def dispatch_message_component(self, request: HiyobotRequest):
        request.ctx.interaction = Interaction(request.json)
        if request.ctx.interaction.data:
            interaction_data = cast(
                ComponentInteractionData, request.ctx.interaction.data
            )
            custom_id = interaction_data["custom_id"]
            if custom_id in self.components:
                await self.components[custom_id].execute(
                    interaction_data["custom_id"], request
                )
            else:
                await request.ctx.response.send("만료된 상호작용이에요.", ephemeral=True)
