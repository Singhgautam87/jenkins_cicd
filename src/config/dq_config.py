"""
Data Quality (Deequ) configuration.
Defines what checks to run and their thresholds.
"""
from typing import List, Dict

# Data quality check levels
DQ_CHECK_LEVELS = {
    "error": "Error",  # Fail pipeline if check fails
    "warning": "Warning",  # Log but continue
}

# Bookings DQ checks configuration
BOOKINGS_DQ_CHECKS: List[Dict] = [
    {
        "name": "bookings_not_empty",
        "type": "hasSize",
        "condition": lambda s: s > 0,
        "message": "Bookings table should not be empty",
        "level": "warning",
    },
    {
        "name": "booking_id_complete",
        "type": "isComplete",
        "field": "booking_id",
        "level": "error",
    },
    {
        "name": "customer_id_complete",
        "type": "isComplete",
        "field": "customer_id",
        "level": "error",
    },
    {
        "name": "booking_status_valid",
        "type": "isContainedIn",
        "field": "booking_status",
        "allowed_values": ["created", "in_progress", "completed", "cancelled"],
        "level": "error",
    },
    {
        "name": "booking_duration_non_negative",
        "type": "isNonNegative",
        "field": "booking_duration_minutes",
        "hint": "Duration should be >= 0",
        "level": "warning",
    },
]

# Customers DQ checks configuration
CUSTOMERS_DQ_CHECKS: List[Dict] = [
    {
        "name": "customers_not_empty",
        "type": "hasSize",
        "condition": lambda s: s > 0,
        "message": "Customers table should not be empty",
        "level": "warning",
    },
    {
        "name": "customer_id_complete",
        "type": "isComplete",
        "field": "customer_id",
        "level": "error",
    },
    {
        "name": "email_complete",
        "type": "isComplete",
        "field": "email",
        "level": "error",
    },
    {
        "name": "email_valid_format",
        "type": "matchesPattern",
        "field": "email",
        "pattern": r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        "level": "error",
    },
]

# DQ reporting configuration
DQ_REPORTING = {
    "generate_html": True,
    "include_summary_stats": True,
    "include_failed_checks": True,
    "report_path": "reports/data_quality_dashboard.html",
}
