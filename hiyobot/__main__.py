from hiyobot.commands.hitomi import hitomi
from hiyobot.commands.anekos import anekos
from hiyobot.commands.license import license
from hiyobot.handler.app import Hiyobot

bot = Hiyobot(
    "client_public_key",
    "bot_token",
)
bot.command_register(hitomi)
bot.command_register(anekos)
bot.command_register(license)

bot.sanic.run("0.0.0.0", 8000)
