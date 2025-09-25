"""
Hiyobot

Author: Saebasol
"""

from discord import Object, Intents

from hiyobot.client import Hiyobot
from hiyobot.commands import commands
from hiyobot.config import HiyobotConfig


def create_client(config: HiyobotConfig) -> Hiyobot:
    """
    명령어를 추가하고, Config값을 사용해서 Hiyobot 클라이언트를 반환합니다.
    """
    hiyobot = Hiyobot(config, intents=Intents.default())
    for command in commands:
        if config.PRODUCTION:
            hiyobot.tree.add_command(command)
        else:
            hiyobot.tree.add_command(command, guild=Object(config.TEST_GUILD_ID))
    return hiyobot
