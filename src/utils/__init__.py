"""Utility functions and helpers."""
from datetime import datetime

def parse_run_date(date_str):
    """Parse date string YYYY-MM-DD to datetime"""
    return datetime.strptime(date_str, '%Y-%m-%d')
