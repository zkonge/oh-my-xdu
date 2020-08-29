from os import environ
from pathlib import Path

from loguru import logger

from ohmyxdu import OMX

debug = bool(environ.get('DEBUG'))


def main():
    # 测试环境中就直接在当前目录读配置
    omx_path = Path() if debug else Path.home() / '.omx'
    config_path = omx_path / 'config.toml'

    logger.add(omx_path / 'omx.log', rotation='5MB')

    app = OMX.from_config_file(config_path)

    if not omx_path.is_dir() or not config_path.exists():
        app.bootstrap()

    app.run()


if __name__ == '__main__':
    main()
