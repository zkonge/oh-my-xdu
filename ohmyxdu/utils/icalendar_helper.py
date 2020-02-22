from typing import Tuple
from datetime import datetime

from icalendar import Calendar, Event

__all__ = ('ClassSchedule',)


class ClassSchedule(Calendar):
    def add_course(self,
                   course_name: str,
                   course_location: str,
                   course_time: Tuple[datetime, datetime]):
        event = Event()
        event.add('summary', course_name)
        event.add('location', course_location)
        event.add('dtstart', course_time[0])
        event.add('dtend', course_time[1])
        self.add_component(event)
