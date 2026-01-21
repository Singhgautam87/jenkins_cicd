import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_raw_dir() -> str:
    return os.path.join(BASE_DIR, "data", "raw")


def get_staging_dir() -> str:
    return os.path.join(BASE_DIR, "data", "staging")


def get_final_dir() -> str:
    return os.path.join(BASE_DIR, "data", "final")


def build_raw_filename(run_date: datetime) -> str:
    """
    Build the expected raw JSON file name for a given run date.
    Pattern: zoom_car_events_yyyymmdd.json
    """
    date_str = run_date.strftime("%Y%m%d")
    return f"zoom_car_events_{date_str}.json"


def get_raw_file_path(run_date: datetime) -> str:
    return os.path.join(get_raw_dir(), build_raw_filename(run_date))


BOOKINGS_STAGING_PATH = os.path.join(get_staging_dir(), "bookings")
CUSTOMERS_STAGING_PATH = os.path.join(get_staging_dir(), "customers")

BOOKINGS_FINAL_PATH = os.path.join(get_final_dir(), "bookings")
CUSTOMERS_FINAL_PATH = os.path.join(get_final_dir(), "customers")

