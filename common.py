import configparser
import glob
import sys

def ERROR(msg, *a, **k):
    print(msg, *a, file=sys.stderr, **k)

def get_config(main="config.ini", priv=glob.glob("*.priv.ini")):
    config = configparser.ConfigParser()
    config.readfp(open(main, "r"))
    config.read(priv)
    return config

def get_pages(pages_f="pages.txt"):
    with open(pages_f, "r") as f:
        return [page.strip() for page in f.readlines()]

def db_string(config):
    return "host={} dbname={} user={} password={}".format(
        config.get("database", "host"),
        config.get("database", "dbname"),
        config.get("database", "user"),
        config.get("database", "password")
    )

