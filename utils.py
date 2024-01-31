import os
from datetime import datetime
from typing import LiteralString

from dotenv import load_dotenv


def missing(item):
    if item is None:
        return True
    if type(item) is str and len(item) == 0:
        return True
    return False


def read_credentials() -> (str, str):
    if not load_dotenv():
        print("missing .env")
    username, password = os.getenv("USERNAME"), os.getenv("PASSWORD")
    if missing(username):
        print("missing username")
        exit(1)
    if missing(password):
        print("missing password")
        exit(1)
    return username, password


def get_year_range() -> (int, int):
    initial_year = 2016
    if not missing(os.getenv("INITIAL_YEAR")):
        initial_year = int(os.getenv("INITIAL_YEAR"))
    return initial_year, get_current_year()


def find(name, path) -> LiteralString | str | bytes | None:
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    print("could not find file:", name)
    return None


def get_current_year() -> int:
    return datetime.now().year


