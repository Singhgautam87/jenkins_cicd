import argparse

from .utils import parse_run_date
from .process_data import run_process_daily
from .transform_merge import run_transform_and_merge


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Zoom Car Daily ETL Pipeline")
    parser.add_argument(
        "--run-date",
        dest="run_date",
        type=str,
        required=False,
        help="Run date in YYYY-MM-DD format. If omitted, uses today's date.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Main batch pipeline entry point.
    Processes daily JSON file and creates final Parquet tables.
    """
    args = parse_args()
    run_dt = parse_run_date(args.run_date)
    
    print(f"Starting batch pipeline for date: {run_dt.strftime('%Y-%m-%d')}")
    
    # Step 1: Read JSON, validate, write to staging
    print("Step 1: Processing raw data...")
    run_process_daily(run_dt)
    
    # Step 2: Transform and merge into final tables
    print("Step 2: Transforming and merging...")
    run_transform_and_merge(run_dt)
    
    print("✅ Batch pipeline completed")


if __name__ == "__main__":
    main()

