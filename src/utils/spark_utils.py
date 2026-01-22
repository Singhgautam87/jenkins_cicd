"""
Spark session creation and configuration utilities.
"""
import os
from pyspark.sql import SparkSession

from ..config.spark_config import get_spark_config


def create_spark(app_name: str = None) -> SparkSession:
    """
    Create a Spark session with proper configuration.
    All Spark config comes from spark_config module.
    
    Args:
        app_name: Application name (overrides default from config)
    
    Returns:
        Configured SparkSession instance
    """
    spark_config = get_spark_config()
    
    # Override app name if provided
    if app_name:
        spark_config["app_name"] = app_name
    
    builder = SparkSession.builder.appName(spark_config["app_name"])
    
    # Apply all Spark configurations
    for key, value in spark_config.items():
        if key not in ["app_name", "master", "spark_version"]:
            builder = builder.config(key, value)
    
    builder = builder.master(spark_config["master"])
    
    # Set Spark version for Deequ (required by pydeequ)
    os.environ["SPARK_VERSION"] = spark_config["spark_version"]
    
    return builder.getOrCreate()
