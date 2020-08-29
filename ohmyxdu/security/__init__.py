from uuid import getnode
from hashlib import blake2s
from secrets import token_bytes
from base64 import b64encode, b64decode

from loguru import logger
from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Util.Padding import pad, unpad


def kdf(base: bytes) -> bytes:
    """
    密钥派生 (Key Derivation Function)

    :param base: 任意长字节串
    :return: 长度为32的字节串
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

    box = ChaCha20_Poly1305.new(key=key, nonce=nonce)
    cipher = box.encrypt_and_digest(pad(plain_password, block_size=32))
    r = nonce + cipher[0] + cipher[1]

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
    nonce, cipher, mac = cipher_password[:12], cipher_password[12:-16], cipher_password[-16:]

    box = ChaCha20_Poly1305.new(key=key, nonce=nonce)

    try:
        return unpad(box.decrypt_and_verify(cipher_password, mac), block_size=32).decode()
    except ValueError:
        raise ValueError('存储密码解密失败，需要重新输入密码')
