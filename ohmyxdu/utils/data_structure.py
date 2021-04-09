__all__ = ("Secret",)


class Secret:
    """
    用于包装机密信息以减少在日志等处泄漏的可能性

    >>> Secret('ImportantPassword')
    Secret('******')
    >>> str(Secret('ImportantPassword'))
    'ImportantPassword'
    """

    def __init__(self, secret: str):
        self._secret = secret

    def __bool__(self) -> bool:
        return bool(self._secret)

    def __str__(self) -> str:
        return self._secret

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}('******')"
