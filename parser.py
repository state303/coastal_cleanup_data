import datetime
import math
from typing import *

import pandas as pd
from pandas import Series

from utils import *

FILE_FMT = "coastalcleanupdata_{}.csv"


class ParseResult:
    id: int
    litters: List[Tuple[Hashable, float]]
    state: str
    country: str
    zone: str
    environment: str
    cleanup_group: str
    cleanup_type: str
    adult: int
    children: int
    kilograms: float
    distance: float
    area: float
    cleaned_at: datetime.datetime
    latitude: float
    longitude: float

    def __init__(self):
        self.litters = list()

    def __getitem__(self, field):
        return self.__dict__[field]

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)


KNOWN_KEYS = ['GPS',
              'Cleanup ID',
              'Zone',
              'State',
              'Country',
              'Environment',
              'Cleanup Type',
              'Cleanup Date',
              'Group Name',
              'Adults',
              'Children',
              'Area km',
              'Kilograms',
              'Distance km',
              'People',
              'Total Items Collected']
KNOWN_KEYS_SET = set()

for key in KNOWN_KEYS:
    KNOWN_KEYS_SET.add(key)


def is_litter_item(k: any):
    return k not in KNOWN_KEYS_SET


def is_valid_result(result: ParseResult):
    if result.id is None:
        return False
    if result.country is None:
        return False
    if result.latitude is None or result.longitude is None:
        return False
    if result.adult is None and result.children is None:
        return False
    if result.cleaned_at is None:
        return False
    return True


def parse_row(v: Series) -> ParseResult | None:
    if not __is_valid_gps__(v.get('GPS')):
        return None
    result = ParseResult()
    result.id = parse_value(v.get('Cleanup ID'))
    result.zone = parse_value(v.get('Zone'))
    result.state = parse_value(v.get('State'))
    result.country = parse_value(v.get('Country'))
    result.latitude, result.longitude = __parse_gps__(v.get('GPS'))
    result.cleanup_type = parse_value(v.get('Cleanup Type'))
    result.environment = parse_value(v.get('Environment'))
    result.cleaned_at = __parse_date__(v.get('Cleanup Date'))
    result.cleanup_group = parse_value(v.get('Group Name'))
    result.adult = parse_value(v.get('Adults'))
    result.children = parse_value(v.get('Children'))
    result.kilograms = parse_value(v.get('Kilograms'))
    result.distance = parse_value(v.get('Distance km'))
    result.area = parse_value(v.get('Area km'))
    for key_name, val in v.items():
        if is_litter_item(key_name):
            if isinstance(v, float) and math.isnan(v):
                result.litters.append((key_name, 0.0))
            else:
                result.litters.append((key_name, val))
    if is_valid_result(result):
        return result
    else:
        return None


def parse(year: int) -> List[ParseResult]:
    parse_result = []
    invalid_item_count = 0
    valid_item_count = 0

    filepath = FILE_FMT.format(year)
    reader = pd.read_csv(filepath, low_memory=False)
    for _, v in reader.iterrows():
        result = parse_row(v)
        if result is not None:
            valid_item_count += 1
            parse_result.append(result)
        else:
            invalid_item_count += 1
    return parse_result


def __parse_date__(date: any) -> datetime.datetime | None:
    if isinstance(date, float) and math.isnan(date):
        return None
    if isinstance(date, float):
        return None
    try:
        return datetime.datetime.fromisoformat(date)
    except Exception as e:
        print("failed to parse invalid date {}: ".format(date, e))
        return None


def parse_value(value: any):
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def __is_valid_gps__(src: str) -> bool:
    if isinstance(src, float):
        return False
    if src is None or len(src) == 0:
        return False
    return True


def __parse_gps__(src: str) -> Tuple[float, float]:
    s = src.strip()
    v = s.split(', ')
    return float(v[0]), float(v[1])
