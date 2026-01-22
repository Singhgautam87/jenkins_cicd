from datetime import datetime

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
)

from .config import paths as config
from .models import bookings as booking_model
from .models import customers as customer_model
from .utils import create_spark


def get_raw_schema() -> StructType:
    """
    Schema for the single daily JSON file (bookings + customers).
    Note: Keeping all fields nullable=True because source data can be messy
    """
    return StructType(
        [
            StructField("booking_id", StringType(), True),
            StructField("customer_id", StringType(), True),
            StructField("start_time", StringType(), True),  # Will parse to timestamp later
            StructField("end_time", StringType(), True),
            StructField("booking_status", StringType(), True),
            StructField("booking_date", StringType(), True),  # Format: YYYY-MM-DD
            StructField("car_type", StringType(), True),
            StructField("pickup_city", StringType(), True),
            StructField("customer_name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("phone", StringType(), True),  # Can be in various formats
            StructField("customer_status", StringType(), True),  # Will normalize later
            StructField("signup_date", StringType(), True),
        ]
    )


def read_raw_daily_file(spark, run_date: datetime) -> DataFrame:
    """
    Read the daily JSON file. 
    TODO: Add retry logic if file doesn't exist immediately
    """
    raw_path = config.get_raw_file_path(run_date)
    # print(f"Reading from: {raw_path}")  # Debug line, commented out
    return spark.read.schema(get_raw_schema()).json(raw_path)


def validate_and_clean(df: DataFrame) -> DataFrame:
    """Apply validation and basic cleaning using model validators."""
    # Validate both bookings and customers
    df = booking_model.validate_booking(df)
    df = customer_model.validate_customer(df)
    return df


def validate_and_clean_bookings(df: DataFrame) -> DataFrame:
    """Validate and clean bookings data."""
    df = booking_model.validate_booking(df)
    return df.select(*[c for c in booking_model.get_booking_columns() if c in df.columns])


def validate_and_clean_customers(df: DataFrame) -> DataFrame:
    """Validate and clean customers data."""
    df = customer_model.validate_customer(df)
    return df.select(*[c for c in customer_model.get_customer_columns() if c in df.columns]).dropDuplicates(["customer_id"])


def split_into_staging(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """Split unified dataset into bookings and customers staging DataFrames."""
    bookings_df = df.select(*[c for c in booking_model.get_booking_columns() if c in df.columns])
    customers_df = df.select(*[c for c in customer_model.get_customer_columns() if c in df.columns]).dropDuplicates(["customer_id"])
    return bookings_df, customers_df


def write_staging(bookings_df: DataFrame, customers_df: DataFrame) -> None:
    bookings_df.write.mode("append").parquet(config.BOOKINGS_STAGING_PATH)
    customers_df.write.mode("append").parquet(config.CUSTOMERS_STAGING_PATH)


def run_process_daily(run_date: datetime) -> None:
    """
    Main processing function for daily batch.
    This is the entry point for batch mode processing.
    """
    spark = create_spark("ZoomCar-Process-Daily")
    try:
        print(f"Processing data for date: {run_date.strftime('%Y-%m-%d')}")
        raw_df = read_raw_daily_file(spark, run_date)
        
        # Quick check - if empty, log and return
        if raw_df.count() == 0:
            print("⚠️ No data found for this date")
            return
        
        cleaned_df = validate_and_clean(raw_df)
        bookings_df, customers_df = split_into_staging(cleaned_df)
        
        # Log counts for debugging
        print(f"Bookings: {bookings_df.count()}, Customers: {customers_df.count()}")
        
        write_staging(bookings_df, customers_df)
        print("✅ Staging write completed")
    except Exception as e:
        print(f"❌ Error in run_process_daily: {e}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    # Simple manual test hook
    from .utils import parse_run_date
    import sys

    run_date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_dt = parse_run_date(run_date_arg)
    run_process_daily(run_dt)

