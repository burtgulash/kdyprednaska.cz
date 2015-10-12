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
        cur.execute("""select event_id,
                              page_id,
                              name,
                              start_time
                         from events
                       order by start_time desc""")

        events = list(cur.fetchall())
    finally:
        conn.close()

    t = j2.get_template("index.jade")
    print(t.render(name="world", events=events))

