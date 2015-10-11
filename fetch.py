#!/usr/bin/python3

import configparser
import csv
import glob
import psycopg2
import requests
import sys



def ERROR(msg, *a, **k):
    print(msg, *a, file=sys.stderr, **k)

def fetch_data(page_id, token):
    url = "https://graph.facebook.com/{version}/{page_id}/events?access_token={token}".format(
            version="v2.5",
            page_id=page_id,
            token=token,
    )

    return requests.get(url)

def store_location(cur, country, city, street, lat, lon, zip):
    cur.execute("""select location_id
                     from locations
                    where country is not distinct from %s
                      and city    is not distinct from %s
                      and street  is not distinct from %s
                      and lat     is not distinct from %s
                      and lon     is not distinct from %s
                      and zip     is not distinct from %s""", (country, city, street, lat, lon, zip))

    location_id = cur.fetchone()
    if location_id:
        location_id = location_id[0]
    else:
        cur.execute("""insert into locations (country,
                                              city,
                                              street,
                                              lat,
                                              lon,
                                              zip)
                     values (%s, %s, %s, %s, %s, %s)
                     returning location_id""", (country, city, street, lat, lon, zip)
        )

        location_id = cur.fetchone()[0]

        print("stored location, id=%s, country=%s, city=%s, street=%s, lat=%s, lon=%s, zip=%s" % (
            location_id, country, city, street, lat, lon, zip))

    return location_id

def store_event(cur, page_id, fb_id, name, description, start_time, place_name, loc_id):
    cur.execute("select exists (select 1 from events where fb_id = %s)", (fb_id, ))
    exists = cur.fetchone()[0]

    if not exists:
        cur.execute("""insert into events (page_id,
                                           fb_id,
                                           name,
                                           description,
                                           start_time,
                                           place_name,
                                           location_id)
                     values (%s, %s, %s, %s, %s, %s, %s)""", (
            page_id, fb_id, name, description, start_time, place_name, loc_id
        ))
        print("stored event, page=%s, fb_id=%s, name=%s, place=%s, start=%s" % (
            page_id, fb_id, name, place_name, start_time))


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.readfp(open("config.ini", "r"))
    config.read(glob.glob("*.priv.ini"))

    dbstring = "host={} dbname={} user={} password={}".format(config.get("database", "host"),
                                                              config.get("database", "dbname"),
                                                              config.get("database", "user"),
                                                              config.get("database", "password"))

    token = config.get("facebook", "token")
    pages = config.get("facebook", "pages")

    parser = csv.reader([pages])
    pages = next(parser)

    conn = psycopg2.connect(dbstring)
    cur = conn.cursor()

    print("processing pages", pages)

    for page_id in pages:
        r = fetch_data(page_id, token)
        if r.status_code != 200:
            ERROR("could not retrieve events, page=%s, err=%s" % (page_id, r.status_code))
            continue

        for event in r.json()["data"]:
            loc_id = None
            place_name = None

            try:
                if "place" in event:
                    place_name = event["place"]["name"]

                    if "location" in event["place"]:
                        loc = event["place"]["location"]
                        loc_id = store_location(cur, loc.get("country"), loc.get("city"), loc.get("street"),
                                                     loc.get("latitude"), loc.get("longitude"), loc.get("zip"))

                store_event(cur,
                    page_id,
                    event["id"],
                    event["name"],
                    event["description"],
                    event["start_time"],
                    place_name,
                    loc_id
                )
            except psycopg2.Error as err:
                ERROR("err storing data: %s" % str(err))
                conn.rollback()
            else:
                conn.commit()

    conn.close()

