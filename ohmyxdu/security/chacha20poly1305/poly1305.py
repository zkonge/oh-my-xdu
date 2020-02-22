from .cryptomath import div_ceil

__all__ = ('Poly1305',)


class Poly1305:
    """Poly1305 authenticator"""

    P = 0x3FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFB  # 2^130-5

    @staticmethod
    def le_bytes_to_num(data: bytes) -> int:
        """Convert a number from little endian byte format"""

        return int.from_bytes(data, 'little')

    @classmethod
    def num_to_16_le_bytes(cls, num: int) -> bytes:
        """Convert number to 16 bytes in little endian format"""

        return (num & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF).to_bytes(16, 'little')

    def __init__(self, key: bytes):
        """Set the authenticator key"""

        if len(key) != 32:
            raise ValueError('Key must be 32 bytes long')

        self.acc = 0
        self.r = self.le_bytes_to_num(key[0:16])
        self.r &= 0x0FFFFFFC0FFFFFFC0FFFFFFC0FFFFFFF
        self.s = self.le_bytes_to_num(key[16:32])

    def create_tag(self, data: bytes) -> bytes:
        """Calculate authentication tag for data"""

        for i in range(div_ceil(len(data), 16)):
            self.acc += self.le_bytes_to_num(data[i * 16:(i + 1) * 16] + b'\x01')
            self.acc = (self.r * self.acc) % self.P

        self.acc += self.s
        return self.num_to_16_le_bytes(self.acc)
