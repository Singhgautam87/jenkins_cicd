"""
Spark-specific configuration.
All Spark settings centralized here for easy tuning.
"""
from .settings import SPARK_VERSION, SPARK_MASTER, SPARK_APP_NAME

# Spark application configuration
SPARK_CONFIG = {
    "app_name": SPARK_APP_NAME,
    "master": SPARK_MASTER,
    "spark_version": SPARK_VERSION,
    
    # Performance tuning
    "spark.sql.shuffle.partitions": 4,
    "spark.sql.adaptive.enabled": True,
    "spark.sql.adaptive.coalescePartitions.enabled": True,
    "spark.sql.adaptive.skewJoin.enabled": True,
    
    # Memory settings (for local mode)
    "spark.driver.memory": "2g",
    "spark.executor.memory": "2g",
    
    # Serialization
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    
    # Deequ package
    "spark.jars.packages": f"com.amazon.deequ:deequ:2.0.7-spark-{SPARK_VERSION}",
    
    # Logging
    "spark.sql.execution.arrow.pyspark.enabled": "false",  # Disable Arrow for compatibility
}

def get_spark_config() -> dict:
    """Get Spark configuration dictionary."""
    return SPARK_CONFIG.copy()
