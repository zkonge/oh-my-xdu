from typing import List, Callable, Any
from sys import path
from pathlib import Path
from importlib import import_module

from toml import loads
from defopt import run

import ohmyxdu
from ohmyxdu import logger


class Application:
    plugins: List[Callable[..., None]]
    base_path: Path

    def __init__(self, base_path: Path):
        ohmyxdu.app = self
        self.plugins = []
        self.base_path = base_path

        ohmyxdu.CONFIG = loads((base_path / 'config.toml').read_text())
        ohmyxdu.BASE_PATH = base_path

        # 内建插件处于ohmyxdu包中
        builtin_plugins_path = Path(__file__).parent / 'builtins'
        plugins_path = base_path / 'plugins'

        self.load_plugin_here(builtin_plugins_path)
        self.load_plugin_here(plugins_path)
        logger.debug(f'已加载插件{self.plugins}')

    def load_plugin_here(self, current_path: Path):
        # 让loader找到插件
        current_path_str = str(current_path)
        if current_path_str not in path:
            path.append(current_path_str)

        for plugin_path in current_path.glob('*.py'):
            plugin_name = plugin_path.stem
            module = import_module(f'{plugin_name}')
            try:
                self.plugins.append(getattr(module, plugin_name))
            except AttributeError:
                logger.warning(f'插件 {plugin_name} 没有公开入口')

    def run(self):
        run(logger.catch(plugin) for plugin in self.plugins)
