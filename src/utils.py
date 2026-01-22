"""
Legacy utils module - re-exports from organized utils modules for backward compatibility.
"""
from .utils.spark_utils import create_spark
from .utils.validators import (
    is_valid_email,
    normalize_phone_to_indian,
    normalize_customer_status,
)
from .utils.date_utils import parse_run_date, parse_date_safe

__all__ = [
    "create_spark",
    "is_valid_email",
    "normalize_phone_to_indian",
    "normalize_customer_status",
    "parse_run_date",
    "parse_date_safe",
]
