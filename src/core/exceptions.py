"""
Custom exceptions for the application.
"""


class ZoomCarETLException(Exception):
    """Base exception for all ETL errors."""
    pass


class DataValidationError(ZoomCarETLException):
    """Raised when data validation fails."""
    pass


class KafkaConnectionError(ZoomCarETLException):
    """Raised when Kafka connection fails."""
    pass


class DatabaseConnectionError(ZoomCarETLException):
    """Raised when database connection fails."""
    pass


class ConfigurationError(ZoomCarETLException):
    """Raised when configuration is invalid."""
    pass


class ProcessingError(ZoomCarETLException):
    """Raised when data processing fails."""
    pass
