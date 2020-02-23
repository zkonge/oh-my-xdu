from typing import Dict, NamedTuple
from base64 import b64decode
from hashlib import sha1

from loguru import logger
from requests import get

from ohmyxdu import app

BASE_URL = 'https://api.github.com/repos/zkonge/oh-my-xdu'


class OnlinePluginInvalidException(Exception):
    pass


class PluginInfo(NamedTuple):
    plugin_name: str
    plugin_sha1: str
    plugin_blob_url: str


def get_online_plugin_info() -> Dict[str, PluginInfo]:
    """获取最新 commit 信息"""

    resp = get(BASE_URL + '/commits/master')
    logger.debug(resp)
    if resp.status_code != 200:
        raise OnlinePluginInvalidException('获取 commit 信息时出现问题')

    resp = get(resp.json()['commit']['tree']['url'])
    logger.debug(resp)
    if resp.status_code != 200:
        raise OnlinePluginInvalidException('获取文件列表时出现问题')

    plugins_url = [
        tree_data['url']
        for tree_data in resp.json()['tree']
        if tree_data['path'] == 'plugins'
    ][0]
    resp = get(plugins_url)
    logger.debug(resp)
    if resp.status_code != 200:
        raise OnlinePluginInvalidException('获取插件列表时出现问题')

    plugins = [
        plugin
        for plugin
        in resp.json()['tree']
        if plugin['type'] == 'blob'
    ]  # TODO:增加模块插件（文件夹）的支持

    ret = dict()
    for plugin in plugins:
        plugin_name = plugin['path'][:-3] if plugin['path'].endswith('.py') else plugin['path']
        ret[plugin_name] = PluginInfo(plugin_name=plugin_name,
                                      plugin_sha1=plugin['sha'],
                                      plugin_blob_url=plugin['url'])

    return ret


def get_online_plugin_content(online_plugin: PluginInfo) -> bytes:
    """获取指定 SHA1 对应文件内容"""

    content_resp = get(online_plugin.plugin_blob_url)
    logger.debug(content_resp)
    if content_resp.status_code != 200:
        raise OnlinePluginInvalidException('下载插件内容时出现问题')

    return b64decode(content_resp.json()['content'])


def update():
    """插件更新"""

    online_plugins = get_online_plugin_info()
    logger.debug(f'在线插件:{online_plugins}')

    local_plugins = dict()

    plugins_path = app.base_path / 'plugins'
    plugins_path.mkdir(parents=True, exist_ok=True)

    for plugin_path in plugins_path.glob('*.py'):
        plugin_name = plugin_path.stem
        plugin_sha1 = sha1(plugin_path.read_bytes()).hexdigest()

        local_plugins[plugin_name] = PluginInfo(plugin_name=plugin_name,
                                                plugin_sha1=plugin_sha1,
                                                plugin_blob_url='')
    logger.debug(f'本地插件:{local_plugins}')

    for key in online_plugins:
        if key in local_plugins and online_plugins[key].plugin_sha1 == local_plugins[key].plugin_sha1:
            continue
        logger.info(f'更新{online_plugins[key].plugin_name}...')

        content = get_online_plugin_content(online_plugins[key])
        (plugins_path / f'{online_plugins[key].plugin_name}.py').write_bytes(content)
