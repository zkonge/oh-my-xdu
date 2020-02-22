from typing import Optional, NamedTuple
from json import dumps
from collections import defaultdict

from ohmyxdu import logger
from ohmyxdu.auth.ids import IDSAuth

BASE_URL = 'http://ehall.xidian.edu.cn'
SERVICE_URL = BASE_URL + '/appShow?appId=4768574631264620'
GRADE_URL = BASE_URL + '/jwapp/sys/cjcx/modules/cjcx/xscjcx.do'


class Grade(NamedTuple):
    course_name: str
    score: float
    grade_point: Optional[float]


def get_grade(*, year_semester: Optional[str] = None):
    """
    获取指定学年成绩，默认获取所有

    :param year_semester: 例如："2019-2020-1" 为2019学年第一学期
    """
    token = IDSAuth(SERVICE_URL)
    query = []

    if year_semester:
        # TODO: query builder
        query.append({'name': 'XNXQDM', 'value': year_semester, 'linkOpt': 'and', 'builder': 'm_value_equal'})

    data = {
        'querySetting': dumps(query),
        '*order': 'KCH,KXH',  # 按课程名，课程号排序
        'pageSize': 1000,  # 有多少整多少.jpg
        'pageNumber': 1
    }

    resp = token.post(GRADE_URL, data=data)

    courses = resp.json()['datas']['xscjcx']['rows']

    grades = defaultdict(lambda: [])

    for course in courses:
        logger.debug(course)
        grades[course['XNXQDM_DISPLAY']].append(Grade(course['XSKCM'], course['ZCJ'], course['XFJD']))

    for year_semester in grades.keys():
        print(f'{year_semester}:')
        for grade in grades[year_semester]:
            if grade.grade_point is not None:
                print(f'\t{grade.course_name}:{grade.score}({grade.grade_point})')
            else:
                print(f'\t{grade.course_name}:{grade.score}')
