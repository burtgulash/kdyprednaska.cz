import argparse
import configparser
import glob
import logging
import sys
import psycopg2

def get_logger():
    logging.basicConfig(format="%(levelname)s %(message)s")
    log = logging.getLogger("kdyprednaska.fetch")
    log.setLevel(logging.INFO)
    return log

log = get_logger()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c",
            action="store",
            dest="config",
            default="config.ini",
            help="config file")
    return parser.parse_args()

def get_config(filename):
    config = configparser.ConfigParser()
    config.readfp(open(filename, "r"))
    return config

def get_pages(pages_f="pages.txt"):
    with open(pages_f, "r") as f:
        return [page.strip() for page in f.readlines()]

def db_connect(dbstring):
    conn = None
    try:
        conn = psycopg2.connect(dbstring)
    except psycopg2.Error as err:
        log.error("could not connect to db: %s", err)
    return conn

def db_string(config):
    return "host={} dbname={} user={} password={}".format(
        config.get("database", "host"),
        config.get("database", "dbname"),
        config.get("database", "user"),
        config.get("database", "password")
    )

