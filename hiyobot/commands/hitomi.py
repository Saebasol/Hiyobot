from urllib.parse import quote

from delphinium.entities.info import Info
from discord import Interaction, app_commands
from discord.embeds import Embed
from discord.ui import Button

from hiyobot.client import Hiyobot
from hiyobot.paginator import Paginator


def make_embed_with_info(info: Info, thumbnail: str) -> Embed:
    tags_join = ", ".join(info.tags) if info.tags else "없음"
    embed = Embed(
        title=info.title,
    )
    embed.set_thumbnail(
        url=f"https://heliotrope.saebasol.org/api/proxy/{quote(thumbnail, safe='-_.!~*\'()')}"
    )
    embed.add_field(
        name="번호",
        value=f"[{info.id}](https://hibiscus.saebasol.org/viewer/{info.id})",
        inline=False,
    )
    embed.add_field(
        name="타입",
        value=info.type,
        inline=False,
    )
    embed.add_field(
        name="작가",
        value=", ".join(info.artists) if info.artists else "없음",
        inline=False,
    )
    embed.add_field(
        name="그룹",
        value=", ".join(info.groups) if info.groups else "없음",
        inline=False,
    )
    embed.add_field(
        name="원작",
        value=", ".join(info.series) if info.series else "없음",
        inline=False,
    )
    embed.add_field(
        name="캐릭터",
        value=", ".join(info.characters) if info.characters else "없음",
        inline=False,
    )
    embed.add_field(
        name="태그",
        value=tags_join if len(tags_join) <= 1024 else "표시하기에는 너무 길어요.",
        inline=False,
    )
    embed.set_footer(text="Powered by Saebasol/Heliotrope")
    return embed


hitomi = app_commands.Group(
    name="히토미", description="히토미 관련 명령어입니다.", nsfw=True
)


@hitomi.command(
    name="정보",
    description="번호로 정보를 가져옵니다.",
)
@app_commands.describe(
    number="정보를 가져올 번호입니다.", ephemeral="나에게만 보일지 선택하는 여부입니다."
)
async def hitomi_info(
    interaction: Interaction[Hiyobot], number: int, ephemeral: bool = False
) -> None:
    info = await interaction.client.delphinium.info(number)
    if info:
        thumbnail = await interaction.client.delphinium.thumbnail(number, "smallbig")
        embed = make_embed_with_info(info, thumbnail[0].url)
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        return

    await interaction.response.send_message(
        "정보를 찾을수 없어요.", ephemeral=ephemeral
    )


@hitomi.command(
    name="리스트",
    description="최신 작품 목록을 가져옵니다.",
)
@app_commands.describe(
    number="가져올 페이지입니다.", ephemeral="나에게만 보일지 선택하는 여부입니다."
)
async def hitomi_list(
    interaction: Interaction[Hiyobot], number: int, ephemeral: bool = False
) -> None:
    await interaction.response.defer()
    infos, _ = await interaction.client.delphinium.list(number)

    embeds = [
        make_embed_with_info(
            info,
            (await interaction.client.delphinium.thumbnail(info.id, "smallbig"))[0].url,
        )
        for info in infos
    ]

    paginator = Paginator(interaction.user.id, embeds)

    paginator.add_item(Button(label="View On Saebasol/Hibiscus", url="https://hibiscus.saebasol.org"))

    return await interaction.followup.send(
        embed=embeds[0],
        view=paginator,
        ephemeral=ephemeral,
    )


@hitomi.command(
    name="뷰어",
    description="디스코드 내에서 작품을 감상합니다.",
)
@app_commands.describe(
    number="감상할 번호입니다.", ephemeral="나에게만 보일지 선택하는 여부입니다."
)
async def hitomi_viewer(
    interaction: Interaction[Hiyobot], number: int, ephemeral: bool = False
) -> None:
    await interaction.response.defer()

    images = await interaction.client.delphinium.image(number)

    if not images:
        return await interaction.followup.send(
            "정보를 찾을수 없어요.", ephemeral=ephemeral
        )

    page = 0
    total = len(images)
    embeds: list[Embed] = []

    for file in images:
        page += 1
        embed = Embed()
        embed.set_image(
            url=f"{interaction.client.delphinium.base_url}/api/proxy/{quote(file.url, safe='-_.!~*\'()')}"
        )
        embed.set_footer(text=f"{page}/{total}")
        embeds.append(embed)

    paginator = Paginator(interaction.user.id, embeds)

    paginator.add_item(Button(label="View On Saebasol/Hibiscus", url=f"https://hibiscus.saebasol.org/viewer/{number}"))

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
    query="검색할 제목 또는 태그입니다. 띄어쓰기로 구분합니다.",
    page="가져올 페이지입니다.",
    ephemeral="나에게만 보일지 선택하는 여부입니다.",
)
async def hitomi_search(
    interaction: Interaction[Hiyobot],
    query: str,
    page: int = 1,
    ephemeral: bool = False,
) -> None:
    await interaction.response.defer()
    querys = query.split(" ")
    results, _ = await interaction.client.delphinium.search(querys, page)
    if results:
        embeds = [
            make_embed_with_info(
                info,
                (await interaction.client.delphinium.thumbnail(info.id, "smallbig"))[
                    0
                ].url,
            )
            for info in results
        ]

        paginator = Paginator(interaction.user.id, embeds)

        return await interaction.followup.send(
            embed=embeds[0],
            view=paginator,
            ephemeral=ephemeral,
        )

    await interaction.followup.send("정보를 찾을수 없어요.", ephemeral=ephemeral)


@hitomi.command(
    name="랜덤",
    description="랜덤 작품을 가져옵니다.",
)
@app_commands.describe(
    query="검색할 제목 또는 태그입니다. 띄어쓰기로 구분합니다.",
    ephemeral="나에게만 보일지 선택하는 여부입니다.",
)
async def hitomi_random(
    interaction: Interaction[Hiyobot], query: str, ephemeral: bool = False
) -> None:
    await interaction.response.defer()
    info = await interaction.client.delphinium.random(query.split(" "))
    if info:
        thumbnail = await interaction.client.delphinium.thumbnail(info.id, "smallbig")
        embed = make_embed_with_info(info, thumbnail[0].url)
        await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        return

    await interaction.followup.send("정보를 찾을수 없어요.", ephemeral=ephemeral)
