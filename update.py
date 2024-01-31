import math
from typing import List

import psycopg2
import psycopg2.extras

from env import *
from parser import ParseResult

keys = ['country', 'zone', 'state', 'cleanup_group', 'cleanup_type', 'environment', 'litter']

cache = {}

for key in keys:
    cache[key] = {}


def is_present(entry: any):
    if entry is None:
        return False
    if isinstance(entry, str) and len(entry) == 0:
        return False
    if isinstance(entry, float) and math.isnan(entry):
        return False
    return True


def get_update_sql(table: str, values: List[str]):
    insertion_values = ""
    values_size = len(values)

    for i in range(values_size):
        if values[i] is None:
            continue
        escaped = values[i].replace("'", "''")
        insertion_values += f"('{escaped}')"
        if i + 1 < values_size:
            insertion_values += ","

    return (f"INSERT INTO {table}(name) VALUES {insertion_values} "
            f"ON CONFLICT (name) DO UPDATE SET name = excluded.name "
            f"RETURNING id;")


def none_or_value(k: str, res: ParseResult):
    try:
        if res[k] is None:
            return None
        if res[k] in cache[k]:
            return cache[k][res[k]]
        return None
    except Exception as e:
        print(f"failed to execute none_or_value with param k:{k}, res: {res}. error: {e}")


def zero_or_value(v: any):
    try:
        if v is None:
            return 0.0
        return v
    except Exception as e:
        print(f"failed to execute zero_or_value with item: {v}")
        raise e


def insert_cleanup_actions(results: List[ParseResult], cursor) -> int:
    cnt = 0

    values = []

    for result in results:
        zone_id = none_or_value("zone", result)
        country_id = none_or_value("country", result)
        state_id = none_or_value("state", result)
        cleanup_group_id = none_or_value("cleanup_group", result)
        environment_id = none_or_value("environment", result)
        cleanup_type_id = none_or_value("cleanup_type", result)
        result.adult = zero_or_value(result.adult)
        result.children = zero_or_value(result.children)
        result.distance = zero_or_value(result.distance)
        result.kilograms = zero_or_value(result.kilograms)
        result.area = zero_or_value(result.area)
        values.append(
            (result.id, result.latitude, result.longitude,
             result.cleaned_at, result.adult, result.children,
             result.kilograms, result.distance, result.area,
             zone_id, country_id, state_id,
             cleanup_group_id, environment_id, cleanup_type_id)
        )
        cnt += 1

    sql = (
        f"INSERT INTO cleanup(id, latitude, longitude, cleaned_at, adult, child, kilograms, distance, area, zone_id, country_id, state_id, cleanup_group_id, environment_id, cleanup_type_id) "
        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        f"ON CONFLICT (id) "
        f"DO UPDATE SET "
        f"latitude = excluded.latitude, "
        f"longitude = excluded.longitude, "
        f"cleaned_at = excluded.cleaned_at, "
        f"adult = excluded.adult, "
        f"child = excluded.child, "
        f"kilograms = excluded.kilograms, "
        f"distance = excluded.distance, "
        f"area = excluded.area, "
        f"zone_id = excluded.zone_id, "
        f"country_id = excluded.country_id, "
        f"state_id = excluded.state_id, "
        f"cleanup_group_id = excluded.cleanup_group_id, "
        f"environment_id = excluded.environment_id, "
        f"cleanup_type_id = excluded.cleanup_type_id;")
    psycopg2.extras.execute_batch(cursor, sql, values, cnt)
    return cnt


def insert_cleanup_litters(results: List[ParseResult], cursor) -> int:
    updated_count = 0
    values = []

    for result in results:
        for name, count in result.litters:
            if math.isnan(count):
                count = 0
            values.append((cache['litter'][name], result.id, count))
            updated_count += 1

    sql = (f"INSERT INTO cleanup_litter(litter_id, cleanup_id, count) "
           f"VALUES (%s, %s, %s) "
           f"ON CONFLICT ON CONSTRAINT pk__cleanup_litter__litter_id_cleanup_id "
           f"DO UPDATE SET count = excluded.count;")

    psycopg2.extras.execute_batch(cursor, sql, values, updated_count)
    return updated_count


def get_upsert_sql_by_tablename(table_name: str) -> str:
    return (f"INSERT INTO {table_name} (name) "
            f"VALUES (%s) "
            f"ON CONFLICT (name) DO NOTHING;")


def run(items: List[ParseResult]):
    updates = {}
    for k in keys:
        updates[k] = set()

    print("updates initialized")

    for entry in items:
        for k in keys:
            if k == 'litter':  # skip litter as we will treat them later on
                continue
            v = entry[k]
            if v is None:
                continue
            if v not in cache[k]:
                updates[k].add(v)

        # handle litters
        for name, count in entry.litters:
            if name not in cache['litter']:
                updates['litter'].add(name)

    with psycopg2.connect(dbname=db_name, user=db_username, password=db_password, host=db_host, port=db_port) as conn:
        with conn.cursor() as cursor:
            for k in keys:
                entry_vals = []
                for v in updates[k]:
                    entry_vals.append((v,))
                size = len(entry_vals)
                if size == 0:
                    print(f"no updates for entry {k}. skipping update...")
                    continue
                sql = get_upsert_sql_by_tablename(k)
                psycopg2.extras.execute_batch(cursor, sql, entry_vals, size)
                conn.commit()
                cursor.execute(f"SELECT * FROM {k}")
                rows = cursor.fetchall()
                for row in rows:
                    if row[0] is None or row[1] is None:
                        continue
                    cache[k][row[1]] = row[0]
                print(f"updated {size} {k} entries.")

            insert_cleanup_actions(items, cursor)
            conn.commit()
            print(f"updated {insert_cleanup_actions(items, cursor)} cleanup entries.")

            litter_count = insert_cleanup_litters(items, cursor)
            conn.commit()
            print(f"updated {litter_count} litter entries.")
