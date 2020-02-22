from secrets import compare_digest
from struct import pack

from .chacha import ChaCha
from .poly1305 import Poly1305

__all__ = ('ChaCha20Poly1305', 'TagInvalidException')


class TagInvalidException(Exception):
    pass


class ChaCha20Poly1305:
    """Pure python implementation of ChaCha20/Poly1305 AEAD cipher"""

    key_length: int = 32
    nonce_length: int = 12
    tag_length: int = 16

    def __init__(self, key: bytes):
        """Set the initial state for the ChaCha20 AEAD"""

        if len(key) != 32:
            raise ValueError('Key must be 32 bytes long')
        self.key = key

    @staticmethod
    def poly1305_key_gen(key: bytes, nonce: bytes) -> bytes:
        """Generate the key for the Poly1305 authenticator"""

        poly = ChaCha(key, nonce)
        return poly.encrypt(bytes(32))

    @staticmethod
    def pad16(data: bytes) -> bytes:
        """Return padding for the Associated Authenticated Data"""

        if len(data) % 16 == 0:
            return bytes(0)
        else:
            return bytes(16 - (len(data) % 16))

    def seal(self, nonce: bytes, plaintext: bytes, data: bytes = b'') -> bytes:
        """
        Encrypts and authenticates plaintext using nonce and data. Returns the
        ciphertext, consisting of the encrypted plaintext and tag concatenated.
        """

        if len(nonce) != 12:
            raise ValueError('Nonce must be 12 bytes large')

        otk = self.poly1305_key_gen(key=self.key, nonce=nonce)

        ciphertext = ChaCha(key=self.key, nonce=nonce, counter=1).encrypt(plaintext)

        mac_data = b''.join((
            data, self.pad16(data),
            ciphertext, self.pad16(ciphertext),
            pack('<Q', len(data)),
            pack('<Q', len(ciphertext))
        ))

        tag = Poly1305(otk).create_tag(mac_data)

        return ciphertext + tag

    def open(self, nonce: bytes, ciphertext: bytes, data: bytes = b'') -> bytes:
        """
        Decrypts and authenticates ciphertext using nonce and data. If the
        tag is valid, the plaintext is returned. If the tag is invalid,
        returns None.
        """

        if len(nonce) != 12:
            raise ValueError('Nonce must be 12 bytes long')

        if len(ciphertext) < 16:
            raise TagInvalidException

        expected_tag = ciphertext[-16:]
        ciphertext = ciphertext[:-16]

        otk = self.poly1305_key_gen(self.key, nonce)

        mac_data = b''.join((
            data, self.pad16(data),
            ciphertext, self.pad16(ciphertext),
            pack('<Q', len(data)),
            pack('<Q', len(ciphertext))
        ))

        tag = Poly1305(otk).create_tag(mac_data)

        if not compare_digest(tag, expected_tag):
            raise TagInvalidException

        return ChaCha(self.key, nonce, counter=1).decrypt(ciphertext)
