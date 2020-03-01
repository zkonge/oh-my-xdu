from typing import List, Callable, Optional
from os import environ
from sys import path
from copy import deepcopy
from pathlib import Path
from importlib import import_module

from toml import dumps, loads
from defopt import run

from ohmyxdu.globals import get_config, set_config, set_current_omx

__all__ = ('__version__', 'OMX')
__version__ = '0.1.0'

debug = bool(environ.get('DEBUG'))
if not debug and not environ.get('LOGURU_LEVEL'):
    # 正式环境关掉 DEBUG 日志
    environ['LOGURU_LEVEL'] = 'INFO'

# 要为调整日志等级违反一下 PEP 8
# TODO:重写log handler
from loguru import logger


class OMX:
    """
    oh-my-xdu

    1.初始化
    可直接向构造函数传入包含账户信息的 dict，
    例如：
    >>> config = {
    ...     'CREDENTIALS': {
    ...         'USERNAME': 'student_id',
    ...         'PASSWORD': 'AeTs70Z/uOZ9DmigTGSm08SU1kWlAf6BBHZZIF/sJOCF13ECP7LDgO2jifYhyvwfg8A0Ym23bRVs/3OP',
    ...         'IDS': {
    ...             'USERNAME': 'student_id'
    ...         }
    ...     }
    ... }
    ...
    >>> omx = OMX(config)

    其中 PASSWORD 部分是由 ohmyxdu.security.encode_password 加密的密码

    也可从指定配置文件导入，在此我们使用一种名为 toml 的配置文件格式存储配置信息，配置文件样例位于根目录
    >>> omx = OMX.from_config_file(Path('~/omx.toml'))

    2.执行脚本
    OMX 对象初始完成后即可直接引入 ohmyxdu.plugins 下的插件。同时，你还可以从 omx.plugins 中获取当前所有可用的插件
    """

    plugins: List[Callable[..., None]]
    config_path = Optional[Path]

    def __init__(self, config: dict):
        self.plugins = []
        self.config_path = None

        set_config(config)
        set_current_omx(self)

        lib_path = Path(__file__).parent

        builtin_path = lib_path / 'builtins'
        plugins_path = lib_path / 'plugins'

        self.load_plugin_here(builtin_path)  # 内建插件不会有返回值，目前其对应的函数不应该直接被调用
        self.load_plugin_here(plugins_path)

        logger.debug(f'已加载插件{self.plugins}')

    @staticmethod
    def from_config_file(config_path: Path) -> 'OMX':
        """
        从指定配置文件初始化 OMX

        :param config_path: 配置文件路径
        :return:
        """

        try:
            config_text = loads(config_path.read_text())
        except FileNotFoundError:
            config_text = {}

        # 防止异步时修改配置文件造成不一致
        # OMX 这种东西随用随建就好了（
        # TODO: OMX 对象复用
        config_text = deepcopy(config_text)

        r = OMX(config_text)
        r.config_path = config_path
        return r

    def dump_config_file(self, config_path: Optional[Path] = None):
        """
        将当前上下文中的配置写回配置文件

        :param config_path: 配置文件路径，留空代表写回生成 OMX 对象时使用的配置文件
        """

        config_text = dumps(get_config())

        if config_path is not None:
            config_path.write_text(config_text)
            return
        elif self.config_path is not None:
            self.config_path.write_text(config_text)
            return

        raise NotImplementedError

    def load_plugin_here(self, current_path: Path):
        """
        加载指定目录下的可用插件

        :param current_path: 目标目录
        """

        # 让 module loader 找到插件
        current_path_str = str(current_path)
        if current_path_str not in path:
            path.append(current_path_str)

        for plugin_path in current_path.glob('*.py'):  # TODO: 增加模块插件（文件夹）的支持
            plugin_name = plugin_path.stem
            module = import_module(f'{plugin_name}')
            try:
                self.plugins.append(getattr(module, plugin_name))
            except AttributeError:
                logger.warning(f'插件 {plugin_name} 没有公开入口')

    def bootstrap(self):
        """交互式初始化 OMX，写入通用配置信息"""

        from getpass import getpass
        from ohmyxdu.security import encode_password

        print(f'oh-my-xdu {__version__} 启动配置:\n'
              f'接下来我们要做的是:\n'
              f'\t[1]:配置通用账号密码')

        # 配置通用密码
        username = input('学工号:').strip()
        while not username:
            username = input('学工号:').strip()
        password = encode_password(getpass('统一身份验证密码:<输入尽可能不会回显>'), username)

        basic_config = {'CREDENTIALS': {
            'USERNAME': username,
            'PASSWORD': password
        }}

        config = get_config()
        config.update(basic_config)
        self.dump_config_file()

    def run(self):
        run(logger.catch(plugin) for plugin in self.plugins)
