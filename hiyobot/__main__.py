"""
최종 진입점 입니다.
"""

from sys import argv

from hiyobot import create_client
from hiyobot.argparser import parse_args
from hiyobot.config import HiyobotConfig


def main() -> None:
    hiyobot_config = HiyobotConfig()
    args = parse_args(argv[1:])
    hiyobot_config.update_with_args(args)
    client = create_client(hiyobot_config)
    client.run()


if __name__ == "__main__":
    main()
