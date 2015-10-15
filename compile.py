#!/usr/bin/python3

import datetime
import jinja2
import psycopg2
import psycopg2.extras
import pytz
import sys

from common import *

j2 = jinja2.Environment(
    loader=jinja2.FileSystemLoader("layouts"),
    extensions=["pyjade.ext.jinja.PyJadeExtension"]
)

if __name__ == "__main__":
    args = get_args()
    config = get_config(args.config)
    dbstring = db_string(config)

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

                       order by start_time desc""")

        events = list(cur.fetchall())
    finally:
        conn.close()

    today = datetime.datetime.today().replace(tzinfo=pytz.UTC)
    t = j2.get_template("events.jade")
    print(t.render(
        events=events,
        today=today,
        tomorrow=today + datetime.timedelta(days=1)
    ))

