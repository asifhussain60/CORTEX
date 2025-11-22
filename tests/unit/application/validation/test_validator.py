"""
Tests for Validator class with fluent API.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
from dataclasses import dataclass
from src.application.validation.validator import Validator


@dataclass
class UserModel:
    """Test model for validation."""
    username: str = ""
    email: str = ""
    age: int = 0
    website: str = ""
    bio: str = ""


class TestValidator:
    """Tests for Validator base class."""
    
    def test_create_empty_validator(self):
        """Test creating a validator with no rules."""
        validator = Validator[UserModel]()
        result = validator.validate(UserModel())
        
        assert result.is_valid is True
    
    def test_validator_with_single_rule(self):
        """Test validator with a single rule."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.username).not_empty()
        
        validator = UserValidator()
        
        # Valid case
        user = UserModel(username="john")
        result = validator.validate(user)
        assert result.is_valid is True
        
        # Invalid case
        user = UserModel(username="")
        result = validator.validate(user)
        assert result.is_invalid is True
        assert len(result.errors) == 1
    
    def test_validator_with_multiple_rules_same_property(self):
        """Test validator with multiple rules on same property."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.username) \
                    .not_empty() \
                    .min_length(3) \
                    .max_length(20)
        
        validator = UserValidator()
        
        # Valid case
        user = UserModel(username="john")
        result = validator.validate(user)
        assert result.is_valid is True
        
        # Too short
        user = UserModel(username="jo")
        result = validator.validate(user)
        assert result.is_invalid is True
        
        # Too long
        user = UserModel(username="verylongusernamethatexceedslimit")
        result = validator.validate(user)
        assert result.is_invalid is True
    
    def test_validator_with_multiple_properties(self):
        """Test validator with rules for multiple properties."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.username).not_empty().min_length(3)
                self.rule_for(lambda x: x.email).not_empty().email()
                self.rule_for(lambda x: x.age).range(0, 120)
        
        validator = UserValidator()
        
        # All valid
        user = UserModel(username="john", email="john@example.com", age=25)
        result = validator.validate(user)
        assert result.is_valid is True
        
        # Multiple invalid
        user = UserModel(username="jo", email="invalid", age=-1)
        result = validator.validate(user)
        assert result.is_invalid is True
        assert len(result.errors) == 3
    
    def test_validator_with_custom_message(self):
        """Test validator with custom error messages."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.username) \
                    .not_empty() \
                    .with_message("Username is required for registration")
        
        validator = UserValidator()
        user = UserModel(username="")
        result = validator.validate(user)
        
        assert result.is_invalid is True
        assert "Username is required for registration" in str(result)
    
    def test_validator_with_conditional_rule(self):
        """Test validator with conditional rule (when)."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.website) \
                    .url() \
                    .when(lambda x: x.website is not None and len(x.website) > 0)
        
        validator = UserValidator()
        
        # No website provided - should pass
        user = UserModel(website="")
        result = validator.validate(user)
        assert result.is_valid is True
        
        # Invalid website provided - should fail
        user = UserModel(website="not-a-url")
        result = validator.validate(user)
        assert result.is_invalid is True
        
        # Valid website - should pass
        user = UserModel(website="https://example.com")
        result = validator.validate(user)
        assert result.is_valid is True
    
    def test_validator_with_must_predicate(self):
        """Test validator with custom must() predicate."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.bio) \
                    .must(lambda bio: len(bio.split()) >= 3) \
                    .with_message("Bio must contain at least 3 words")
        
        validator = UserValidator()
        
        # Valid bio
        user = UserModel(bio="I love coding Python")
        result = validator.validate(user)
        assert result.is_valid is True
        
        # Invalid bio
        user = UserModel(bio="Too short")
        result = validator.validate(user)
        assert result.is_invalid is True
        assert "at least 3 words" in str(result)
    
    def test_validator_email_validation(self):
        """Test validator with email rule."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.email).email()
        
        validator = UserValidator()
        
        # Valid email
        user = UserModel(email="user@example.com")
        result = validator.validate(user)
        assert result.is_valid is True
        
        # Invalid email
        user = UserModel(email="not-an-email")
        result = validator.validate(user)
        assert result.is_invalid is True
    
    def test_validator_url_validation(self):
        """Test validator with url rule."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.website).url()
        
        validator = UserValidator()
        
        # Valid URL
        user = UserModel(website="https://example.com")
        result = validator.validate(user)
        assert result.is_valid is True
        
        # Invalid URL
        user = UserModel(website="not-a-url")
        result = validator.validate(user)
        assert result.is_invalid is True
    
    def test_validator_range_validation(self):
        """Test validator with range rule."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.age).range(0, 120)
        
        validator = UserValidator()
        
        # Valid age
        user = UserModel(age=25)
        result = validator.validate(user)
        assert result.is_valid is True
        
        # Invalid age (negative)
        user = UserModel(age=-1)
        result = validator.validate(user)
        assert result.is_invalid is True
        
        # Invalid age (too high)
        user = UserModel(age=150)
        result = validator.validate(user)
        assert result.is_invalid is True
    
    def test_validator_matches_pattern(self):
        """Test validator with regex pattern."""
        class CodeValidator(Validator):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.code).matches(r'^[A-Z]{3}\d{3}$')
        
        validator = CodeValidator()
        
        @dataclass
        class CodeModel:
            code: str
        
        # Valid code
        model = CodeModel(code="ABC123")
        result = validator.validate(model)
        assert result.is_valid is True
        
        # Invalid code
        model = CodeModel(code="abc123")
        result = validator.validate(model)
        assert result.is_invalid is True
    
    def test_validator_async(self):
        """Test async validation."""
        import asyncio
        
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.username).not_empty()
        
        validator = UserValidator()
        user = UserModel(username="")
        
        result = asyncio.run(validator.validate_async(user))
        assert result.is_invalid is True
    
    def test_get_errors_by_property(self):
        """Test getting errors for specific property."""
        class UserValidator(Validator[UserModel]):
            def __init__(self):
                super().__init__()
                self.rule_for(lambda x: x.username).not_empty().min_length(3)
                self.rule_for(lambda x: x.email).not_empty()
        
        validator = UserValidator()
        user = UserModel(username="jo", email="")
        result = validator.validate(user)
        
        username_errors = result.get_errors_for_property("username")
        assert len(username_errors) == 1
        assert "at least 3" in username_errors[0].error_message
        
        email_errors = result.get_errors_for_property("email")
        assert len(email_errors) == 1
