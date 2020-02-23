from typing import List, NamedTuple

from loguru import logger
from parsel import Selector

from ohmyxdu.auth.zfw import ZFWAuth


class Package(NamedTuple):
    package_name: str
    used_flow: str
    left_flow: str
    paid_left_flow: str
    settling_day: str
    expires_day: str


def get_network_usage() -> List[Package]:
    """获取校园网流量使用情况"""

    token = ZFWAuth()

    resp = token.get('https://zfw.xidian.edu.cn/home')

    html = Selector(resp.text)
    package_tags = html.css('#w3-container>table>tbody>tr')

    packages = []
    for package_tag in package_tags:
        packages.append(Package(*[tag.get() for tag in package_tag.css('td::text')]))

    for package in packages:
        logger.opt(colors=True).success('套餐名称:<blue>{}</blue> '
                                        '已用流量:<blue>{}</blue> '
                                        '剩余流量:<blue>{}</blue> '
                                        '充值剩余流量:<blue>{}</blue> '
                                        '结算日期:<blue>{}</blue> '
                                        '套餐到期时间:<blue>{}</blue> ', *package)
    return packages
