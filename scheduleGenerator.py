import json


class Schedule(object):
    def __init__(self, events_json):
        pass


class Event(object):
    def __init__(self, course, section, eventType, startTime, endTime, room):
        self.course = course
        self.section = section
        self.eventType = eventType
        self.startTime = to_hr_min(startTime)
        self.endTime = to_hr_min(endTime)
        self.room = room


def to_hr_min(timeStr):
    pass
