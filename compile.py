#!/usr/bin/python3

from datetime import datetime
from datetime import timedelta
import jinja2
import os
import psycopg2
import psycopg2.extras
import pytz
import sys

from common import *

j2 = jinja2.Environment(
    loader=jinja2.FileSystemLoader("layouts"),
    extensions=["pyjade.ext.jinja.PyJadeExtension"]
)

def is_url(url):
    if url:
        if url.startswith("<<"):
            return False
        return True
    return False

j2.filters["is_url"] = is_url



if __name__ == "__main__":
    args = get_args()
    config = get_config(args.config)
    dbstring = db_string(config)

    dist = "dist"

    conn = db_connect(dbstring)
    if not conn:
        sys.exit(1)

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""select e.event_id,
                              e.name event_name,
                              e.start_time,
                              e.end_time,
                              e.place_name,
                              e.event_type,
                              e.fb_id,
                              e.attending_count,
                              e.declined_count,
                              e.maybe_count,
                              e.noreply_count,
       format('https://facebook.com/events/%s', e.fb_id) link,
                              p.name page_name,
                              p.username,
                              p.page_id,
                              p.picture
                         from events e
                         join pages  p
                           on p.page_id = e.page_id

                       -- Only public events!
                        where e.event_type = 'public'

                       order by start_time desc,
                       e.attending_count desc""")

        events = list(cur.fetchall())


        cur.execute("""select p.*,
                              count(*) event_count
                         from pages p
                         join events e
                           on p.page_id = e.page_id
                     group by p.page_id
                     order by p.likes desc""", ())

        pages = list(cur.fetchall())
    finally:
        conn.close()

    today = datetime.today()
    today = datetime.combine(today, datetime.min.time())
    today = today.replace(tzinfo=pytz.UTC)
    tomorrow = today + timedelta(days=1)
    tomorrow2 = today + timedelta(days=2)
    weekday = today.weekday()

    week_start = today - timedelta(days=weekday)
    week_end = week_start + timedelta(weeks=1)

    current_week = True
    # if it is weekend at the moment, show next week instead of current week
    if weekday >= 5:
        current_week = False
        week_start += timedelta(weeks=1)
        week_end += timedelta(weeks=1)


    events_today = [e for e in events if e["start_time"].date() == today.date()]
    events_tomorrow = [e for e in events if e["start_time"].date() == tomorrow.date()]
    events_tomorrow2 = [e for e in events if e["start_time"].date() == tomorrow2.date()]
    events_week = [e for e in events if week_start.date() <= e["start_time"].date() < week_end.date()]

    t = j2.get_template("events.jade")
    with open(os.path.join(dist, "index.html"), "w") as out:
        out.write(t.render(
            events=events,
            events_today=events_today,
            events_tomorrow=events_tomorrow,
            events_tomorrow2=events_tomorrow2,
            events_week=events_week,
            now=datetime.now(),
            today=today,
            tomorrow=tomorrow,
            tomorrow2=tomorrow2,
            current_week=current_week,
        ))

    t = j2.get_template("all_events.jade")
    with open(os.path.join(dist, "vsechny.html"), "w") as out:
        out.write(t.render(
            events=events,
            now=datetime.now(),
        ))

    t = j2.get_template("pages.jade")
    with open(os.path.join(dist, "kluby.html"), "w") as out:
        out.write(t.render(
            pages=pages,
            now=datetime.now(),
        ))

