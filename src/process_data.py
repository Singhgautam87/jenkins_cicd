from datetime import datetime

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    TimestampType,
)

from . import config
from .utils import create_spark, is_valid_email, normalize_customer_status


BOOKING_STATUSES = ["created", "in_progress", "completed", "cancelled"]


def get_raw_schema() -> StructType:
    """
    Schema for the single daily JSON file (bookings + customers).
    """
    return StructType(
        [
            StructField("booking_id", StringType(), True),
            StructField("customer_id", StringType(), True),
            StructField("start_time", StringType(), True),
            StructField("end_time", StringType(), True),
            StructField("booking_status", StringType(), True),
            StructField("booking_date", StringType(), True),
            StructField("car_type", StringType(), True),
            StructField("pickup_city", StringType(), True),
            StructField("customer_name", StringType(), True),
            StructField("email", StringType(), True),
            StructField("phone", StringType(), True),
            StructField("customer_status", StringType(), True),
            StructField("signup_date", StringType(), True),
        ]
    )


def read_raw_daily_file(spark, run_date: datetime) -> DataFrame:
    raw_path = config.get_raw_file_path(run_date)
    return spark.read.schema(get_raw_schema()).json(raw_path)


def validate_and_clean(df: DataFrame) -> DataFrame:
    """
    Apply validation and basic cleaning.
    """
    # Drop null keys
    df = df.dropna(subset=["booking_id", "customer_id"])

    # Parse dates
    df = df.withColumn("booking_date_parsed", F.to_date("booking_date", "yyyy-MM-dd"))
    df = df.withColumn("signup_date_parsed", F.to_date("signup_date", "yyyy-MM-dd"))

    df = df.filter(F.col("booking_date_parsed").isNotNull())
    df = df.filter(F.col("signup_date_parsed").isNotNull())

    # Enforce valid booking statuses
    df = df.filter(F.lower(F.col("booking_status")).isin([s.lower() for s in BOOKING_STATUSES]))

    # Email validation via UDF
    is_valid_email_udf = F.udf(is_valid_email)
    df = df.withColumn("email_valid", is_valid_email_udf("email"))
    df = df.filter(F.col("email_valid") == F.lit(True)).drop("email_valid")

    # Standardize customer status
    normalize_status_udf = F.udf(normalize_customer_status)
    df = df.withColumn("customer_status_std", normalize_status_udf("customer_status"))

    return df


def split_into_staging(df: DataFrame) -> tuple[DataFrame, DataFrame]:
    """
    Split unified dataset into bookings and customers staging DataFrames.
    """
    bookings_cols = [
        "booking_id",
        "customer_id",
        "start_time",
        "end_time",
        "booking_status",
        "booking_date_parsed",
        "car_type",
        "pickup_city",
    ]
    customers_cols = [
        "customer_id",
        "customer_name",
        "email",
        "phone",
        "customer_status_std",
        "signup_date_parsed",
    ]

    bookings_df = df.select(*bookings_cols)
    customers_df = df.select(*customers_cols).dropDuplicates(["customer_id"])

    return bookings_df, customers_df


def write_staging(bookings_df: DataFrame, customers_df: DataFrame) -> None:
    bookings_df.write.mode("append").parquet(config.BOOKINGS_STAGING_PATH)
    customers_df.write.mode("append").parquet(config.CUSTOMERS_STAGING_PATH)


def run_process_daily(run_date: datetime) -> None:
    spark = create_spark("ZoomCar-Process-Daily")
    try:
        raw_df = read_raw_daily_file(spark, run_date)
        cleaned_df = validate_and_clean(raw_df)
        bookings_df, customers_df = split_into_staging(cleaned_df)
        write_staging(bookings_df, customers_df)
    finally:
        spark.stop()


if __name__ == "__main__":
    # Simple manual test hook
    from .utils import parse_run_date
    import sys

    run_date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_dt = parse_run_date(run_date_arg)
    run_process_daily(run_dt)

