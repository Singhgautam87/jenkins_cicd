from datetime import datetime

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from . import config
from .utils import create_spark, normalize_phone_to_indian


def transform_bookings(df: DataFrame) -> DataFrame:
    df = df.withColumn("start_ts", F.to_timestamp("start_time"))
    df = df.withColumn("end_ts", F.to_timestamp("end_time"))
    df = df.withColumn(
        "booking_duration_minutes",
        (F.unix_timestamp("end_ts") - F.unix_timestamp("start_ts")) / 60.0,
    )
    return df


def transform_customers(df: DataFrame, run_date: datetime) -> DataFrame:
    normalize_phone_udf = F.udf(normalize_phone_to_indian)

    df = df.withColumn("phone_norm", normalize_phone_udf("phone"))
    df = df.withColumn(
        "customer_tenure_days",
        F.datediff(F.lit(run_date.date()), F.col("signup_date_parsed")),
    )
    return df


def read_if_exists(spark, path: str) -> DataFrame | None:
    try:
        return spark.read.parquet(path)
    except Exception:
        return None


def merge_bookings(spark) -> None:
    staging = read_if_exists(spark, config.BOOKINGS_STAGING_PATH)
    if staging is None:
        return

    staging = transform_bookings(staging)

    existing = read_if_exists(spark, config.BOOKINGS_FINAL_PATH)
    if existing is None:
        combined = staging
    else:
        combined = existing.unionByName(staging)

    # Simulate Delta merge:
    # - Remove cancelled bookings
    # - Deduplicate on booking_id keeping the latest booking_date_parsed
    filtered = combined.filter(F.lower(F.col("booking_status")) != "cancelled")

    w = Window.partitionBy("booking_id").orderBy(F.col("booking_date_parsed").desc())
    deduped = filtered.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")

    deduped.write.mode("overwrite").parquet(config.BOOKINGS_FINAL_PATH)


def merge_customers(spark, run_date: datetime) -> None:
    staging = read_if_exists(spark, config.CUSTOMERS_STAGING_PATH)
    if staging is None:
        return

    staging = transform_customers(staging, run_date)

    existing = read_if_exists(spark, config.CUSTOMERS_FINAL_PATH)
    if existing is None:
        combined = staging
    else:
        combined = existing.unionByName(staging)

    # Upsert on customer_id: keep latest signup_date_parsed
    w = Window.partitionBy("customer_id").orderBy(F.col("signup_date_parsed").desc())
    deduped = combined.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")

    deduped.write.mode("overwrite").parquet(config.CUSTOMERS_FINAL_PATH)


def run_transform_and_merge(run_date: datetime) -> None:
    spark = create_spark("ZoomCar-Transform-Merge")
    try:
        merge_bookings(spark)
        merge_customers(spark, run_date)
    finally:
        spark.stop()


if __name__ == "__main__":
    from .utils import parse_run_date
    import sys

    run_date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_dt = parse_run_date(run_date_arg)
    run_transform_and_merge(run_dt)

