import json
from PIL import Image, ImageDraw

columnWidth = 70
dateCellHeight = 30
cellHeight = 50
dayOrdering = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}


class Schedule(object):
    def __init__(self, data):
        self.events = []
        for ev in data["events"]:
            self.events.append(Event(ev))
        # Sort events by time and day
        self.events.sort(key=lambda x: (x.startTime.time, dayOrdering[x.days[0]]))

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

        # No need to sort because events are already sorted by time, then day
        return dayEvents

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
        absStart, absEnd = self._get_absolute_start_end_time()
        minY, maxY = dateCellHeight, self.canvas.height

        for ev in self.events:
            # Linearly interpolate y
            eventY = (maxY - minY) / (absEnd - absStart) * (
                ev.startTime.to_absolute() - absStart
            ) + minY

            for d in ev.days:
                eventX = self.days.index(d) * columnWidth
                self._print_event(ev._get_formatted_event(), eventX, eventY, (0, 0, 0))

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

    def __str__(self):
        return f"{self.course} {self.eventType} at {self.startTime} to {self.endTime} ({self.endTime.time - self.startTime.time} minutes)."

    def _get_formatted_event(self):
        """
        Return an event string in schedule format.
        """
        return f"{self.course}\n{self.eventType}\n{self.room}"

    def is_during(self, T):
        """
        Return if time T is within the start and end times of the event.
        """
        return self.startTime.time < T.time and T.time > self.endTime.time


class Time(object):
    """
    Store time as the number of minutes since 12:00am.
    """

    def __init__(self, time):
        self.time = time

    @classmethod
    def from_string(cls, timeStr):
        hour, minute = timeStr.split(":")
        return cls(int(hour) * 60 + int(minute))

    @classmethod
    def from_hour_minute(cls, hour, minute):
        return cls(hour * 60 + minute)

    def to_hour_min(self):
        return (self.time // 60, self.time % 60)

    def __add__(self, other):
        return Time(self.time + other.time)

    def __str__(self):
        hour, minute = self.to_hour_min()
        return f"{hour}:{minute}"


with open("schedule.json", "r") as F:
    mySchedule = Schedule(json.load(F))

mySchedule.initializeSchedule()
mySchedule.fill_schedule()
mySchedule.saveSchedule()
