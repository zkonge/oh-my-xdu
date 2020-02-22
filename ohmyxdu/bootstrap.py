from pathlib import Path
from getpass import getpass

from toml import dumps

from ohmyxdu import __version__
from ohmyxdu.security import encode_password


def bootstrap(base_path: Path):
    print(f'''oh-my-xdu {__version__} 启动配置:
接下来我们要做的是:
    [1]:配置通用账号密码
    [2]:更新插件''')

    # 配置通用密码
    username = input('学工号:').strip()
    while not username:
        username = input('学工号:').strip()
    password = encode_password(getpass('统一身份验证密码:<输入尽可能不会回显>'), username)

    basic_config = {'CREDENTIALS': {
        'USERNAME': username,
        'PASSWORD': password
    }}

    (base_path / 'config.toml').write_text(dumps(basic_config))

    # 更新插件
    ...
