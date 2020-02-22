from typing import List, Tuple
from struct import pack, unpack

__all__ = ('ChaCha',)


class ChaCha:
    """Pure python implementation of ChaCha cipher"""

    constants: Tuple[int] = (0x61707865, 0x3320646e, 0x79622d32, 0x6b206574)

    @staticmethod
    def rotl32(v: int, c: int) -> int:
        """Rotate left a 32 bit integer v by c bits"""

        return ((v << c) & 0xffffffff) | (v >> (32 - c))

    @staticmethod
    def quarter_round(x: List[int], a: int, b: int, c: int, d: int):
        """Perform a ChaCha quarter round"""

        xa = x[a]
        xb = x[b]
        xc = x[c]
        xd = x[d]

        xa = (xa + xb) & 0xffffffff
        xd = xd ^ xa
        xd = ((xd << 16) & 0xffffffff | (xd >> 16))

        xc = (xc + xd) & 0xffffffff
        xb = xb ^ xc
        xb = ((xb << 12) & 0xffffffff | (xb >> 20))

        xa = (xa + xb) & 0xffffffff
        xd = xd ^ xa
        xd = ((xd << 8) & 0xffffffff | (xd >> 24))

        xc = (xc + xd) & 0xffffffff
        xb = xb ^ xc
        xb = ((xb << 7) & 0xffffffff | (xb >> 25))

        x[a] = xa
        x[b] = xb
        x[c] = xc
        x[d] = xd

    _round_mixup_box: Tuple[Tuple[int]] = ((0x0, 0x4, 0x8, 0xC),
                                           (0x1, 0x5, 0x9, 0xD),
                                           (0x2, 0x6, 0xA, 0xE),
                                           (0x3, 0x7, 0xB, 0xF),
                                           (0x0, 0x5, 0xA, 0xF),
                                           (0x1, 0x6, 0xB, 0xC),
                                           (0x2, 0x7, 0x8, 0xD),
                                           (0x3, 0x4, 0x9, 0xE))

    @classmethod
    def double_round(cls, x: List[int]):
        """Perform two rounds of ChaCha cipher"""

        for a, b, c, d in cls._round_mixup_box:
            cls.quarter_round(x, a, b, c, d)

    @classmethod
    def chacha_block(cls, key: Tuple[int], counter: int, nonce: Tuple[int], rounds: int) -> Tuple[int]:
        """Generate a state of a single block"""

        state: Tuple[int, ...] = *cls.constants, *key, counter, *nonce

        working_state: List[int] = list(state)

        for _ in range(rounds // 2):
            cls.double_round(working_state)

        return tuple(
            (x + y) & 0xffffffff
            for x, y
            in zip(state, working_state)
        )

    @staticmethod
    def word_to_bytes(state: Tuple[int]) -> bytes:
        """Convert state to little endian bytestream"""

        return pack(f'<{len(state)}L', *state)

    @staticmethod
    def bytes_to_words(data: bytes) -> Tuple[int]:
        """Convert a bytes to array of word sized ints"""

        return unpack(f'<{len(data) // 4}L', data)

    def __init__(self, key: bytes, nonce: bytes, counter: int = 0, rounds: int = 20):
        """Set the initial state for the ChaCha cipher"""

        if len(key) != 32:
            raise ValueError('Key must be 32 bytes long')
        if len(nonce) != 12:
            raise ValueError('Nonce must be 12 bytes long')

        # convert bytes key and nonce to little endian 32 bit unsigned ints
        self.key = self.bytes_to_words(key)
        self.nonce = self.bytes_to_words(nonce)
        self.counter = counter
        self.rounds = rounds

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt the data"""

        encrypted_message = []

        for i, block in enumerate(plaintext[i:i + 64]
                                  for i
                                  in range(0, len(plaintext), 64)):
            key_stream = self.chacha_block(key=self.key,
                                           counter=self.counter + i,
                                           nonce=self.nonce,
                                           rounds=self.rounds)
            key_stream = self.word_to_bytes(key_stream)

            encrypted_message += [x ^ y for x, y in zip(key_stream, block)]

        return bytes(encrypted_message)

    def decrypt(self, ciphertext):
        """Decrypt the data"""

        return self.encrypt(ciphertext)
