"""
Application settings and environment configuration.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Spark Configuration
SPARK_VERSION = os.getenv("SPARK_VERSION", "3.3")
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
SPARK_APP_NAME = os.getenv("SPARK_APP_NAME", "ZoomCar-ETL")

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_RAW_EVENTS = os.getenv("KAFKA_TOPIC_RAW_EVENTS", "zoomcar-raw-events")
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "zoomcar-etl-group")
KAFKA_AUTO_OFFSET_RESET = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")

# PostgreSQL Configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "zoomcar_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "zoomcar_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "zoomcar_pass")
POSTGRES_POOL_SIZE = int(os.getenv("POSTGRES_POOL_SIZE", "5"))

# Data Processing
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))

# Data Quality
DQ_ENABLED = os.getenv("DQ_ENABLED", "true").lower() == "true"
DQ_STRICT_MODE = os.getenv("DQ_STRICT_MODE", "false").lower() == "true"

# Kafka Producer Settings
KAFKA_PRODUCER_CONFIG = {
    "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS.split(","),
    "value_serializer": "json",
    "key_serializer": "string",
    "acks": "all",  # Wait for all replicas
    "retries": 3,
    "max_in_flight_requests_per_connection": 1,
    "compression_type": "snappy",
}

# Kafka Consumer Settings
KAFKA_CONSUMER_CONFIG = {
    "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS.split(","),
    "group_id": KAFKA_CONSUMER_GROUP,
    "auto_offset_reset": KAFKA_AUTO_OFFSET_RESET,
    "enable_auto_commit": True,
    "auto_commit_interval_ms": 5000,
    "max_poll_records": 500,
}

# PostgreSQL Connection Pool Settings
POSTGRES_CONNECTION_POOL = {
    "pool_size": POSTGRES_POOL_SIZE,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 3600,  # Recycle connections after 1 hour
    "pool_pre_ping": True,  # Verify connections before using
}

# File Processing Settings
FILE_PROCESSING = {
    "encoding": "utf-8",
    "chunk_size": 8192,  # Bytes
    "max_file_size_mb": 500,
}

# Logging Configuration
LOGGING_CONFIG = {
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "file_rotation": {
        "max_bytes": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5,
    },
}
