"""
Real-time ETL pipeline: Kafka → Spark → PostgreSQL
Main entry point for real-time data processing pipeline.
"""
import argparse
from datetime import datetime

from .utils import parse_run_date
from .ingestion.kafka_ingestion import run_realtime_etl
from .utils import create_spark


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Zoom Car Real-time ETL Pipeline")
    parser.add_argument(
        "--run-date",
        dest="run_date",
        type=str,
        required=False,
        help="Reference date in YYYY-MM-DD format. If omitted, uses today's date.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for real-time pipeline.
    Creates Spark session, runs ETL, handles cleanup.
    """
    args = parse_args()
    run_dt = parse_run_date(args.run_date)
    
    print("🚀 Starting Real-time ETL Pipeline...")
    print(f"📅 Reference Date: {run_dt.strftime('%Y-%m-%d')}")
    
    spark = create_spark("ZoomCar-Realtime-Pipeline")
    try:
        run_realtime_etl(spark, run_dt)
        print("✅ Real-time pipeline completed successfully")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise
    finally:
        spark.stop()
        print("Spark session closed")


if __name__ == "__main__":
    main()
