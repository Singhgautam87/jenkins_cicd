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
    args = parse_args()
    run_dt = parse_run_date(args.run_date)

    # 1) Process raw daily JSON into staging
    run_process_daily(run_dt)

    # 2) Transform and merge into final tables
    run_transform_and_merge(run_dt)


if __name__ == "__main__":
    main()

