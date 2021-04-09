from loguru import logger
from ohmyxdu.auth.wx import WXAuth


def get_card_balance() -> int:
    """
    获取当前账户对应的校园卡余额

    :return: 校园卡余额，以分为单位
    """

    token = WXAuth()

    resp = token.post("http://202.117.121.7:8080/infoCampus/playCampus/getAllPurposeCard.do")

    wallet = resp.json()["allPurposeCardVO"]["cardGeneralInfo"][0]["value"]
    logger.success(f"一卡通余额:￥{int(wallet) / 100:.2f}")

    return int(wallet)
