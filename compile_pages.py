#!/usr/bin/python3

import jinja2
import psycopg2
import psycopg2.extras
import sys

from common import *

j2 = jinja2.Environment(
    loader=jinja2.FileSystemLoader("layouts"),
    extensions=["pyjade.ext.jinja.PyJadeExtension"]
)

j2.filters["is_url"] = lambda text: text.startswith("http") if text else False

if __name__ == "__main__":
    args = get_args()
    config = get_config(args.config)
    dbstring = db_string(config)

    conn = db_connect(dbstring)
    if not conn:
        sys.exit(1)

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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

    t = j2.get_template("pages.jade")
    print(t.render(pages=pages))

