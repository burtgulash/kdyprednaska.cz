#!/usr/bin/python3

import configparser
import glob
import jinja2
import psycopg2

j2 = jinja2.Environment(
    loader=jinja2.FileSystemLoader("layouts"),
    extensions=["pyjade.ext.jinja.PyJadeExtension"]
)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.readfp(open("config.ini", "r"))
    config.read(glob.glob("*.priv.ini"))

    dbstring = "host={} dbname={} user={} password={}".format(
            config.get("database", "host"),
            config.get("database", "dbname"),
            config.get("database", "user"),
            config.get("database", "password"))

    conn = psycopg2.connect(dbstring)
    try:
        cur = conn.cursor()
        cur.execute("""select event_id,
                              name,
                              start_time
                         from events
                       order by start_time desc""")

        events = list(cur.fetchall())
    finally:
        conn.close()

    print(events)

    t = j2.get_template("index.jade")
    print(t.render(name="world"))

