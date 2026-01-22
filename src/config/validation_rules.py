"""
Data validation rules and schemas.
These define what constitutes valid data in our system.
"""
import re
from typing import List, Pattern

# Email validation regex
EMAIL_REGEX: Pattern = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

# Required fields for each entity
REQUIRED_FIELDS = {
    "bookings": ["booking_id", "customer_id", "booking_date", "booking_status"],
    "customers": ["customer_id", "customer_name", "email"],
}

# Fields that cannot be null
NOT_NULL_FIELDS = {
    "bookings": ["booking_id", "customer_id", "booking_status"],
    "customers": ["customer_id", "customer_name", "email"],
}

# Field length constraints
FIELD_LENGTHS = {
    "booking_id": {"max": 50},
    "customer_id": {"max": 50},
    "customer_name": {"max": 200},
    "email": {"max": 200},
    "phone": {"max": 20},
    "booking_status": {"max": 20},
    "car_type": {"max": 50},
    "pickup_city": {"max": 100},
}

# Data type validations
VALIDATION_PATTERNS = {
    "email": EMAIL_REGEX,
    "phone_indian": re.compile(r"^\+91[6-9]\d{9}$"),  # Indian mobile format
    "booking_id": re.compile(r"^[A-Z0-9_-]+$"),  # Alphanumeric with dashes/underscores
    "customer_id": re.compile(r"^[A-Z0-9_-]+$"),
}

# Business validation rules
BUSINESS_VALIDATIONS = {
    "booking_duration": {
        "min_minutes": 0,
        "max_minutes": 10080,  # 7 days
    },
    "booking_date": {
        "min_date": "2020-01-01",  # No bookings before this
        "max_date_offset_days": 30,  # No bookings more than 30 days in future
    },
    "customer_tenure": {
        "min_days": 0,
        "max_days": 3650,  # 10 years max
    },
}
