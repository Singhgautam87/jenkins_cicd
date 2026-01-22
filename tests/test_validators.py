"""
Unit tests for validation utilities.
"""
import pytest
from src.utils.validators import (
    is_valid_email,
    normalize_phone_to_indian,
    normalize_customer_status,
)


class TestEmailValidation:
    """Test email validation."""
    
    def test_valid_emails(self):
        assert is_valid_email("test@example.com") is True
        assert is_valid_email("user.name@domain.co.uk") is True
    
    def test_invalid_emails(self):
        assert is_valid_email("invalid") is False
        assert is_valid_email("@domain.com") is False
        assert is_valid_email(None) is False
        assert is_valid_email("") is False


class TestPhoneNormalization:
    """Test phone number normalization."""
    
    def test_indian_10_digit(self):
        assert normalize_phone_to_indian("9876543210") == "+919876543210"
    
    def test_indian_with_country_code(self):
        assert normalize_phone_to_indian("919876543210") == "+919876543210"
    
    def test_invalid_phone(self):
        assert normalize_phone_to_indian(None) is None
        assert normalize_phone_to_indian("123") is None


class TestStatusNormalization:
    """Test customer status normalization."""
    
    def test_active_variants(self):
        assert normalize_customer_status("active") == "ACTIVE"
        assert normalize_customer_status("ACTIVE") == "ACTIVE"
        assert normalize_customer_status("act") == "ACTIVE"
    
    def test_invalid_status(self):
        assert normalize_customer_status(None) is None
