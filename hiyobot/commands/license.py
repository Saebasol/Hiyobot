from discord.embeds import Embed
from discord import Interaction, app_commands

embed = Embed(
    title="OSS Notice",
    description="This project uses OSS (open source software) under the following licenses.",
)
embed.add_field(
    name="discord.py",
    value="https://github.com/Rapptz/discord.py\nCopyright (c) 2015-present Rapptz\n[MIT License](https://github.com/Rapptz/discord.py/blob/master/LICENSE)",
)
embed.add_field(
    name="Mintchoco",
    value="https://github.com/Saebasol/Mintchoco\nCopyright (c) 2021 Saebasol\n[MIT License](https://github.com/Saebasol/Mintchoco/blob/main/LICENSE)",
    inline=False,
)


@app_commands.command()
async def license(interaction: Interaction) -> None:
    """
    Licenses for OSS used in Hiyobot
    """
    return await interaction.response.send_message(embed=embed)
