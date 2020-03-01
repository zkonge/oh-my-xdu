from typing import Optional, NamedTuple
from pathlib import Path
from datetime import datetime, timedelta

from loguru import logger

from ohmyxdu.auth.ids import IDSAuth
from ohmyxdu.utils.icalendar_helper import ClassSchedule

BASE_URL = 'http://ehall.xidian.edu.cn'
SERVICE_URL = BASE_URL + '/appShow?appId=4770397878132218'
YEAR_SEMESTER_URL = BASE_URL + '/jwapp/sys/wdkb/modules/jshkcb/dqxnxq.do'
YEAR_SEMESTER_INFO_URL = BASE_URL + '/jwapp/sys/wdkb/modules/jshkcb/cxjcs.do'
CLASS_SCHEDULE_URL = BASE_URL + '/jwapp/sys/wdkb/modules/xskcb/xskcb.do'

# 上课时间 [(begin, end), ...]
MORNING_TIME = [
    ('8:30', '10:05'),
    ('10:25', '12:00')
]
SUMMER_TIME = MORNING_TIME + [
    ('14:30', '16:05'),
    ('16:25', '18:00'),
    ('19:30', '21:05')
]
WINTER_TIME = MORNING_TIME + [
    ('14:00', '15:35'),
    ('15:55', '17:30'),
    ('19:00', '20:35')
]


class YearSemester(NamedTuple):
    school_year: int
    semester: int


def get_semester_code(year_semester: YearSemester) -> str:
    """
    学年学期代号转换

    :param year_semester: 学年学期对象
    :return: 形如 '2019-2020-1' 的学年学期代号
    >>> get_semester_code(YearSemester(2019,1))
    '2019-2020-1'
    """

    return f'{year_semester.school_year}-{year_semester.school_year + 1}-{year_semester.semester}'


def get_latest_year_semester(token: IDSAuth) -> YearSemester:
    """
    获取当前学年学期

    :param token: IDS令牌
    :return:
    """

    # 获取学年学期
    resp = token.get(YEAR_SEMESTER_URL)

    data = resp.json()['datas']['dqxnxq']['rows'][0]['DM'].split('-')
    return YearSemester(int(data[0]), int(data[2]))


def clock_to_timedelta(clock: str) -> timedelta:
    """
    时刻转 timedelta

    :param clock: 形如 18:18 的时刻
    :return:
    >>> clock_to_timedelta('18:18')
    datetime.timedelta(seconds=65880)
    """

    hours, minutes = clock.split(':')
    return timedelta(hours=int(hours), minutes=int(minutes))


def get_start_time(token: IDSAuth, year_semester: YearSemester) -> datetime:
    """
    获取指定学年开始时间

    :param token: IDS令牌
    :param year_semester: 学年学期
    :return: 该学年开始时间
    """

    semester_code = get_semester_code(year_semester)

    post_data = {'XN': semester_code[:-2], 'XQ': semester_code[-1:]}
    resp = token.post(YEAR_SEMESTER_INFO_URL, data=post_data)

    return datetime.strptime(resp.json()['datas']['cxjcs']['rows'][0]['XQKSRQ'], '%Y-%m-%d %H:%M:%S')


def get_class_schedule(token: IDSAuth, year_semester: YearSemester) -> ClassSchedule:  # TODO: 更换对第三方更友好的参数
    """
    获取指定学年课程表

    如果是把 oh-my-xdu 作为库来调用，并且只想获取课程表信息，
    推荐直接使用本函数。

    :param token: IDS令牌
    :param year_semester: 学年学期
    :return: 课程表
    """

    post_data = {'XNXQDM': get_semester_code(year_semester)}

    resp = token.post(CLASS_SCHEDULE_URL, data=post_data)

    semester_start_time = get_start_time(token, year_semester)
    schedule_row = resp.json()['datas']['xskcb']['rows']

    class_schedule = ClassSchedule()

    for course in schedule_row:
        for week_count, has_course_in_week in enumerate(course['SKZC']):
            if has_course_in_week == '0':
                continue
            day_count = int(course['SKXQ']) - 1
            course_sequence_start = int(course['KSJC'])

            course_date = semester_start_time + timedelta(week_count * 7 + day_count)
            if 5 <= course_date.month < 10:
                timetable = SUMMER_TIME
            else:
                timetable = WINTER_TIME
            course_start_time, course_end_time = timetable[course_sequence_start // 2]
            course_start_time = course_date + clock_to_timedelta(course_start_time)
            course_end_time = course_date + clock_to_timedelta(course_end_time)
            course_time = course_start_time, course_end_time
            class_schedule.add_course(course_name=course['KCM'],
                                      course_location=course['JASMC'] if course['JASMC'] else '待定',
                                      course_time=course_time)

    return class_schedule


def export_class_schedule(*,
                          save_path: Optional[Path] = None,
                          school_year: Optional[int] = None,
                          semester: Optional[int] = None):
    """
    获取 ehall 在线课程表并转换成 .ics 课程表文件

    :param save_path: .ics 文件存放位置，默认为当前目录
    :param school_year: 学年，默认为当前学年
    :param semester: 学期，可为 1（上学期）或 2（下学期），默认为当前学期
    """

    token = IDSAuth(SERVICE_URL)

    if school_year and semester:
        year_semester = YearSemester(school_year, semester)
    else:
        year_semester = get_latest_year_semester(token)
    semester_code = get_semester_code(year_semester)

    logger.info('即将生成 {} 学年的课程表', semester_code)
    class_schedule = get_class_schedule(token, year_semester)

    if not save_path:
        save_path = Path()

    ical_path = save_path / f'{token.username}_{semester_code}.ics'
    ical_path.write_bytes(class_schedule.to_ical())

    logger.opt(colors=True).success('生成完成，保存路径为 <yellow>{}</yellow>', ical_path.absolute())
