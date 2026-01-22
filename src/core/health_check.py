"""
Health check utilities for services (Kafka, PostgreSQL).
"""
from typing import Dict
import logging

from ..config.settings import (
    KAFKA_BOOTSTRAP_SERVERS,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)

logger = logging.getLogger(__name__)


def check_kafka_health() -> Dict[str, any]:  # type: ignore
    """
    Check Kafka broker health.
    
    Returns:
        Dict with status and details
    """
    try:
        from kafka import KafkaProducer
        
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(","),
            request_timeout_ms=5000,
        )
        producer.close()
        
        return {
            "status": "healthy",
            "service": "kafka",
            "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
        }
    except Exception as e:
        logger.error(f"Kafka health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "kafka",
            "error": str(e),
        }


def check_postgres_health() -> Dict[str, any]:  # type: ignore
    """
    Check PostgreSQL database health.
    
    Returns:
        Dict with status and details
    """
    try:
        from sqlalchemy import create_engine, text
        
        url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        engine = create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 5})
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        engine.dispose()
        
        return {
            "status": "healthy",
            "service": "postgresql",
            "host": POSTGRES_HOST,
            "database": POSTGRES_DB,
        }
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "postgresql",
            "error": str(e),
        }


def check_all_services() -> Dict[str, any]:  # type: ignore
    """
    Check health of all services.
    
    Returns:
        Dict with overall status and individual service statuses
    """
    kafka_status = check_kafka_health()
    postgres_status = check_postgres_health()
    
    all_healthy = (
        kafka_status.get("status") == "healthy" and
        postgres_status.get("status") == "healthy"
    )
    
    return {
        "overall_status": "healthy" if all_healthy else "degraded",
        "services": {
            "kafka": kafka_status,
            "postgresql": postgres_status,
        },
    }
