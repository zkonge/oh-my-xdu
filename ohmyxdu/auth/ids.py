from secrets import token_bytes

from loguru import logger
from parsel import Selector
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from ohmyxdu.auth import Auth

__all__ = ('IDSAuth',)


def encrypt(key: bytes, value: bytes):
    """
    登录时用于加密密码

    :param key:
    :param value:
    :return:
    """
    # 别学这个登录流程，正确方法可以去看一下非对称密码。
    # 如果需在不可信信道传递信息的话请优先考虑 TLS1.3+(HTTPS), Noise Protocol 等专业设施
    # 其实这里只要有一处随机即可，两次随机并不能有效增加安全性
    box = AES.new(key=key, mode=AES.MODE_CBC, iv=token_bytes(16))
    return box.encrypt(pad(token_bytes(64) + value, block_size=16))


class IDSAuth(Auth):
    """统一身份验证"""

    AUTH_NAME = 'IDS'
    AUTH_URL = 'http://ids.xidian.edu.cn/authserver/login'

    def __init__(self, service_url: str):
        """
        初始化验证会话

        :param service_url: 需要使用 IDS 验证的服务 URL（应该可以认为是跳转来源？）
        """

        super().__init__()

        # 获取登录必须的信息
        params = {'service': service_url}
        logger.debug(f'service_url:{service_url}')
        resp = self.get(self.AUTH_URL, params=params)

        html = Selector(resp.text)
        hidden_tags = html.css('input[type=hidden]')

        data = {'username': self.username, 'password': self.password}
        data.update({tag.attrib['name']: tag.attrib['value'] for tag in hidden_tags})

        logger.debug(data)

        key = html.css('input#pwdDefaultEncryptSalt').attrib['value']
        data['password'] = encrypt(str(data['password']).encode(), key.encode())

        self.post(self.AUTH_URL, params=params, data=data)
        self.get(service_url)
