from uuid import getnode
from hashlib import blake2s
from secrets import token_bytes
from base64 import b64encode, b64decode

from loguru import logger

from ohmyxdu.security.chacha20poly1305 import ChaCha20Poly1305, TagInvalidException


def pad(data: bytes) -> bytes:
    """
    数据定长填充

    :param data:
    :return:
    """

    # 真的有人会用32字节长的密码吗
    n = 32 - (len(data) % 32)
    return data + bytes([n]) * n


def unpad(data: bytes) -> bytes:
    """
    数据定长解除填充

    :param data:
    :return:
    """

    # 有AEAD就不去检查unpad操作是否合法了
    return data[:-data[-1]]


def kdf(base: bytes) -> bytes:
    """
    密钥派生 (Key Derivation Function)

    :param base: 任意长字节串
    :return: 长32的字节串
    """

    mac = getnode()
    if (mac >> 40) & 1:
        logger.warning('似乎无法获取计算机MAC地址，密码验证可能会失败')
    return blake2s(base, key=mac.to_bytes(32, 'big')).digest()


def encode_password(plain_password: str, username: str) -> str:
    """
    加密本地密码

    :param plain_password: 明文密码
    :param username: 用户名
    :return:
    """

    key = kdf(username.encode())
    plain_password = plain_password.encode()
    nonce = token_bytes(12)

    box = ChaCha20Poly1305(key)
    r = nonce + box.seal(nonce, pad(plain_password))

    return b64encode(r).decode()


def decode_password(cipher_password: str, username: str) -> str:
    """
    解密本地密码

    :param cipher_password: 明文密码
    :param username: 用户名
    :return:
    """

    key = kdf(username.encode())
    cipher_password = b64decode(cipher_password)
    nonce, cipher_password = cipher_password[:12], cipher_password[12:]

    box = ChaCha20Poly1305(key)

    try:
        return unpad(box.open(nonce, cipher_password)).decode()
    except TagInvalidException:
        logger.error('存储密码解密失败，需要重新输入密码')
        raise TagInvalidException
