"""
Date parsing and utility functions.
"""
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def parse_date_safe(date_str: Optional[str], format_str: str = "%Y-%m-%d") -> Optional[datetime]:
    """
    Safely parse date string.
    
    Args:
        date_str: Date string to parse
        format_str: Date format string
    
    Returns:
        Parsed datetime or None if parsing fails
    """
    if date_str is None or not isinstance(date_str, str):
        return None
    
    try:
        return datetime.strptime(date_str.strip(), format_str)
    except (ValueError, AttributeError) as e:
        logger.debug(f"Failed to parse date '{date_str}': {e}")
        return None


def parse_run_date(run_date_str: Optional[str]) -> datetime:
    """
    Parse run date parameter, defaulting to today if not provided.
    
    Args:
        run_date_str: Date string in YYYY-MM-DD format (or RUN_DATE=YYYY-MM-DD)
    
    Returns:
        Parsed datetime object
    """
    if run_date_str:
        # Handle cases like "RUN_DATE=2026-01-01"
        if "=" in run_date_str:
            run_date_str = run_date_str.split("=")[-1].strip()
        
        parsed = parse_date_safe(run_date_str)
        if parsed:
            return parsed
        else:
            logger.warning(f"Invalid run_date format: {run_date_str}, using today")
    
    return datetime.now()
