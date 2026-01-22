"""
Business rules and domain-specific configurations.
These are business logic constants that might change based on requirements.
"""
from typing import List

# Booking statuses - these are the valid states in our system
VALID_BOOKING_STATUSES: List[str] = ["created", "in_progress", "completed", "cancelled"]

# Customer status mappings - how we normalize various input formats
CUSTOMER_STATUS_MAPPING: dict = {
    "active": ["active", "act", "a"],
    "inactive": ["inactive", "inact", "i"],
    "blocked": ["blocked", "block", "b", "banned"],
}

# Data quality thresholds
DQ_THRESHOLDS = {
    "min_booking_duration_minutes": 0,  # Negative durations are invalid
    "max_booking_duration_hours": 168,  # 7 days max
    "min_customer_tenure_days": 0,
    "max_email_length": 200,
    "max_phone_length": 20,
}

# Date formats we accept
DATE_FORMATS = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"]  # Primary format first
TIMESTAMP_FORMATS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"]

# Phone number normalization rules
PHONE_NORMALIZATION = {
    "country_code": "+91",  # India
    "min_digits": 10,
    "max_digits": 12,
    "remove_chars": [" ", "-", "(", ")", "+"],  # Characters to strip
}

# Data retention policies (in days)
RETENTION_POLICIES = {
    "raw_data": 90,  # Keep raw JSON for 90 days
    "staging_data": 30,  # Staging data for 30 days
    "final_data": 365,  # Final data for 1 year
}

# Processing batch sizes
BATCH_SIZES = {
    "kafka_max_messages": 1000,
    "postgres_batch_size": 500,  # Rows per batch when writing to PostgreSQL
    "spark_partitions": 4,
}

# Deduplication rules
DEDUP_RULES = {
    "bookings": {
        "key": "booking_id",
        "order_by": "booking_date_parsed",
        "order_direction": "desc",  # Keep latest
    },
    "customers": {
        "key": "customer_id",
        "order_by": "signup_date_parsed",
        "order_direction": "desc",  # Keep latest
    },
}
