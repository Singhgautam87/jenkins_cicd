"""
Customers data model and processing logic.
"""
from datetime import datetime
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from ..utils.validators import normalize_phone_to_indian, normalize_customer_status, is_valid_email


def validate_customer(df: DataFrame) -> DataFrame:
    """Validate customers data."""
    df = df.dropna(subset=["customer_id"])
    df = df.withColumn("signup_date_parsed", F.to_date("signup_date", "yyyy-MM-dd"))
    df = df.filter(F.col("signup_date_parsed").isNotNull())
    
    # Email validation
    is_valid_email_udf = F.udf(is_valid_email)
    df = df.withColumn("email_valid", is_valid_email_udf("email"))
    df = df.filter(F.col("email_valid") == F.lit(True)).drop("email_valid")
    
    # Standardize customer status
    normalize_status_udf = F.udf(normalize_customer_status)
    df = df.withColumn("customer_status_std", normalize_status_udf("customer_status"))
    
    return df


def transform_customer(df: DataFrame, run_date: datetime) -> DataFrame:
    """Transform customers: normalize phone, calculate tenure."""
    normalize_phone_udf = F.udf(normalize_phone_to_indian)
    df = df.withColumn("phone_norm", normalize_phone_udf("phone"))
    df = df.withColumn(
        "customer_tenure_days",
        F.datediff(F.lit(run_date.date()), F.col("signup_date_parsed")),
    )
    return df


def get_customer_columns() -> list:
    """Get list of customer columns."""
    return [
        "customer_id",
        "customer_name",
        "email",
        "phone",
        "customer_status_std",
        "signup_date_parsed",
    ]
