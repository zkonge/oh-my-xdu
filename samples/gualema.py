from os import environ

# 关掉 loguru 的 debug 日志
environ['LOGURU_LEVEL'] = 'WARNING'

from ohmyxdu import OMX
from ohmyxdu.security import encode_password
from ohmyxdu.plugins.get_grade import get_grade


def main():
    """今天我挂课了🐴"""

    # omx 对每个用户都需要做单独的初始化工作，之后才能使用引入的插件
    # omx 需要读入加密的密码，所有这里需要把明文密码加密输入
    # 同时强烈建议不要明文存储用户密码，如果在服务器上使用，请再套一层加密，更多工具请参考 ohmyxdu/security 目录
    _ = OMX({'CREDENTIALS': {
        'USERNAME': 'username',  # 学工号
        'PASSWORD': encode_password('password', 'username')  # 密码
    }})

    # 提取第一项结果
    grades_in_this_year = next(iter(get_grade(year_semester='2019-2020-1').values()))

    # 提取挂了的科目
    gua = [g for g in grades_in_this_year if g.score < 60]

    for v in gua:
        print(f'挂了 {v.course_name} 分数是{v.score}')

    # 我下学期一定好好学习


if __name__ == '__main__':
    main()
