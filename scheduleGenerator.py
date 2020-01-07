import json
from PIL import Image, ImageDraw

columnWidth = 70
dateCellHeight = 30
cellHeight = 50
dayOrdering = {
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6,
    "Sunday": 7,
}


class Schedule(object):
    def __init__(self, data):
        self.events = []
        for ev in data["events"]:
            self.events.append(Event(ev))

        self.days = set()
        for ev in self.events:
            for day in ev.days:
                self.days.add(day)
        self.days = sorted(self.days, key=lambda x: dayOrdering[x])

    def get_events_for_day(self, day):
        """
        Return all events for the specified day, sorted by time.
        """
        dayEvents = []
        for ev in self.events:
            if day in ev.days:
                dayEvents.append(ev)

        return sorted(dayEvents, key=lambda x: x.startTime[0] * 60 + x.startTime[1])

    def initializeSchedule(self):
        """
        Initializes a schedule for the provided days.
        """
        self.canvas = Image.new(
            "RGB",
            (len(self.days) * columnWidth, cellHeight * self._get_max_daily_events()),
            (255, 255, 255),
        )
        self.draw = ImageDraw.Draw(self.canvas, "RGB")
        for i in range(len(self.days)):
            x, y = columnWidth * (0.5 + i), dateCellHeight / 2
            txtWidth, txtHeight = self.draw.textsize(self.days[i])
            self.draw.text(
                (x - txtWidth / 2, y - txtHeight / 2), self.days[i], fill=(255, 0, 0)
            )

        for i in range(len(self.days) - 1):
            self._verticalLine(columnWidth * (1 + i), (0, 0, 0))

        self._horizontalLine(dateCellHeight, (0, 0, 0))

    def saveSchedule(self, filename=None):
        """
        Saves the schedule with the provided filename.
        """
        if filename:
            self.canvas.save(filename, "PNG")
        else:
            self.canvas.save("outputSchedule.png", "PNG")

    def _verticalLine(self, x, color):
        self.draw.line([(x, 0), (x, self.canvas.height)], fill=color, width=2)

    def _horizontalLine(self, y, color):
        self.draw.line([(0, y), (self.canvas.width, y)], fill=color, width=2)

    def _get_max_daily_events(self):
        """
        Return the number of events for the busiest day.
        """
        daily_events = []
        for day in self.days:
            daily_events.append(self.get_events_for_day(day))

        number_of_daily_events = map(len, daily_events)
        return max(number_of_daily_events)

    def _find_common_break(self):
        pass


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

    def _printEvent(self, pos, color):
        """
        Prints the event in the position provided.
            'pos' represents the top left corner.
        """


def to_hr_min(timeStr):
    hour, minute = timeStr.split(":")
    return [int(hour), int(minute)]


with open("schedule.json", "r") as F:
    mySchedule = Schedule(json.load(F))

mySchedule.initializeSchedule()
mySchedule.saveSchedule()
