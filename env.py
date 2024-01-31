import datetime
import os

from dotenv import load_dotenv

load_dotenv()

db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

for item in ["DB_USERNAME", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]:
    if os.getenv(item) is None:
        print(f"missing env: {item}")
        exit(1)

min_year = os.getenv("MIN_YEAR")
max_year = os.getenv("MAX_YEAR")
if min_year is None:
    min_year = 2016
if max_year is None:
    max_year = datetime.datetime.now().year
