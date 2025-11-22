"""
Tests for common validators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
from src.application.validation.common_validators import (
    NotEmptyValidator,
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
    EmailValidator,
    UrlValidator,
    RangeValidator,
    PredicateValidator,
)


class TestNotEmptyValidator:
    """Tests for NotEmptyValidator."""
    
    def test_valid_string(self):
        """Test validation passes for non-empty string."""
        validator = NotEmptyValidator("name", lambda x: x.name)
        
        class Model:
            name = "John"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_empty_string_fails(self):
        """Test validation fails for empty string."""
        validator = NotEmptyValidator("name", lambda x: x.name)
        
        class Model:
            name = ""
        
        is_valid, error = validator.validate(Model())
        assert is_valid is False
        assert "must not be empty" in error
    
    def test_whitespace_string_fails(self):
        """Test validation fails for whitespace-only string."""
        validator = NotEmptyValidator("name", lambda x: x.name)
        
        class Model:
            name = "   "
        
        is_valid, error = validator.validate(Model())
        assert is_valid is False
    
    def test_none_fails(self):
        """Test validation fails for None value."""
        validator = NotEmptyValidator("name", lambda x: x.name)
        
        class Model:
            name = None
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is False
    
    def test_empty_list_fails(self):
        """Test validation fails for empty list."""
        validator = NotEmptyValidator("items", lambda x: x.items)
        
        class Model:
            items = []
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is False


class TestMinLengthValidator:
    """Tests for MinLengthValidator."""
    
    def test_valid_length(self):
        """Test validation passes when length meets minimum."""
        validator = MinLengthValidator("name", lambda x: x.name, min_length=3)
        
        class Model:
            name = "John"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_exact_min_length(self):
        """Test validation passes when length equals minimum."""
        validator = MinLengthValidator("name", lambda x: x.name, min_length=4)
        
        class Model:
            name = "John"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_too_short_fails(self):
        """Test validation fails when length is below minimum."""
        validator = MinLengthValidator("name", lambda x: x.name, min_length=5)
        
        class Model:
            name = "John"
        
        is_valid, error = validator.validate(Model())
        assert is_valid is False
        assert "at least 5" in error
    
    def test_list_length(self):
        """Test validation works with lists."""
        validator = MinLengthValidator("items", lambda x: x.items, min_length=2)
        
        class Model:
            items = [1, 2, 3]
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True


class TestMaxLengthValidator:
    """Tests for MaxLengthValidator."""
    
    def test_valid_length(self):
        """Test validation passes when length is below maximum."""
        validator = MaxLengthValidator("name", lambda x: x.name, max_length=10)
        
        class Model:
            name = "John"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_exact_max_length(self):
        """Test validation passes when length equals maximum."""
        validator = MaxLengthValidator("name", lambda x: x.name, max_length=4)
        
        class Model:
            name = "John"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_too_long_fails(self):
        """Test validation fails when length exceeds maximum."""
        validator = MaxLengthValidator("name", lambda x: x.name, max_length=3)
        
        class Model:
            name = "John"
        
        is_valid, error = validator.validate(Model())
        assert is_valid is False
        assert "at most 3" in error
    
    def test_none_passes(self):
        """Test validation passes for None (max length is optional)."""
        validator = MaxLengthValidator("name", lambda x: x.name, max_length=10)
        
        class Model:
            name = None
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True


class TestRegexValidator:
    """Tests for RegexValidator."""
    
    def test_valid_pattern(self):
        """Test validation passes for matching pattern."""
        validator = RegexValidator("code", lambda x: x.code, pattern=r'^[A-Z]{3}\d{3}$')
        
        class Model:
            code = "ABC123"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_invalid_pattern_fails(self):
        """Test validation fails for non-matching pattern."""
        validator = RegexValidator("code", lambda x: x.code, pattern=r'^[A-Z]{3}\d{3}$')
        
        class Model:
            code = "abc123"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is False


class TestEmailValidator:
    """Tests for EmailValidator."""
    
    def test_valid_email(self):
        """Test validation passes for valid email."""
        validator = EmailValidator("email", lambda x: x.email)
        
        class Model:
            email = "user@example.com"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_invalid_email_fails(self):
        """Test validation fails for invalid email."""
        validator = EmailValidator("email", lambda x: x.email)
        
        class Model:
            email = "not-an-email"
        
        is_valid, error = validator.validate(Model())
        assert is_valid is False
        assert "valid email" in error
    
    def test_email_without_domain_fails(self):
        """Test validation fails for email without domain."""
        validator = EmailValidator("email", lambda x: x.email)
        
        class Model:
            email = "user@"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is False


class TestUrlValidator:
    """Tests for UrlValidator."""
    
    def test_valid_http_url(self):
        """Test validation passes for valid HTTP URL."""
        validator = UrlValidator("website", lambda x: x.website)
        
        class Model:
            website = "http://example.com"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_valid_https_url(self):
        """Test validation passes for valid HTTPS URL."""
        validator = UrlValidator("website", lambda x: x.website)
        
        class Model:
            website = "https://example.com/path"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_invalid_url_fails(self):
        """Test validation fails for invalid URL."""
        validator = UrlValidator("website", lambda x: x.website)
        
        class Model:
            website = "not-a-url"
        
        is_valid, error = validator.validate(Model())
        assert is_valid is False
        assert "valid URL" in error


class TestRangeValidator:
    """Tests for RangeValidator."""
    
    def test_valid_range(self):
        """Test validation passes for value within range."""
        validator = RangeValidator("age", lambda x: x.age, min_value=0, max_value=120)
        
        class Model:
            age = 25
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_min_boundary(self):
        """Test validation passes at minimum boundary."""
        validator = RangeValidator("age", lambda x: x.age, min_value=0, max_value=120)
        
        class Model:
            age = 0
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_max_boundary(self):
        """Test validation passes at maximum boundary."""
        validator = RangeValidator("age", lambda x: x.age, min_value=0, max_value=120)
        
        class Model:
            age = 120
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_below_range_fails(self):
        """Test validation fails for value below range."""
        validator = RangeValidator("age", lambda x: x.age, min_value=0, max_value=120)
        
        class Model:
            age = -1
        
        is_valid, error = validator.validate(Model())
        assert is_valid is False
        assert "between 0 and 120" in error
    
    def test_above_range_fails(self):
        """Test validation fails for value above range."""
        validator = RangeValidator("age", lambda x: x.age, min_value=0, max_value=120)
        
        class Model:
            age = 121
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is False


class TestPredicateValidator:
    """Tests for PredicateValidator."""
    
    def test_valid_predicate(self):
        """Test validation passes when predicate returns True."""
        validator = PredicateValidator(
            "age",
            lambda x: x.age,
            predicate=lambda age: age >= 18
        )
        
        class Model:
            age = 25
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
    
    def test_invalid_predicate_fails(self):
        """Test validation fails when predicate returns False."""
        validator = PredicateValidator(
            "age",
            lambda x: x.age,
            predicate=lambda age: age >= 18
        )
        
        class Model:
            age = 15
        
        is_valid, error = validator.validate(Model())
        assert is_valid is False
        assert "does not meet" in error
    
    def test_complex_predicate(self):
        """Test validation with complex predicate."""
        validator = PredicateValidator(
            "content",
            lambda x: x.content,
            predicate=lambda c: len(c.split()) >= 3
        )
        
        class Model:
            content = "This is valid content"
        
        is_valid, _ = validator.validate(Model())
        assert is_valid is True
