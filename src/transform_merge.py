from datetime import datetime

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .config import paths as config
from .config.business_rules import DEDUP_RULES
from .models import bookings as booking_model
from .models import customers as customer_model
from .utils import create_spark


def transform_bookings(df: DataFrame) -> DataFrame:
    """Transform bookings using model logic."""
    return booking_model.transform_booking(df)


def transform_customers(df: DataFrame, run_date: datetime) -> DataFrame:
    """Transform customers using model logic."""
    return customer_model.transform_customer(df, run_date)


def read_if_exists(spark, path: str) -> DataFrame | None:
    try:
        return spark.read.parquet(path)
    except Exception:
        return None


def merge_bookings(spark) -> None:
    """
    Merge staging bookings into final table.
    Logic: Remove cancelled, keep latest record per booking_id
    """
    staging = read_if_exists(spark, config.BOOKINGS_STAGING_PATH)
    if staging is None:
        print("No staging bookings found, skipping merge")
        return

    staging = transform_bookings(staging)
    print(f"Staging bookings count: {staging.count()}")

    existing = read_if_exists(spark, config.BOOKINGS_FINAL_PATH)
    if existing is None:
        combined = staging
        print("No existing bookings, using staging as final")
    else:
        combined = existing.unionByName(staging)
        print(f"Combined count: {combined.count()}")

    # Business rule: cancelled bookings should be removed from final table
    filtered = combined.filter(F.lower(F.col("booking_status")) != "cancelled")
    print(f"After removing cancelled: {filtered.count()}")

    # Deduplicate: if same booking_id appears multiple times, keep the latest one
    # Using config from business_rules
    dedup_rule = DEDUP_RULES["bookings"]
    order_col = dedup_rule["order_by"]
    order_dir = dedup_rule["order_direction"]
    
    w = Window.partitionBy(dedup_rule["key"]).orderBy(
        F.col(order_col).desc() if order_dir == "desc" else F.col(order_col).asc()
    )
    deduped = filtered.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")
    
    print(f"Final bookings count: {deduped.count()}")
    deduped.write.mode("overwrite").parquet(config.BOOKINGS_FINAL_PATH)
    print("✅ Bookings merge completed")


def merge_customers(spark, run_date: datetime) -> None:
    """
    Merge staging customers into final table.
    Upsert logic: if customer_id exists, keep the one with latest signup_date
    """
    staging = read_if_exists(spark, config.CUSTOMERS_STAGING_PATH)
    if staging is None:
        print("No staging customers found, skipping merge")
        return

    staging = transform_customers(staging, run_date)
    print(f"Staging customers count: {staging.count()}")

    existing = read_if_exists(spark, config.CUSTOMERS_FINAL_PATH)
    if existing is None:
        combined = staging
    else:
        combined = existing.unionByName(staging)

    # Upsert: keep latest customer record based on signup_date
    # This handles cases where customer info gets updated
    # Using config from business_rules
    dedup_rule = DEDUP_RULES["customers"]
    order_col = dedup_rule["order_by"]
    order_dir = dedup_rule["order_direction"]
    
    w = Window.partitionBy(dedup_rule["key"]).orderBy(
        F.col(order_col).desc() if order_dir == "desc" else F.col(order_col).asc()
    )
    deduped = combined.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")
    
    print(f"Final customers count: {deduped.count()}")
    deduped.write.mode("overwrite").parquet(config.CUSTOMERS_FINAL_PATH)
    print("✅ Customers merge completed")


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

