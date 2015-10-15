#!/usr/bin/python3

import logging
import psycopg2
import requests
import sys

from common import get_config, get_pages, db_string, ERROR

log = logging.getLogger("kdyprednaska.fetch")
log.setLevel(logging.INFO)
logging.basicConfig(format="%(levelname)s %(message)s")

def fetch_page(page_id, token):
    url = "https://graph.facebook.com/{version}/{page_id}?fields={fields}&access_token={token}".format(
        version="v2.5",
        page_id=page_id,
        token=token,
        fields = ",".join([
            "about",
            "emails",
            "link",
            "location",
            "likes",
            "name",
            "username",
            "website",
            "picture",
        ])
    )

    log.info("fetching page, page=%s", page_id)
    log.debug("fetching page, page=%s, url=%s", page_id, url)

    return requests.get(url)

def fetch_events(page_id, token):
    url = "https://graph.facebook.com/{version}/{page_id}/events?access_token={token}&fields={fields}".format(
        version="v2.5",
        page_id=page_id,
        token=token,
        fields=",".join([
           "id",
           "name",
           "type",
           "start_time",
           "end_time",
           "place",
           "attending_count",
           "maybe_count",
           "declined_count",
           "noreply_count",
        ])
    )

    return requests.get(url)

def store_page(cur, page_id, page):
    cur.execute("select page_id from pages where page_id = %s",
        (page_id, )
    )

    page["email"] = None
    if "emails" in page and page["emails"]:
        page["email"] = page["emails"][0]

    page["page_id"] = page_id
    page["picture"] = page["picture"]["data"]["url"]

    fields = [
        "page_id",
        "about",
        "email",
        "link",
        "likes",
        "name",
        "username",
        "website",
        "picture",
    ]

    exists = cur.fetchone()
    if not exists:
        cur.execute("""insert into pages ("""
                + ",".join(fields) + """)
                       values (%s, %s, %s,
                               %s, %s, %s,
                               %s, %s, %s)""",
            [page.get(field) for field in fields]
        )
        log.info("stored page, id=%s", page_id)


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

        log.info("stored location, id=%s, country=%s, city=%s, street=%s", location_id, country, city, street)

    return location_id

def store_event(cur, event):
    cur.execute("select exists (select 1 from events where fb_id = %s)", (event["fb_id"], ))
    exists = cur.fetchone()[0]

    fields = [
        "page_id",
        "fb_id",
        "name",
        "start_time",
        "end_time",
        "event_type",
        "place_name",
        "location_id",
        "attending_count",
        "maybe_count",
        "declined_count",
        "noreply_count",
    ]

    if not exists:
        cur.execute("""insert into events ("""
                      + ",".join(fields) + """)
                     values (%s, %s, %s, %s,
                             %s, %s, %s, %s,
                             %s, %s, %s, %s)""",
            [event.get(field) for field in fields]
        )
        log.info("stored event, page=%s, fb_id=%s",
            event["page_id"], event["fb_id"]
        )


if __name__ == "__main__":
    config = get_config()
    dbstring = db_string(config)

    token = config.get("facebook", "token")
    pages_f = config.get("facebook", "pages")
    pages = get_pages(pages_f)

    conn = psycopg2.connect(dbstring)
    cur = conn.cursor()

    log.info("processing pages, pages=%s", pages)

    for page_id in pages:
        r = fetch_page(page_id, token)
        if r.status_code != 200:
            ERROR("could not retrieve page, page=%s, err=%s" % (page_id, r.status_code))
            continue

        page = r.json()
        try:
            store_page(cur, page_id, page)
        except psycopg2.Error as err:
            conn.rollback()
            ERROR("error storing page: %s" % str(err))
            continue
        else:
            conn.commit()


        r = fetch_events(page_id, token)
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
                        loc_id = store_location(cur,
                                loc.get("country"),
                                loc.get("city"),
                                loc.get("street"),
                                loc.get("latitude"),
                                loc.get("longitude"),
                                loc.get("zip"))

                event["page_id"] = page_id
                event["fb_id"] = event["id"]
                event["place_name"] = place_name
                event["location_id"] = loc_id
                event["event_type"] = event.get("type")

                store_event(cur, event)
            except psycopg2.Error as err:
                conn.rollback()
                ERROR("error storing events: %s" % str(err))
                continue
            else:
                conn.commit()

    conn.close()

