"""
Data validation utilities.
"""
from typing import Optional

from ..config.validation_rules import EMAIL_REGEX, PHONE_NORMALIZATION
from ..config.business_rules import CUSTOMER_STATUS_MAPPING


def is_valid_email(email: Optional[str]) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
    
    Returns:
        True if valid, False otherwise
    """
    if email is None or not isinstance(email, str):
        return False
    return EMAIL_REGEX.match(email.strip()) is not None


def normalize_phone_to_indian(phone: Optional[str]) -> Optional[str]:
    """
    Normalize phone number to Indian format (+91XXXXXXXXXX).
    Handles various formats: 9876543210, 919876543210, 09876543210, etc.
    Uses configuration from business_rules for country code.
    """
    import re
    
    if phone is None or not isinstance(phone, str):
        return None
    
    # Remove characters as per config
    digits = phone
    for char in PHONE_NORMALIZATION.get("remove_chars", [" ", "-", "(", ")", "+", "."]):
        digits = digits.replace(char, "")
    
    # Extract only digits
    digits = re.sub(r"\D", "", digits)
    
    country_code = PHONE_NORMALIZATION["country_code"].replace("+", "")
    min_digits = PHONE_NORMALIZATION.get("min_digits", 10)
    max_digits = PHONE_NORMALIZATION.get("max_digits", 10)
    
    # Handle different Indian number formats
    if digits.startswith(country_code) and len(digits) == 12:
        # Already has country code
        return f"+{digits}"
    elif digits.startswith("0") and len(digits) == 11:
        # Leading zero format (09876543210)
        return f"+{country_code}{digits[1:]}"
    elif len(digits) == min_digits:
        # Standard 10-digit mobile number
        return f"+{country_code}{digits}"
    # else: invalid format, return None
    
    return None


def normalize_customer_status(status: Optional[str]) -> Optional[str]:
    """
    Normalize customer status to standard format.
    Uses mapping from business_rules config.
    """
    if status is None or not isinstance(status, str):
        return None
    
    status_lower = status.lower().strip()
    
    # Check against configured mappings
    for normalized_status, variations in CUSTOMER_STATUS_MAPPING.items():
        if status_lower in variations:
            return normalized_status.upper()
    
    # If not recognized, just uppercase it (might be a custom status)
    return status.upper()
