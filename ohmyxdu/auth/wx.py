from typing import Any, Dict, Optional
from json import dumps
from hashlib import md5

from ohmyxdu import logger
from ohmyxdu.auth import Auth
from ohmyxdu.utils import timestamp


class WXAuth(Auth):
    AUTH_NAME = 'WX'
    AUTH_URL = 'http://202.117.121.7:8080'

    def __init__(self):
        super().__init__()

        data = {'userName': self.username, 'password': self.password, 'schoolId': 190}
        data['password'] = str(data['password'])
        resp = self.post(self.AUTH_URL + '/baseCampus/login/login.do', data=data)

        data = resp.json()
        if data['isConfirm'] != 1:
            raise PermissionError('登录失败')

        self.headers['token'] = '_'.join(data['token'])
        logger.debug('token:{}', data['token'])

    @staticmethod
    def sign_data(data: Dict):
        s = '&'.join(f'{key}={value}' for key, value in data.items())
        return md5(s.encode()).hexdigest()

    def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs):
        if data is None:
            data = {}
        json = {'appKey': 'GiITvn', 'param': dumps(data), 'secure': 0, 'time': timestamp()}
        json['sign'] = self.sign_data(json)
        return super().post(url, json=json, **kwargs)
