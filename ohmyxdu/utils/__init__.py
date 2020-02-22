from time import time

__all__ = ('timestamp',)


def timestamp():
    return int(time() * 1000)
