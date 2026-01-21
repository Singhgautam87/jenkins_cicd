import re
from datetime import datetime
from typing import Optional

from pyspark.sql import SparkSession


def create_spark(app_name: str = "ZoomCarPipeline") -> SparkSession:
    """
    Create a local Spark session suitable for running inside Docker.
    """
    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        # Add Deequ package for data quality checks
        .config("spark.jars.packages", "com.amazon.deequ:deequ:2.0.7-spark-3.3")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(email: Optional[str]) -> bool:
    if email is None:
        return False
    return EMAIL_REGEX.match(email) is not None


def normalize_customer_status(status: Optional[str]) -> Optional[str]:
    if status is None:
        return None
    s = status.strip().lower()
    if s in {"active", "act", "a"}:
        return "ACTIVE"
    if s in {"inactive", "inact", "i"}:
        return "INACTIVE"
    if s in {"blocked", "banned"}:
        return "BLOCKED"
    return status.upper()


def normalize_phone_to_indian(phone: Optional[str]) -> Optional[str]:
    """
    Very simple normalization:
    - keep only digits
    - if 10 digits -> assume Indian mobile and prefix with +91
    - if already starts with country code (e.g. 91XXXXXXXXXX) -> prefix '+' if missing
    """
    if phone is None:
        return None
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 10:
        return "+91" + digits
    if len(digits) == 12 and digits.startswith("91"):
        return "+" + digits
    return "+" + digits if digits else None


def parse_run_date(run_date_str: Optional[str]) -> datetime:
    """
    Accepts run_date as 'YYYY-MM-DD'. If None or empty, returns today's date.
    """
    if not run_date_str:
        return datetime.today()

    clean = run_date_str.strip()
    # Handle inputs like "RUN_DATE=2026-01-01"
    if "=" in clean:
        clean = clean.split("=", 1)[1].strip()

    return datetime.strptime(clean, "%Y-%m-%d")

