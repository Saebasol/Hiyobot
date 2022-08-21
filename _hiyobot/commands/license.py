from discord.embeds import Embed

from _hiyobot.registry.command import RegisterCommand
from _hiyobot.handler.app import Context

embed = Embed(
    title="OSS Notice",
    description="This project uses OSS (open source software) under the following licenses.",
)
embed.add_field(
    name="aiohttp",
    value="https://github.com/aio-libs/aiohttp\nCopyright aio-libs contributors.\n[Apache-2.0 License](https://github.com/aio-libs/aiohttp/blob/master/LICENSE.txt)",
    inline=False,
)
embed.add_field(
    name="pynacl",
    value="https://github.com/pyca/pynacl\nCopyright pyca\n[Apache-2.0 License](https://github.com/pyca/pynacl/blob/main/LICENSE)",
    inline=False,
)
embed.add_field(
    name="sanic",
    value="https://github.com/sanic-org/sanic\nCopyright (c) 2016-present Sanic Community\n[MIT License](https://github.com/sanic-org/sanic/blob/main/LICENSE)",
    inline=False,
)
embed.add_field(
    name="discord.py/types",
    value="https://github.com/Rapptz/discord.py\nCopyright (c) Copyright (c) 2015-present Rapptz\n[MIT License](https://github.com/Rapptz/discord.py/blob/master/LICENSE)",
)
embed.add_field(
    name="Mintchoco",
    value="https://github.com/Saebasol/Mintchoco\nCopyright (c) 2021 Saebasol\n[MIT License](https://github.com/Saebasol/Mintchoco/blob/main/LICENSE)",
    inline=False,
)

license = RegisterCommand(
    name="licence", description="Licenses for OSS used in Hiyobot"
)


@license.command()
async def show_license(context: Context):
    context.singleton.webhook_context.create_interaction_response(context.interaction.id, context.interaction.token, session=)
