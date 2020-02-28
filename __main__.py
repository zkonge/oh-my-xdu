from os import environ
from pathlib import Path

debug = bool(environ.get('DEBUG'))
if not debug and not environ.get('LOGURU_LEVEL'):
    # 正式环境关掉 DEBUG 日志
    environ['LOGURU_LEVEL'] = 'INFO'

# 要为调整日志等级违反一下 PEP 8
# TODO:重写log handler
from ohmyxdu import OMX
from loguru import logger

# 测试环境中就直接在当前目录读配置
omx_path = Path() if debug else Path.home() / '.omx'
config_path = omx_path / 'config.toml'

logger.add(omx_path / 'omx.log', rotation='5MB')

app = OMX.from_config_file(config_path)

if not omx_path.is_dir() or not config_path.exists():
    app.bootstrap()

app.run()
