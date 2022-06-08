from typing import Literal, get_args
from hiyobot.discord.embeds import Embed
from hiyobot.handler.app import HiyobotRequest
from hiyobot.handler.register import CommandArgument, RegisterCommand
from hiyobot.utils import is_nsfw
from random import choice


BASE_URL = "https://neko-love.xyz/api/"
VERSION = "v1"
URL = BASE_URL + VERSION

sfw_tags = [
    "neko",
    "kitsune",
    "hug",
    "pat",
    "waifu",
    "cry",
    "kiss",
    "slap",
    "smug",
    "punch",
]

nsfw_tags = ["nekolewd"]


main_embed = Embed(colour=0xC44BAB)
main_embed.set_footer(
    text="With Neko-love",
    icon_url="https://neko-love.xyz/assets/icon-min.png",
)

anekos = RegisterCommand(name="네코", description="귀여운 네코미미를 보여줍니다. 태그를 사용해서 검색도 가능합니다.")


@anekos.sub_command(name="도움말", description="태그 목록을 가져옵니다.")
async def neko_help(request: HiyobotRequest):
    embed = Embed(title="사용할 수 있는 태그 목록입니다.")
    embed.add_field(name="전연령 태그", value="\n".join(sfw_tags))
    if await is_nsfw(request):
        embed.add_field(name="성인 태그", value="\n".join(nsfw_tags))
    return await request.ctx.response.send(embed=embed)


@anekos.sub_command(name="랜덤", description="랜덤으로 가져옵니다.")
async def neko(request: HiyobotRequest):
    tag = choice(sfw_tags if not await is_nsfw(request) else nsfw_tags)
    img_url = (await request.app.ctx.request.get(URL + f"/{tag}"))["url"]
    return await request.ctx.response.send(embed=main_embed.set_image(url=img_url))


@anekos.sub_command(
    name="검색",
    description="태그를 이용해 사진을 가져옵니다.",
    options=[
        CommandArgument(
            name="태그",
            description="검색할 태그입니다. ",
            type=3,
            required=True,
        )
    ],
)
async def neko_search(request: HiyobotRequest, tag: str):
    if tag not in sfw_tags and tag not in nsfw_tags:
        return await request.ctx.response.send(
            "해당 태그는 없어요! 태그는 ``/네코 도움말``을 통해 확인하실 수 있어요."
        )
    if tag in nsfw_tags:
        if not await is_nsfw(request):
            return await request.ctx.response.send(
                "해당 태그는 성인 태그인 것 같습니다. 연령 제한이 설정된 채널에서 사용해주세요."
            )
    img_url = (await request.app.ctx.request.get(URL + f"/{tag}"))["url"]
    return await request.ctx.response.send(embed=main_embed.set_image(url=img_url))
