from typing import Optional
from getpass import getpass

from ohmyxdu.globals import get_config, get_current_omx
from ohmyxdu.security import encode_password


def credentials(item: str, auth_name: Optional[str] = None):
    """
    修改各项验证账号或密码

    :param item: 修改项，如 username 或 password。
    :param auth_name: 验证名，例如 IDS 即为统一身份验证（ehall等）所需的验证服务，默认为 IDS （即全局服务）
    """

    auth_config: dict = get_config().get('CREDENTIALS')

    if auth_name is None or auth_name.upper() == 'IDS':
        config_to_modify = auth_config
    else:
        config_to_modify = auth_config.get(auth_name.upper(), {})

    if item.upper() == 'PASSWORD':
        # 密码必须以安全的方式输入，如想从程序中调用，请通过 ohmyxdu.security.encode_password 直接保存
        username = config_to_modify.get('USERNAME', auth_config.get('USERNAME'))
        if not username:
            raise AttributeError('配置文件损坏')
        password = encode_password(getpass(f'新密码:<输入尽可能不会回显>'), username)
        config_to_modify['PASSWORD'] = password
    else:
        config_to_modify[item.upper()] = input(f'{item}:').strip()
        while not config_to_modify[item.upper()]:
            config_to_modify[item.upper()] = input(f'{item}:').strip()

    auth_config[auth_name.upper()] = config_to_modify

    get_current_omx().dump_config_file()
