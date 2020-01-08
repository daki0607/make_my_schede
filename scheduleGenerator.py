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

        return sorted(dayEvents, key=lambda x: x.startTime.to_absolute())

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

    def _print_event(self, eventStr, xPos, yPos, color):
        x, y = xPos + columnWidth / 2, yPos + cellHeight / 2
        txtWidth, txtHeight = self.draw.multiline_textsize(eventStr)
        self.draw.multiline_text(
            (x - txtWidth / 2, y - txtHeight / 2),
            eventStr,
            fill=color,
            align="center",
            spacing=0,
        )

    def fill_schedule(self):
        self.absStart, self.absEnd = self._get_absolute_start_end_time()

        for ev in self.events:
            self._print_event(ev._get_formatted_event(), 0, dateCellHeight, (0, 0, 0))

    def _get_absolute_start_end_time(self):
        startTime = 25 * 60
        endTime = 0

        for ev in self.events:
            startTime = min(ev.startTime.to_absolute(), startTime)
            endTime = max(ev.endTime.to_absolute(), endTime)

        return (startTime, endTime)

    def print(self):
        for ev in self.events:
            print(ev)


class Event(object):
    def __init__(self, data):
        self.course = data["course"]
        self.section = data["section"]
        self.eventType = data["type"]
        self.startTime = Time.from_string(data["start"])
        self.endTime = Time.from_string(data["end"])
        self.room = data["room"]
        self.days = data["days"]

        self.duration = self.endTime.to_absolute() - self.startTime.to_absolute()

    def __str__(self):
        return f"{self.course} {self.eventType} at {self.startTime} to {self.endTime} ({self.duration} minutes)."

    def _get_formatted_event(self):
        """
        Return an event string in schedule format.
        """
        return f"{self.course}\n{self.eventType}\n{self.room}"


class Time(object):
    def __init__(self, hour, minute):
        self.hour = hour
        self.minute = minute

    @classmethod
    def from_string(cls, timeStr):
        hour, minute = timeStr.split(":")
        return cls(int(hour), int(minute))

    @classmethod
    def from_absolute(cls, absoluteTime):
        hour, minute = absoluteTime // 60, absoluteTime % 60
        return cls(hour, minute)

    def to_absolute(self):
        return 60 * self.hour + self.minute

    def __add__(self, other):
        return Time.from_absolute(self.to_absolute() + other.to_absolute())

    def __str__(self):
        return f"{self.hour}:{self.minute}"


with open("schedule.json", "r") as F:
    mySchedule = Schedule(json.load(F))

mySchedule.print()
mySchedule.initializeSchedule()
mySchedule.fill_schedule()
mySchedule.saveSchedule()
