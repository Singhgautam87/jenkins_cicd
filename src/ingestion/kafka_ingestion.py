"""
Real-time ingestion from Kafka, process and store in PostgreSQL.
"""
from sqlalchemy import text
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, DateType
import pandas as pd
from pyspark.sql.functions import from_json, col

from ..config.kafka_config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_RAW_EVENTS
from ..config.business_rules import BATCH_SIZES
from ..config.database import get_engine, init_schema
from ..process_data import get_raw_schema, validate_and_clean_bookings, validate_and_clean_customers
from ..transform_merge import transform_bookings, transform_customers
from ..utils import create_spark


def kafka_to_spark_df(spark: SparkSession, max_messages: int = None) -> tuple:
    """
    Read from Kafka and convert to Spark DataFrames.
    Note: Spark's Kafka connector reads in batches, not truly streaming here.
    For real streaming, would use readStream instead of read.
    """
    # Use configured batch size if not provided
    if max_messages is None:
        max_messages = BATCH_SIZES["kafka_max_messages"]
    
    print(f"Reading from Kafka topic: {KAFKA_TOPIC_RAW_EVENTS} (max: {max_messages} messages)")
    
    # Read from Kafka topic - using batch read for now
    # TODO: Consider switching to streaming for true real-time
    kafka_df = spark.read.format("kafka").option(
        "kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS
    ).option("subscribe", KAFKA_TOPIC_RAW_EVENTS).option(
        "startingOffsets", "earliest"
    ).option("endingOffsets", "latest").load()
    
    msg_count = kafka_df.count()
    print(f"Found {msg_count} messages in Kafka")
    
    if msg_count == 0:
        print("No messages in Kafka, returning empty DataFrames")
        return spark.createDataFrame([], get_raw_schema()), spark.createDataFrame([], get_raw_schema())
    
    # Parse JSON from Kafka value column
    schema = get_raw_schema()
    parsed_df = kafka_df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*").filter(
        col("booking_id").isNotNull() | col("customer_id").isNotNull()
    )
    
    print(f"Parsed {parsed_df.count()} valid records")
    
    # Split into bookings and customers
    bookings_df = validate_and_clean_bookings(parsed_df)
    customers_df = validate_and_clean_customers(parsed_df)
    
    return bookings_df, customers_df


