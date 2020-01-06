import json


class Schedule(object):
    def __init__(self, filePointer):
        data = json.load(filePointer)
        self.events = []
        for ev in data["events"]:
            self.events.append(Event(ev))


class Event(object):
    def __init__(self, data):
        self.course = data["course"]
        self.section = data["section"]
        self.eventType = data["type"]
        self.startTime = to_hr_min(data["start"])
        self.endTime = to_hr_min(data["end"])
        self.room = data["room"]


def to_hr_min(timeStr):
    hour, minute = timeStr.split(":")
    return [int(hour), int(minute)]


with open("schedule.json", "r") as F:
    mySchedule = Schedule(F)
