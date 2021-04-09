from typing import Any, Dict, Optional

from loguru import logger
from requests import Session

from ohmyxdu.globals import get_config
from ohmyxdu.security import decode_password
from ohmyxdu.utils.data_structure import Secret

__all__ = ("Auth",)


# TODO:独立验证模块
class Auth(Session):
    """抽象验证模型"""

    AUTH_NAME: Optional[str] = None  # 所有派生类都应提供该参数，大写
    credentials: Dict[str, Any]

    def __init__(self):
        super().__init__()

        # 全局认证信息
        self.credentials = get_config()["CREDENTIALS"]

        # 来自 AUTH_NAME 的特定性验证信息
        self.specificity_credentials = self.credentials.get(self.AUTH_NAME, {})

    @property
    def username(self) -> str:
        username = self.specificity_credentials.get("USERNAME")
        if not username:
            username = self.credentials["USERNAME"]
            logger.debug("未能找到 {} 对应的账号，使用通用账号。", self.AUTH_NAME)
        return username

    @property
    def password(self) -> Secret:
        # 注意：所有敏感信息（如密码）都应被转为 Secret 对象
        password = Secret(self.specificity_credentials.get("PASSWORD", ""))
        if not password:
            password = Secret(self.credentials["PASSWORD"])
            logger.debug("未能找到 {} 对应的密码，使用通用密码。", self.AUTH_NAME)
        return Secret(decode_password(str(password), self.username))