def spark_to_postgres(df, table_name: str):
    """
    Write Spark DataFrame to PostgreSQL table with upsert logic.
    Converts to Pandas first (works for small-medium datasets).
    TODO: For large datasets, might need to use JDBC directly from Spark
    """
  
    
    row_count = df.count()
    if row_count == 0:
        print(f"⚠️ No data to write to {table_name}")
        return
    
    print(f"Converting {row_count} rows to Pandas for PostgreSQL write...")
    engine = get_engine()
    pandas_df = df.toPandas()
    
    # Map Spark column names to database column names
    if table_name == "bookings":
    # Remove the db_cols mapping completely
    # pandas_df = pandas_df[available_cols]
    # pandas_df = pandas_df.rename(columns=db_cols)
    
        # Direct write with proper column handling
        with engine.connect() as conn:
            for _, row in pandas_df.iterrows():
                row_dict = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
            
            # Make sure booking_date exists
                if 'booking_date' not in row_dict:
                    print(f"⚠️ Warning: booking_date missing in row: {row_dict}")
                    continue
                
                conn.execute(text("""
                    INSERT INTO bookings (
                        booking_id, customer_id, booking_date, booking_status,
                        start_time, end_time, booking_duration_minutes,
                        car_type, pickup_city
                    ) VALUES (
                        :booking_id, :customer_id, :booking_date, :booking_status,
                        :start_time, :end_time, :booking_duration_minutes,
                        :car_type, :pickup_city
                    )
                    ON CONFLICT (booking_id) DO UPDATE SET
                        customer_id = EXCLUDED.customer_id,
                        booking_status = EXCLUDED.booking_status,
                        start_time = EXCLUDED.start_time,
                        end_time = EXCLUDED.end_time,
                        booking_duration_minutes = EXCLUDED.booking_duration_minutes,
                        updated_at = CURRENT_TIMESTAMP
                """), row_dict)
            conn.commit()
        
        # Upsert using ON CONFLICT
        with engine.connect() as conn:
            for _, row in pandas_df.iterrows():
                # Handle NaN values (convert to None for SQL)
                row_dict = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
                conn.execute(text("""
                    INSERT INTO bookings (
                        booking_id, customer_id, booking_date, booking_status,
                        start_time, end_time, booking_duration_minutes,
                        car_type, pickup_city
                    ) VALUES (
                        :booking_id, :customer_id, :booking_date, :booking_status,
                        :start_time, :end_time, :booking_duration_minutes,
                        :car_type, :pickup_city
                    )
                    ON CONFLICT (booking_id) DO UPDATE SET
                        customer_id = EXCLUDED.customer_id,
                        booking_status = EXCLUDED.booking_status,
                        start_time = EXCLUDED.start_time,
                        end_time = EXCLUDED.end_time,
                        booking_duration_minutes = EXCLUDED.booking_duration_minutes,
                        updated_at = CURRENT_TIMESTAMP
                """), row_dict)
            conn.commit()
            
    elif table_name == "customers":
        db_cols = {
            'customer_id': 'customer_id',
            'customer_name': 'customer_name',
            'email': 'email',
            'phone': 'phone',
            'phone_norm': 'phone_norm',
            'customer_status_std': 'customer_status_std',
            'signup_date_parsed': 'signup_date',
            'customer_tenure_days': 'customer_tenure_days',
        }
        available_cols = [c for c in db_cols.keys() if c in pandas_df.columns]
        pandas_df = pandas_df[available_cols]
        pandas_df = pandas_df.rename(columns=db_cols)
        
        with engine.connect() as conn:
            for _, row in pandas_df.iterrows():
                row_dict = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
                conn.execute(text("""
                    INSERT INTO customers (
                        customer_id, customer_name, email, phone, phone_norm,
                        customer_status_std, signup_date, customer_tenure_days
                    ) VALUES (
                        :customer_id, :customer_name, :email, :phone, :phone_norm,
                        :customer_status_std, :signup_date, :customer_tenure_days
                    )
                    ON CONFLICT (customer_id) DO UPDATE SET
                        customer_name = EXCLUDED.customer_name,
                        email = EXCLUDED.email,
                        phone = EXCLUDED.phone,
                        phone_norm = EXCLUDED.phone_norm,
                        customer_status_std = EXCLUDED.customer_status_std,
                        updated_at = CURRENT_TIMESTAMP
                """), row_dict)
            conn.commit()
    else:
        raise ValueError(f"Unknown table name: {table_name}")
    
    print(f"✅ Successfully wrote {len(pandas_df)} rows to {table_name}")


def run_realtime_etl(spark: SparkSession, run_date: datetime):
    """
    Main real-time ETL: Kafka → Spark → PostgreSQL.
    This is the core function that orchestrates the entire real-time pipeline.
    """
    # Make sure database schema exists
    print("Initializing database schema...")
    init_schema()
    
    # Read from Kafka
    print("📥 Reading from Kafka...")
    bookings_df, customers_df = kafka_to_spark_df(spark, max_messages=1000)
    
    bookings_count = bookings_df.count()
    customers_count = customers_df.count()
    
    if bookings_count == 0 and customers_count == 0:
        print("⚠️ No new events from Kafka, nothing to process")
        return
    
    print(f"Processing {bookings_count} bookings and {customers_count} customers")
    
    # Apply transformations
    print("Applying transformations...")
    bookings_transformed = transform_bookings(bookings_df)
    customers_transformed = transform_customers(customers_df, run_date)
    
    # Write to PostgreSQL with upsert logic
    print("💾 Writing to PostgreSQL...")
    spark_to_postgres(bookings_transformed, "bookings")
    spark_to_postgres(customers_transformed, "customers")
    
    print("✅ Real-time ETL completed successfully")


if __name__ == "__main__":
    from ..utils import parse_run_date
    import sys
    
    run_date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run_dt = parse_run_date(run_date_arg)
    
    spark = create_spark("ZoomCar-Realtime-ETL")
    try:
        run_realtime_etl(spark, run_dt)
    finally:
        spark.stop()
