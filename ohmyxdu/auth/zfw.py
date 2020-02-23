from loguru import logger
from parsel import Selector

from ohmyxdu.auth import Auth


class ZFWAuth(Auth):
    AUTH_NAME = 'ZFW'
    AUTH_URL = 'https://zfw.xidian.edu.cn'

    def __init__(self):
        super().__init__()

        # 绕过验证码
        self.headers['User-Agent'] = 'Mobile'

        resp = self.get(self.AUTH_URL)

        html = Selector(resp.text)
        hidden_tags = html.css('input[type=hidden]')

        data = {'LoginForm[username]': self.username, 'LoginForm[password]': self.password}
        data.update({tag.attrib['name']: tag.attrib['value'] for tag in hidden_tags})

        logger.debug(data)

        data['LoginForm[password]'] = str(data['LoginForm[password]'])

        self.post(self.AUTH_URL, data=data)

        del self.headers['User-Agent']
