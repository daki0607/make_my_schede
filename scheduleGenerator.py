import json
from PIL import Image, ImageDraw, ImageFont
from random import shuffle


scale = 3
gutterWidth = 27 * scale
columnWidth = 70 * scale
dateCellHeight = 30 * scale
segmentHeight = 22 * scale
bottomBuffer = 10 * scale

dayOrdering = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}
eventColors = ["red", "blue", "green", "magenta", "cyan", "orange", "pink"]
shuffle(eventColors)

dayFont = ImageFont.truetype(font="Gelasio-Regular.ttf", size=scale * 11)
cellFont = ImageFont.truetype(font="Gelasio-Regular.ttf", size=scale * 9)
timeFont = ImageFont.truetype(font="Gelasio-Regular.ttf", size=scale * 6)


class Schedule(object):
    def __init__(self, data):
        self.events = []
        for ev in data["events"]:
            self.events.append(Event(ev))
        # Sort events by time and day
        self.events.sort(key=lambda x: (
            x.startTime.time, dayOrdering[x.days[0]]))

        self.days = set()
        for ev in self.events:
            for day in ev.days:
                self.days.add(day)
        self.days = sorted(self.days, key=lambda x: dayOrdering[x])

        start, end = self._get_absolute_start_end_time()
        start = (start.time // 30) * 30
        end = (end.time // 30 + 2) * 30
        allTimes = [Time(time) for time in range(start, end, 30)]
        self.scheduledTimes = allTimes

        for ev in self.events:
            allTimes = [
                T for T in allTimes if not T.is_between(
                    ev.startTime, ev.endTime)
            ]

        self.scheduledTimes = [
            T for T in self.scheduledTimes if T not in allTimes]

    def initializeSchedule(self):
        """
        Initializes a schedule for the provided days.
        """
        # Create a canvas with width based on the number of days and height #
        #  based on the segments in the busiest day
        self.canvas = Image.new(
            "RGB",
            (
                gutterWidth + len(self.days) * columnWidth,
                dateCellHeight + bottomBuffer +
                segmentHeight * len(self.scheduledTimes),
            ),
            "white",
        )
        self.draw = ImageDraw.Draw(self.canvas, "RGB")

        for i in range(len(self.days)):
            # Set x and y of each day's text as the middle of the text box
            x, y = gutterWidth + columnWidth * (0.5 + i), dateCellHeight / 2
            txtWidth, txtHeight = self.draw.textsize(
                self.days[i], font=dayFont)
            self.draw.text(
                (x - txtWidth / 2, y - txtHeight / 2),
                self.days[i],
                fill=(255, 0, 0),
                font=dayFont,
            )

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

    def _draw_event(self, ev, pos, txtColor="black"):
        """
        'pos' represents the center of the bounding box.
        """
        eventStr = ev._get_formatted_event()
        x, y = pos
        lineColor = ev.color
        txtWidth, txtHeight = self.draw.multiline_textsize(
            eventStr, font=cellFont)

        self.draw.multiline_text(
            (x - txtWidth / 2, y - txtHeight / 2),
            eventStr,
            fill=txtColor,
            align="center",
            spacing=0,
            font=cellFont,
        )

    def _draw_time(self, timeStr, y, txtColor):
        txtWidth, txtHeight = self.draw.textsize(timeStr, font=timeFont)
        self.draw.text(
            ((gutterWidth - 10 - txtWidth)/2, y - txtHeight/2),
            timeStr,
            fill=txtColor,
            font=timeFont,
            stroke_fill="lightgray",
            stroke_width=1,
        )
        self.draw.line([((gutterWidth + txtWidth)/2, y),
                        (gutterWidth - 5, y)],
                       fill=txtColor, width=2)

    def _draw_superellipse(self, boundingBox, color):
        (x0, y0), (x1, y1) = boundingBox
        cx = (x0 + x1)/2
        cy = (y0 + y1)/2

        # Top left
        self.draw.pieslice([(x0, y0), (cx, cy)],
                           180, 270, fill=color)
        # Top right
        self.draw.pieslice([(cx, y0), (x1, cy)],
                           270, 360, fill=color)
        # Bottom left
        self.draw.pieslice([(x0, cy), (cx, y1)],
                           90, 180, fill=color)
        # Bottom right
        self.draw.pieslice([(cx, cy), (x1, y1)],
                           0, 90, fill=color)

        # Top rectangle
        self.draw.rectangle([((x0 + cx)/2, y0),
                             ((x1 + cx)/2, (y0 + cy)/2)],
                            fill=color)
        # Left rectangle
        self.draw.rectangle([(x0, (y0 + cy)/2),
                             ((x0 + cx)/2, (y1 + cy)/2)],
                            fill=color)
        # Right rectangle
        self.draw.rectangle([((x1 + cx)/2, (y0 + cy)/2),
                             (x1, (y1 + cy)/2)],
                            fill=color)
        # Bottom rectangle
        self.draw.rectangle([((x0 + cx)/2, (y1 + cy)/2),
                             ((x1 + cx)/2, y1)],
                            fill=color)
        # Center rectangle
        self.draw.rectangle([((x0 + cx)/2, (y0 + cy)/2),
                             ((x1 + cx)/2, (y1 + cy)/2)],
                            fill=color)

    def _get_y_pos(self, eventTime):
        i = 0
        while self.scheduledTimes[i].time <= eventTime.time:
            i += 1

            if (i > len(self.scheduledTimes)):
                break

        i -= 1

        y = dateCellHeight + segmentHeight * i

        # The preceding time, rounded to 30 minutes
        timeSegmentBefore = (eventTime.time // 30) * 30
        # Linearly interpolate to find exact y position
        y += segmentHeight / 30 * (eventTime.time - timeSegmentBefore)

        return y

    def fill_schedule(self):
        for ev in self.events:
            for day in ev.days:
                x = gutterWidth + columnWidth * (self.days.index(day) + 0.5)
                startY = self._get_y_pos(ev.startTime)
                endY = (startY
                        + segmentHeight
                        * ((ev.endTime.time - ev.startTime.time) // 30)
                        + ((ev.endTime.time - ev.startTime.time) % 30))
                # Draw the event
                #  Get the event's position
                self._draw_superellipse([(x - columnWidth/2, startY),
                                         (x + columnWidth/2, endY)],
                                        ev.color)
                self._draw_event(ev, (x, (startY + endY) / 2))
                # Draw the time
                self._draw_time(str(ev.startTime), startY, ev.color)
                self._draw_time(str(ev.endTime), endY, ev.color)

        # Draw vertical lines between the days
        for i in range(len(self.days)):
            self._verticalLine(gutterWidth + columnWidth * (i), "gray")

        # Draw a line underneath the days
        self.draw.line([(gutterWidth, dateCellHeight),
                        (self.canvas.width, dateCellHeight)],
                       fill="gray", width=2,
                       )

    def _get_absolute_start_end_time(self):
        startTime = min([ev.startTime for ev in self.events])
        endTime = max([ev.endTime for ev in self.events])

        return (startTime, endTime)


class Event(object):
    colorPos = 0

    def __init__(self, data):
        self.course = data["course"]
        self.section = data["section"]
        self.eventType = data["type"]
        self.startTime = Time.from_string(data["start"])
        self.endTime = Time.from_string(data["end"])
        self.room = data["room"]
        self.days = data["days"]

        self.color = eventColors[Event.colorPos]
        Event.colorPos += 1

    def __str__(self):
        return f"""{self.course} {self.eventType} at {self.startTime} to \
                {self.endTime} ({self.endTime.time - self.startTime.time} \
                minutes)."""

    def _get_formatted_event(self):
        """
        Return an event string in schedule format.
        """
        return f"{self.course}\n{self.eventType.capitalize()}\n{self.room}"


class Time(object):
    """
    Store time as the number of minutes since 12: 00am.
    """

    def __init__(self, time):
        self.time = time

    @classmethod
    def from_string(cls, timeStr):
        """
        Builds a Time object from the format "hh: mm".
        """
        hour, minute = timeStr.split(":")
        return cls(int(hour) * 60 + int(minute))

    def to_hour_min(self):
        """
        Converts a Time object to the format(hh, mm).
        """
        return (self.time // 60, self.time % 60)

    def to_12_hour(self):
        """
        Converts a Time object to the format(hh, mm) while honoring 12-hour
        time.
        """
        h, m = self.to_hour_min()
        h = h - 12 if h > 12 else h
        return (h, m)

    def __str__(self):
        hour, minute = self.to_12_hour()
        return f"{hour}:{minute:02}"

    def __repr__(self):
        hour, minute = self.to_12_hour()
        return f"Time object {{{hour}:{minute:02}}}"

    def __eq__(self, other):
        return self.time == other.time

    def __gt__(self, other):
        return self.time > other.time

    def __lt__(self, other):
        return self.time < other.time

    def is_between(self, time1, time2):
        """
        Return True if the absolute time is between time1 and time2, inclusive.
        """
        return time1.time <= self.time and self.time <= time2.time


with open("schedule.json", "r") as F:
    mySchedule = Schedule(json.load(F))


mySchedule.initializeSchedule()
mySchedule.fill_schedule()
mySchedule.saveSchedule()
# mySchedule.print()
# for T in mySchedule.scheduledTimes:
#     print(T)
