#!/usr/bin/env python3
"""
Generate an .ics file for a recurring event:
  Event: PB Calendar
  When: Every Friday at 6 PM IST
Output: pb_calendar.ics in the current directory
"""

from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event, Timezone, TimezoneStandard

def create_pb_hustle_ics(filename='pb_calendar.ics'):
    # 1. Base calendar
    cal = Calendar()
    cal.add('prodid', '-//PB Calendar//')
    cal.add('version', '2.0')
    cal.add('X-WR-TIMEZONE', 'Asia/Kolkata')

    # 2. Timezone definition (optional, but ensures clients know IST)
    tz = Timezone()
    tz.add('tzid', 'Asia/Kolkata')
    std = TimezoneStandard()
    std.add('dtstart', datetime(1970, 1, 1, 0, 0, 0))
    std.add('tzname', 'IST')
    std.add('tzoffsetfrom', timedelta(hours=5, minutes=30))
    std.add('tzoffsetto',   timedelta(hours=5, minutes=30))
    tz.add_component(std)
    cal.add_component(tz)

    # 3. Compute next Friday at 18:00 IST (aware datetime)
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    # Friday is weekday 4 (Mon=0 … Sun=6)
    days_ahead = 4 - now.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    first_friday = (now + timedelta(days=days_ahead)).replace(
        hour=18, minute=0, second=0, microsecond=0
    )
    # first_friday is already tz-aware, so we do NOT call localize()

    # 4. Build the event
    event = Event()
    event.add('summary', 'PB Hustle')
    event.add('dtstart', first_friday)
    event.add('dtend',   first_friday + timedelta(hours=1))  # assumes 1 h duration
    event.add('rrule',   {'freq': 'weekly', 'byday': ['FR']})

    cal.add_component(event)

    # 5. Write to .ics
    with open(filename, 'wb') as f:
        f.write(cal.to_ical())

    print(f"✅  '{filename}' created; import it into your calendar.")

if __name__ == '__main__':
    create_pb_hustle_ics()
