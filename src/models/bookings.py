"""
Bookings data model and processing logic.
Handles all booking-related validations and transformations.
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from ..config.business_rules import VALID_BOOKING_STATUSES


def validate_booking(df: DataFrame) -> DataFrame:
    """
    Validate bookings data.
    Drops records without booking_id or customer_id, validates dates and status.
    """
    # Must have booking_id and customer_id
    df = df.dropna(subset=["booking_id", "customer_id"])
    
    # Parse booking date - if parsing fails, row will be null and we filter it out
    df = df.withColumn("booking_date_parsed", F.to_date("booking_date", "yyyy-MM-dd"))
    df = df.filter(F.col("booking_date_parsed").isNotNull())
    
    # Only allow valid statuses (case-insensitive check)
    df = df.filter(F.lower(F.col("booking_status")).isin([s.lower() for s in VALID_BOOKING_STATUSES]))
    
    return df


def transform_booking(df: DataFrame) -> DataFrame:
    """
    Transform bookings: calculate duration in minutes.
    Note: Negative durations will be null (end_time < start_time is invalid)
    """
    df = df.withColumn("start_ts", F.to_timestamp("start_time"))
    df = df.withColumn("end_ts", F.to_timestamp("end_time"))
    
    # Calculate duration in minutes
    # Using unix_timestamp for reliable subtraction
    df = df.withColumn(
        "booking_duration_minutes",
        (F.unix_timestamp("end_ts") - F.unix_timestamp("start_ts")) / 60.0,
    )
    
    # TODO: Maybe filter out negative durations? For now keeping them as null
    return df


def get_booking_columns() -> list:
    """Get list of booking columns."""
    return [
        "booking_id",
        "customer_id",
        "start_time",
        "end_time",
        "booking_status",
        "booking_date_parsed",
        "car_type",
        "pickup_city",
    ]
