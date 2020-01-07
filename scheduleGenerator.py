import json
from PIL import Image, ImageDraw

columnWidth = 80
dateCellHeight = 50
cellHeight = 100


class Schedule(object):
    def __init__(self, data):
        self.events = []
        for ev in data["events"]:
            self.events.append(Event(ev))

    def get_events_for_day(self, day):
        """
        Return all events for the specified day, sorted by time.
        """
        dayEvents = []
        for ev in self.events:
            if day in ev.days:
                dayEvents.append(ev)

        return sorted(dayEvents, key=lambda x: x.startTime[0] * 60 + x.startTime[1])

    def initializeSchedule(self, days):
        """
        Initializes a schedule for the provided days.
        """
        self.canvas = Image.new("RGB", (len(days) * columnWidth, 400), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.canvas, "RGB")
        for i in range(len(days)):
            x, y = columnWidth * (0.5 + i), dateCellHeight / 2
            txtWidth, txtHeight = self.draw.textsize(days[i])
            self.draw.text(
                (x - txtWidth / 2, y - txtHeight / 2), days[i], fill=(255, 0, 0)
            )

    def saveSchedule(self, filename=None):
        if filename:
            self.canvas.save(filename, "PNG")
        else:
            self.canvas.save("outputSchedule.png", "PNG")


class Event(object):
    def __init__(self, data):
        self.course = data["course"]
        self.section = data["section"]
        self.eventType = data["type"]
        self.startTime = to_hr_min(data["start"])
        self.endTime = to_hr_min(data["end"])
        self.room = data["room"]
        self.days = data["days"]

        self.duration = (60 * self.endTime[0] + self.endTime[1]) - (
            60 * self.startTime[0] + self.startTime[1]
        )

    def __str__(self):
        return f"{self.course} {self.eventType} at {self.startTime[0]}:{self.startTime[1]} to {self.endTime[0]}:{self.endTime[1]} ({self.duration} minutes)."


def to_hr_min(timeStr):
    hour, minute = timeStr.split(":")
    return [int(hour), int(minute)]


with open("schedule.json", "r") as F:
    mySchedule = Schedule(json.load(F))

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
mySchedule.initializeSchedule(days)
mySchedule.saveSchedule()
