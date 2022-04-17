from hiyobot.discord.embeds import Embed
from hiyobot.handler.app import HiyobotRequest
from hiyobot.handler.register import RegisterCommand

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
    name="Mintchoco",
    value="https://github.com/Saebasol/Mintchoco\nCopyright (c) 2021 Saebasol\n[MIT License](https://github.com/Saebasol/Mintchoco/blob/main/LICENSE)",
    inline=False,
)

license = RegisterCommand(name="license", description="")


@license.command(options=None)
async def show_license(request: HiyobotRequest):
    return await request.ctx.response.send(embed=embed)
