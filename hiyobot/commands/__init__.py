"""
Hiyobot의 커맨드들이 모여있는곳입니다.

이곳 폴더 아래에 모든 커맨드가 작성되어야합니다.
"""

from typing import Any

from discord.app_commands import Command, Group

# 와일드카드 임포트
from hiyobot.commands.hitomi import hitomi as hitomi
from hiyobot.commands.license import license as license

# 임포트한것중에 필요한것만 필터링
commands: list[Command[Any, Any, Any] | Group] = [
    val
    for val in locals().values()
    if isinstance(val, Command) or isinstance(val, Group)
]
