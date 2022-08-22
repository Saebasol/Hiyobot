from discord.embeds import Embed
from discord import Interaction, app_commands

from hiyobot.client import Hiyobot
from mintchoco.model.info import Info
from hiyobot.paginator import Paginator


def make_embed_with_info(info: Info):
    tags_join = ", ".join(info.tags) if info.tags else "없음"
    embed = Embed(
        title=info.title,
    )
    embed.set_thumbnail(url=f"https://api.saebasol.org/api/proxy/{info.thumbnail}")
    embed.add_field(
        name="번호",
        value=f"[{info.id}](https://hitomi.la/reader/{info.id}.html)",
        inline=False,
    )
    embed.add_field(
        name="타입",
        value=info.type,
        inline=False,
    )
    embed.add_field(
        name="작가", value=",".join(info.artist) if info.artist else "없음", inline=False
    )
    embed.add_field(
        name="그룹", value=",".join(info.group) if info.group else "없음", inline=False
    )
    embed.add_field(
        name="원작", value=",".join(info.series) if info.series else "없음", inline=False
    )
    embed.add_field(
        name="캐릭터",
        value=",".join(info.character) if info.character else "없음",
        inline=False,
    )
    embed.add_field(
        name="태그",
        value=tags_join if len(tags_join) <= 1024 else "표시하기에는 너무 길어요.",
        inline=False,
    )
    return embed


hitomi = app_commands.Group(name="히토미", description="히토미 관련 명령어입니다.", nsfw=True)


@hitomi.command(
    name="정보",
    description="번호로 정보를 가져옵니다.",
)
@app_commands.describe(number="정보를 가져올 번호입니다.", ephemeral="나에게만 보일지 선택하는 여부입니다.")
async def hitomi_info(
    interaction: Interaction, number: int, ephemeral: bool = False
) -> None:
    info = await Hiyobot.mintchoco.info(number)
    if info:
        embed = make_embed_with_info(info)
        return await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    return await interaction.response.send_message("정보를 찾을수 없어요.", ephemeral=ephemeral)


@hitomi.command(
    name="리스트",
    description="최신 작품 목록을 가져옵니다.",
)
@app_commands.describe(number="가져올 페이지입니다.", ephemeral="나에게만 보일지 선택하는 여부입니다.")
async def hitomi_list(
    interaction: Interaction, number: int, ephemeral: bool = False
) -> None:
    await interaction.response.defer()
    infos = await Hiyobot.mintchoco.list(number)
    assert infos

    embeds = [make_embed_with_info(info) for info in infos.list]

    paginator = Paginator(interaction.user.id, embeds)

    return await interaction.followup.send(
        embed=embeds[0],
        view=paginator,
        ephemeral=ephemeral,
    )


@hitomi.command(
    name="뷰어",
    description="디스코드 내에서 작품을 감상합니다.",
)
@app_commands.describe(number="감상할 번호입니다.", ephemeral="나에게만 보일지 선택하는 여부입니다.")
async def hitomi_viewer(
    interaction: Interaction, number: int, ephemeral: bool = False
) -> None:
    await interaction.response.defer()

    images = await Hiyobot.mintchoco.image(number)

    if not images:
        return await interaction.followup.send("정보를 찾을수 없어요.", ephemeral=ephemeral)

    page = 0
    total = len(images.files)
    embeds: list[Embed] = []

    for file in images.files:
        page += 1
        embed = Embed()
        embed.set_image(url=f"{Hiyobot.mintchoco.BASE_URL}/proxy/{file.url}")
        embed.set_footer(text=f"{page}/{total}")
        embeds.append(embed)

    paginator = Paginator(interaction.user.id, embeds)

    return await interaction.followup.send(
        embed=embeds[0],
        view=paginator,
        ephemeral=ephemeral,
    )


@hitomi.command(
    name="검색",
    description="작품을 찾습니다.",
)
@app_commands.describe(
    query="검색할 제목 또는 태그입니다.",
    page="가져올 페이지입니다.",
    ephemeral="나에게만 보일지 선택하는 여부입니다.",
)
async def hitomi_search(
    interaction: Interaction, query: str, page: int = 1, ephemeral: bool = False
) -> None:
    await interaction.response.defer()
    querys = query.split(" ")
    search = await Hiyobot.mintchoco.search(querys, page)
    if search:
        if search.result:
            embeds = [make_embed_with_info(info) for info in search.result]

            paginator = Paginator(interaction.user.id, embeds)

            return await interaction.followup.send(
                embed=embeds[0],
                view=paginator,
                ephemeral=ephemeral,
            )

    await interaction.followup.send("정보를 찾을수 없어요.", ephemeral=ephemeral)
