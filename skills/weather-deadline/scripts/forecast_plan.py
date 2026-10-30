"""Original, dependency-free synthetic deadline/weather planner. No credentials or write APIs."""

import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


def plan(events, day, minutes, zone):
    start = datetime.combine(day, time(8), zone)
    end = datetime.combine(day, time(20), zone)
    now = datetime.now(zone)
    if day == now.date():
        start = min(max(start, now), end)
    intervals = []
    for event in events:
        a, b = (datetime.fromisoformat(event[k]) for k in ('start', 'end'))
        if a.tzinfo is None or b.tzinfo is None or b <= a:
            raise ValueError('Every synthetic event must have timezone-aware start < end')
        a, b = max(a.astimezone(zone), start), min(b.astimezone(zone), end)
        if a < b:
            intervals.append((a, b, event['title']))
    intervals.sort()
    conflicts, slots, cursor = [], [], start
    for index, (a, b, title) in enumerate(intervals):
        conflicts.extend([prior[2], title] for prior in intervals[:index] if prior[1] > a)
        if (a-cursor).total_seconds() >= minutes*60:
            slots.append({'start': cursor.isoformat(), 'end': a.isoformat()})
        cursor = max(cursor, b)
    if (end-cursor).total_seconds() >= minutes*60:
        slots.append({'start': cursor.isoformat(), 'end': end.isoformat()})
    return {'conflicts': conflicts, 'free_slots': slots, 'requested_minutes': minutes}


def forecast(zone):
    query = urllib.parse.urlencode({'latitude': 34.05, 'longitude': -118.24,
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_probability_max',
        'timezone': zone.key, 'forecast_days': 2})
    with urllib.request.urlopen('https://api.open-meteo.com/v1/forecast?'+query, timeout=15) as response:
        raw = response.read(2*1024*1024+1)
    if len(raw)>2*1024*1024:
        raise ValueError('Weather response exceeds limit')
    data = json.loads(raw)
    return {'source': 'Open-Meteo', 'source_url': 'https://open-meteo.com/',
            'retrieved_local': datetime.now(zone).isoformat(), 'location': 'Los Angeles city centre',
            'resolution': 'daily; no hourly guarantee', 'units': data.get('daily_units'),
            'daily': data['daily']}


def main():
    parser = argparse.ArgumentParser()
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('--demo', action='store_true')
    choice.add_argument('--events', type=Path, help='Explicitly synthetic JSON: {synthetic:true, events:[...]}')
    parser.add_argument('--day', help='YYYY-MM-DD; default tomorrow')
    parser.add_argument('--minutes', type=int, default=45)
    parser.add_argument('--timezone', default='America/Los_Angeles')
    args = parser.parse_args()
    if not 5 <= args.minutes <= 480:
        parser.error('Duration must be between 5 and 480 minutes')
    zone = ZoneInfo(args.timezone)
    day = datetime.fromisoformat(args.day).date() if args.day else datetime.now(zone).date()+timedelta(days=1)
    if args.demo:
        start = datetime.combine(day, time(10), zone)
        events = [{'title': title, 'start': (start+timedelta(minutes=offset)).isoformat(),
                   'end': (start+timedelta(minutes=offset+60)).isoformat()}
                  for title, offset in [('Fictional Cardinal planning', 0), ('Fictional Cardinal review', 30)]]
    else:
        if args.events.stat().st_size > 1024*1024:
            parser.error('Synthetic event fixture exceeds 1 MiB')
        fixture = json.loads(args.events.read_text())
        if fixture.get('synthetic') is not True:
            parser.error('Use explicitly synthetic assignment data only')
        events = fixture['events']
    result = {'synthetic': True, 'day': day.isoformat(), 'timezone': zone.key,
              'calendar': plan(events, day, args.minutes, zone)}
    try:
        result['weather'] = forecast(zone)
    except (OSError, ValueError, KeyError) as exc:
        result['weather'] = {'status': 'unavailable', 'error_category': type(exc).__name__}
    result['guidance'] = 'Choose a returned slot; prefer indoor work when rain is forecast. Daily data cannot guarantee dry weather at a particular hour. Never invent a deadline.'
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
