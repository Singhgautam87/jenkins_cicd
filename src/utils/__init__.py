"""Utility functions and helpers."""
from datetime import datetime
from pyspark.sql import SparkSession

def parse_run_date(date_str):
    """Parse date string YYYY-MM-DD to datetime"""
    return datetime.strptime(date_str, '%Y-%m-%d')



def create_spark(app_name="ZoomcarETL"):
    """Create and return Spark session"""
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .config("spark.sql.streaming.schemaInference", "true") \
        .getOrCreate()
