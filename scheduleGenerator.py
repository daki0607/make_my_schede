import json
from PIL import Image, ImageDraw, ImageFont


scale = 3
gutterWidth = 30 * scale
columnWidth = 70 * scale
dateCellHeight = 30 * scale
segmentHeight = 22 * scale
dayOrdering = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}
dayFont = ImageFont.truetype(font="Gelasio-Regular.ttf", size=scale * 11)
cellFont = ImageFont.truetype(font="Gelasio-Regular.ttf", size=scale * 11)


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
        # Create a canvas with width based on the number of days and height based on the segments in the busiest day
        self.canvas = Image.new(
            "RGB",
            (
                gutterWidth + len(self.days) * columnWidth,
                dateCellHeight + segmentHeight * self._get_max_daily_segments(),
            ),
            (255, 255, 255),
        )
        self.draw = ImageDraw.Draw(self.canvas, "RGB")

        for i in range(len(self.days)):
            # Set x and y of each day's text as the middle of the text box
            x, y = gutterWidth + columnWidth * (0.5 + i), dateCellHeight / 2
            txtWidth, txtHeight = self.draw.textsize(self.days[i], font=dayFont)
            self.draw.text(
                (x - txtWidth / 2, y - txtHeight / 2),
                self.days[i],
                fill=(255, 0, 0),
                font=dayFont,
            )

        # Draw vertical lines between the days
        for i in range(len(self.days)):
            self._verticalLine(gutterWidth + columnWidth * (i), (0, 0, 0))

        # Draw a line underneath the days
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

    def _get_max_daily_segments(self):
        """
        Return the number of 30-minute segments for the busiest day.
        """
        start, end = self._get_absolute_start_end_time()

        return (end - start) // 30 + 1

    def _draw_event(self, eventStr, pos, topBotY, txtColor, lineColor):
        """
        pos represents the center of the bounding box.
        """
        xPos, yPos = pos
        txtWidth, txtHeight = self.draw.multiline_textsize(eventStr, font=cellFont)
        self.draw.multiline_text(
            (xPos - txtWidth / 2, yPos - txtHeight / 2),
            eventStr,
            fill=txtColor,
            align="center",
            spacing=0,
            font=cellFont,
        )
        self.draw.line(
            [
                (xPos - columnWidth / 2, topBotY[0] + 2),
                (xPos + columnWidth / 2, topBotY[0] + 2),
            ],
            fill=lineColor,
            width=2,
        )
        self.draw.line(
            [
                (xPos - columnWidth / 2, topBotY[1] - 2),
                (xPos + columnWidth / 2, topBotY[1] - 2),
            ],
            fill=lineColor,
            width=2,
        )

    def fill_schedule(self):
        absStart, absEnd = self._get_absolute_start_end_time()
        minY, maxY = dateCellHeight, self.canvas.height
        interpolationFactor = (maxY - minY) / (absEnd - absStart)

        for ev in self.events:
            startEventY = interpolationFactor * (ev.startTime.time - absStart) + minY
            endEventY = interpolationFactor * (ev.endTime.time - absStart) + minY
            eventY = (startEventY + endEventY) / 2

            for d in ev.days:
                eventX = gutterWidth + (self.days.index(d) + 0.5) * columnWidth
                self._draw_event(
                    ev._get_formatted_event(),
                    (eventX, eventY),
                    (startEventY, endEventY),
                    (0, 0, 0),
                    (0, 0, 255),
                )

    def _get_absolute_start_end_time(self):
        startTime = 25 * 60
        endTime = 0

        for ev in self.events:
            startTime = min(ev.startTime.time, startTime)
            endTime = max(ev.endTime.time, endTime)

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
        return f"{self.course}\n{self.eventType.capitalize()}\n{self.room}"

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
# mySchedule.print()
