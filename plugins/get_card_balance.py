from ohmyxdu.auth.wx import WXAuth


def get_card_balance():
    """获取当前账户对应的校园卡余额"""

    token = WXAuth()

    resp = token.post('http://202.117.121.7:8080/infoCampus/playCampus/getAllPurposeCard.do')

    wallet = resp.json()['allPurposeCardVO']['cardGeneralInfo'][0]['value']
    print(f'一卡通余额:￥{int(wallet) / 100:.2f}')
