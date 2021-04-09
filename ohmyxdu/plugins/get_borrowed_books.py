from typing import Optional, List
from itertools import count

from loguru import logger

from ohmyxdu.auth.wx import WXAuth

SERVICE_URL = "http://202.117.121.7:8080/oaCampus/library/getReturn.do"


def get_borrowed_books(*, limit: Optional[int] = None) -> List[dict]:
    """
    获取当前所有（或指定数量）的借书记录，按时间降序

    :param limit: 指定输出数量
    :return: 获取到的课本信息
    """

    token = WXAuth()

    if limit is None:
        limit = float("inf")

    books = []
    for offset in count(1):
        data = token.post(SERVICE_URL, data={"offset": offset}).json()
        logger.debug(data)
        if data["msgState"] != 1 or len(books) > limit:
            break
        books.extend(data["list"])
    books = books[: min(limit, len(books))]
    for book in books:
        logger.success(f'应还日期:{book["returnDate"]} 《{book["title"]}》')

    return books
