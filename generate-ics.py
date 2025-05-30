#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0

"""
Generate or update an ICS file with a recurring weekly event.

Example:
  python generate-ics.py \
    --name "PB Hustle" \
    --byday FR \
    --time 18:00 \
    --timezone Asia/Kolkata \
    --start-date 2025-06-06 \
    --duration 60 \
    --output pb_calendar.ics
"""

import os
import argparse
from datetime import datetime, timedelta
import pytz
from icalendar import Calendar, Event, Timezone, TimezoneStandard

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate or update an .ics calendar with a recurring weekly event."
    )
    parser.add_argument(
        '-n','--name', required=True,
        help="Event summary/title"
    )
    parser.add_argument(
        '-d','--byday', required=True, nargs='+',
        choices=['MO','TU','WE','TH','FR','SA','SU'],
        metavar='DAY',
        help="Weekday codes for recurrence (e.g. FR for Friday; multiple allowed)"
    )
    parser.add_argument(
        '-t','--time', required=True,
        help="Time of day in 24h format HH:MM"
    )
    parser.add_argument(
        '-s','--start-date',
        help="Start date YYYY-MM-DD; if omitted, uses the next matching weekday"
    )
    parser.add_argument(
        '-u','--duration', type=int, default=60,
        help="Duration in minutes (default: 60)"
    )
    parser.add_argument(
        '-z','--timezone', default='Asia/Kolkata',
        help="Timezone name (default: Asia/Kolkata)"
    )
    parser.add_argument(
        '-o','--output', default='calendar.ics',
        help="Output ICS file (created or updated)"
    )
    return parser.parse_args()

def load_or_create_calendar(path, tzid):
    if os.path.exists(path):
        with open(path,'rb') as f:
            return Calendar.from_ical(f.read())
    cal = Calendar()
    cal.add('prodid', '-//PB Calendar//')
    cal.add('version', '2.0')
    cal.add('X-WR-TIMEZONE', tzid)

    # embed a minimal timezone component
    tz_comp = Timezone()
    tz_comp.add('tzid', tzid)
    std = TimezoneStandard()
    std.add('dtstart', datetime(1970,1,1,0,0,0))
    std.add('tzname', tzid)
    std.add('tzoffsetfrom', timedelta(hours=5, minutes=30))
    std.add('tzoffsetto',   timedelta(hours=5, minutes=30))
    tz_comp.add_component(std)
    cal.add_component(tz_comp)

    return cal

def compute_start(dt_str, time_str, weekdays, tz):
    hh, mm = map(int, time_str.split(':'))
    if dt_str:
        d = datetime.strptime(dt_str, '%Y-%m-%d').date()
        naïve = datetime.combine(d, datetime.min.time()).replace(hour=hh, minute=mm)
        return tz.localize(naïve)

    # find next matching weekday at hh:mm
    now = datetime.now(tz).replace(hour=hh, minute=mm, second=0, microsecond=0)
    codes = {'MO':0,'TU':1,'WE':2,'TH':3,'FR':4,'SA':5,'SU':6}
    targets = {codes[w] for w in weekdays}

    for delta in range(0, 8):
        cand = now + timedelta(days=delta)
        if cand.weekday() in targets and cand > now:
            return cand
    # fallback (shouldn’t happen)
    return now + timedelta(days=7)

def main():
    args = parse_args()
    tz = pytz.timezone(args.timezone)
    cal = load_or_create_calendar(args.output, args.timezone)

    dtstart = compute_start(args.start_date, args.time, args.byday, tz)
    dtend   = dtstart + timedelta(minutes=args.duration)

    ev = Event()
    ev.add('summary', args.name)
    ev.add('dtstart', dtstart)
    ev.add('dtend',   dtend)
    ev.add('rrule',   {'freq':'weekly','byday': args.byday})

    cal.add_component(ev)

    with open(args.output,'wb') as f:
        f.write(cal.to_ical())

    print(f"✅  '{args.output}' has been created/updated.")

if __name__ == '__main__':
    main()