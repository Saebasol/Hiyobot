"""
Hiyobot의 기본 베이스가 되는 클라이언트입니다.
"""
from typing import Any

from discord.client import Client
from discord.object import Object
from discord.app_commands.tree import CommandTree
from mintchoco.client import Mintchoco
from hiyobot.config import HiyobotConfig
from hiyobot.request import Request
from discord.flags import Intents


class Hiyobot(Client):
    mintchoco: Mintchoco
    request: Request

    def __init__(
        self, config: HiyobotConfig, intents: Intents, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(intents=intents, *args, **kwargs)
        self.tree = CommandTree(self)
        self.config = config
        Hiyobot.mintchoco = Mintchoco()
        Hiyobot.request = Request()

    async def setup_hook(self):
        if self.config.PRODUCTION:
            await self.tree.sync()
        else:
            await self.tree.sync(guild=Object(self.config.TEST_GUILD_ID))

    def run(self, *args: Any, **kwargs: Any) -> None:
        """
        Hiyobot을 실행합니다.

        토큰은 Config에서 로드하기 때문에 인자로 줄 필요가 없습니다.
        """
        kwargs.update({"token": self.config.TOKEN})
        return super().run(*args, **kwargs)
