import os
import shutil
from datetime import datetime

import pandas as pd
from pyspark.sql import functions as F

from .utils import create_spark
from . import config


def ensure_reports_dir() -> str:
    """
    Create a fresh reports directory so old dashboards disappear if data is missing.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, "reports")
    if os.path.exists(reports_dir):
        shutil.rmtree(reports_dir, ignore_errors=True)
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir


def run_deequ_checks(spark) -> dict:
    """
    Run basic data quality checks on staging tables using Deequ (via pydeequ).
    Returns a dict with check results for easy reporting.
    """
    from pydeequ.checks import Check, CheckLevel
    from pydeequ.verification import VerificationSuite

    results: dict[str, dict] = {}

    # --- Bookings DQ checks ---
    try:
        bookings_df = spark.read.parquet(config.BOOKINGS_STAGING_PATH)
    except Exception:
        bookings_df = None

    if bookings_df is not None:
        check = (
            Check(spark, CheckLevel.Warning, "bookings_dq")
            .hasSize(lambda s: s > 0, "Bookings table should not be empty")
            .isComplete("booking_id")
            .isComplete("customer_id")
            .isContainedIn(
                "booking_status",
                ["created", "in_progress", "completed", "cancelled"],
            )
            .isNonNegative("booking_duration_minutes", hint="Duration should be >= 0")
        )

        verification_result = (
            VerificationSuite(spark)
            .onData(bookings_df)
            .addCheck(check)
            .run()
        )
        results["bookings"] = VerificationResult.checkResultsAsJson(spark, verification_result)

    # --- Customers DQ checks ---
    try:
        customers_df = spark.read.parquet(config.CUSTOMERS_STAGING_PATH)
    except Exception:
        customers_df = None

    if customers_df is not None:
        check = (
            Check(spark, CheckLevel.Warning, "customers_dq")
            .hasSize(lambda s: s > 0, "Customers table should not be empty")
            .isComplete("customer_id")
            .isComplete("email")
            .isComplete("customer_status_std")
        )

        verification_result = (
            VerificationSuite(spark)
            .onData(customers_df)
            .addCheck(check)
            .run()
        )
        results["customers"] = VerificationResult.checkResultsAsJson(spark, verification_result)

    return results


def build_valid_data_summary(spark) -> dict:
    """
    Simple aggregations over final tables for dashboard.
    """
    summary: dict[str, pd.DataFrame] = {}

    # Bookings summaries
    try:
        bookings = spark.read.parquet(config.BOOKINGS_FINAL_PATH)
    except Exception:
        bookings = None

    if bookings is not None:
        by_status = (
            bookings.groupBy("booking_status")
            .agg(
                F.count("*").alias("booking_count"),
                F.avg("booking_duration_minutes").alias("avg_duration_min"),
            )
            .orderBy("booking_status")
        )
        summary["bookings_by_status"] = by_status.toPandas()

        by_city = (
            bookings.groupBy("pickup_city")
            .agg(F.count("*").alias("booking_count"))
            .orderBy(F.desc("booking_count"))
        )
        summary["bookings_by_city"] = by_city.toPandas()

    # Customers summaries
    try:
        customers = spark.read.parquet(config.CUSTOMERS_FINAL_PATH)
    except Exception:
        customers = None

    if customers is not None:
        by_status = (
            customers.groupBy("customer_status_std")
            .agg(
                F.count("*").alias("customer_count"),
                F.avg("customer_tenure_days").alias("avg_tenure_days"),
            )
            .orderBy("customer_status_std")
        )
        summary["customers_by_status"] = by_status.toPandas()

    return summary


def generate_html_dashboard(dq_results: dict, summary_tables: dict) -> None:
    reports_dir = ensure_reports_dir()
    html_path = os.path.join(reports_dir, "data_quality_dashboard.html")

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    parts = [
        "<html><head><title>Zoom Car Data Quality Dashboard</title>",
        "<style>",
        "body{font-family:Arial, sans-serif;margin:20px;}",
        ".card{border:1px solid #ddd;border-radius:6px;padding:12px;margin:12px 0;background:#fafafa;box-shadow:0 1px 3px rgba(0,0,0,0.08);}",
        "h1{margin-bottom:4px;} .meta{color:#666;font-size:13px;}",
        "table{border-collapse:collapse;width:100%;margin:8px 0;}",
        "th,td{border:1px solid #ccc;padding:6px 8px;font-size:13px;text-align:left;}",
        "th{background:#f0f0f0;}",
        ".badge{display:inline-block;padding:4px 8px;border-radius:12px;font-size:12px;color:#fff;}",
        ".pass{background:#28a745;} .warn{background:#ffc107;color:#333;} .fail{background:#dc3545;}",
        "</style>",
        "</head><body>",
        f"<h1>Zoom Car Data Quality & Valid Data Dashboard</h1>",
        f"<div class='meta'>Generated at: {now_str}</div>",
    ]

    # DQ section
    parts.append("<div class='card'><h2>Data Quality Checks (Deequ)</h2>")
    if not dq_results:
        parts.append("<p>No DQ results available (staging tables not found).</p></div>")
    else:
        for table_name, result in dq_results.items():
            parts.append(f"<h3>Table: {table_name}</h3>")
            check_results = result.get("checkResults", {})
            rows = []
            for check_name, details in check_results.items():
                status = details.get("status")
                constraint_results = details.get("constraintResults", [])
                for constraint in constraint_results:
                    rows.append(
                        {
                            "check": check_name,
                            "status": status,
                            "constraint": constraint.get("constraint"),
                            "constraint_status": constraint.get("status"),
                            "message": constraint.get("message"),
                        }
                    )
            if rows:
                df = pd.DataFrame(rows)
                # Render status as colored badges
                def fmt_status(s):
                    if s is None:
                        return s
                    s = str(s).lower()
                    if s == "success":
                        return "<span class='badge pass'>PASS</span>"
                    if s == "warning":
                        return "<span class='badge warn'>WARN</span>"
                    return "<span class='badge fail'>FAIL</span>"

                df["status"] = df["status"].apply(fmt_status)
                df["constraint_status"] = df["constraint_status"].apply(fmt_status)
                parts.append(df.to_html(index=False, escape=False))
            else:
                parts.append("<p>No constraint results found.</p>")
        parts.append("</div>")

    # Valid data summaries
    parts.append("<div class='card'><h2>Valid Data Summary (Final Tables)</h2>")
    if not summary_tables:
        parts.append("<p>No final tables found.</p></div>")
    else:
        for name, df in summary_tables.items():
            parts.append(f"<h3>{name}</h3>")
            parts.append(df.to_html(index=False))
        parts.append("</div>")

    parts.append("</body></html>")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def delete_dashboard_if_exists() -> None:
    """
    Remove any existing dashboard artifacts when no data is available.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, "reports")
    if os.path.exists(reports_dir):
        shutil.rmtree(reports_dir, ignore_errors=True)


def main() -> None:
    spark = create_spark("ZoomCar-DQ-Dashboard")
    try:
        dq_results = run_deequ_checks(spark)
        summary = build_valid_data_summary(spark)

        # If no data anywhere, remove stale dashboard; else regenerate fresh
        if not dq_results and not summary:
            delete_dashboard_if_exists()
        else:
            generate_html_dashboard(dq_results, summary)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

