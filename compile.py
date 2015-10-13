#!/usr/bin/python3

import configparser
import jinja2
import psycopg2
import psycopg2.extras

from common import get_config, db_string

j2 = jinja2.Environment(
    loader=jinja2.FileSystemLoader("layouts"),
    extensions=["pyjade.ext.jinja.PyJadeExtension"]
)

if __name__ == "__main__":
    config = get_config()
    dbstring = db_string(config)

    conn = psycopg2.connect(dbstring)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""select e.event_id,
                              e.name event_name,
                              e.start_time,
                              e.place_name,
                              p.name page_name,
                              p.page_id
                         from events e
                         join pages  p
                           on p.page_id = e.page_id
                       order by start_time desc""")

        events = list(cur.fetchall())
    finally:
        conn.close()

    t = j2.get_template("index.jade")
    print(t.render(events=events))

