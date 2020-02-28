from loguru import logger
from parsel import Selector

from ohmyxdu.auth import Auth


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

        data['password'] = str(data['password'])

        self.post(self.AUTH_URL, params=params, data=data)
        self.get(service_url)
