"""
Unit tests for RoleVerbosityProfiles.

Tests per-role formatting preferences for Engineer, PM, Business, Architect.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34 specification
"""

import pytest
from typing import Dict, Any

from cortex.orchestrators.response.role_verbosity_profiles import (
    RoleVerbosityProfiles,
    Role,
    VerbosityProfile,
)


class TestRoleVerbosityProfiles:
    """Test role-based verbosity profiles."""
    
    @pytest.fixture
    def profiles(self) -> RoleVerbosityProfiles:
        """Create profiles instance."""
        return RoleVerbosityProfiles()
    
    def test_all_roles_defined(self, profiles):
        """Test that all 4 roles have profiles."""
        assert Role.ENGINEER in profiles.profiles
        assert Role.PM in profiles.profiles
        assert Role.BUSINESS in profiles.profiles
        assert Role.ARCHITECT in profiles.profiles
    
    def test_engineer_profile_high_detail(self, profiles):
        """Test that engineer profile has high detail level."""
        engineer = profiles.get_profile(Role.ENGINEER)
        
        assert engineer.detail_level == "HIGH"
        assert engineer.code_examples == "REQUIRED"
        assert engineer.technical_depth == "MAXIMUM"
    
    def test_pm_profile_balanced(self, profiles):
        """Test that PM profile is balanced."""
        pm = profiles.get_profile(Role.PM)
        
        assert pm.detail_level == "MEDIUM"
        assert pm.code_examples == "OPTIONAL"
        assert pm.technical_depth == "MODERATE"
    
    def test_business_profile_minimal(self, profiles):
        """Test that business profile is minimal."""
        business = profiles.get_profile(Role.BUSINESS)
        
        assert business.detail_level == "LOW"
        assert business.code_examples == "NONE"
        assert business.business_language == "PRIMARY"
    
    def test_architect_profile_selective(self, profiles):
        """Test that architect profile is selective."""
        architect = profiles.get_profile(Role.ARCHITECT)
        
        assert architect.detail_level == "MEDIUM-HIGH"
        assert architect.code_examples == "SELECTIVE"
        assert architect.technical_depth == "HIGH"
    
    def test_apply_profile_to_response(self, profiles):
        """Test applying profile to response."""
        response = """
        The system uses PostgreSQL for data storage.
        
        ```python
        def connect_db():
            return psycopg2.connect(...)
        ```
        
        PostgreSQL handles ACID transactions.
        It supports JSON data types.
        """
        
        # Apply business profile (should remove code)
        business_response = profiles.apply_profile(response, Role.BUSINESS)
        
        assert "```python" not in business_response
        assert "PostgreSQL" in business_response
    
    def test_engineer_profile_preserves_code(self, profiles):
        """Test that engineer profile preserves all code."""
        response = """
        Implementation details:
        
        ```python
        def authenticate(token):
            return verify_jwt(token)
        ```
        """
        
        engineer_response = profiles.apply_profile(response, Role.ENGINEER)
        
        assert "```python" in engineer_response
        assert "def authenticate" in engineer_response
    
    def test_default_profile_is_engineer(self, profiles):
        """Test that default profile is engineer."""
        default = profiles.get_profile()
        assert default.detail_level == "HIGH"
    
    def test_profile_expected_reduction(self, profiles):
        """Test expected reduction rates per profile."""
        engineer = profiles.get_profile(Role.ENGINEER)
        pm = profiles.get_profile(Role.PM)
        business = profiles.get_profile(Role.BUSINESS)
        architect = profiles.get_profile(Role.ARCHITECT)
        
        # Verify reduction expectations
        assert engineer.expected_reduction == "0-10%"
        assert pm.expected_reduction == "20-30%"
        assert business.expected_reduction == "40-50%"
        assert architect.expected_reduction == "10-20%"


class TestRole:
    """Test Role enum."""
    
    def test_all_roles_enumerated(self):
        """Test that all 4 roles are enumerated."""
        roles = list(Role)
        assert len(roles) == 4
        assert Role.ENGINEER in roles
        assert Role.PM in roles
        assert Role.BUSINESS in roles
        assert Role.ARCHITECT in roles


class TestVerbosityProfile:
    """Test VerbosityProfile dataclass."""
    
    def test_profile_creation(self):
        """Test VerbosityProfile instantiation."""
        profile = VerbosityProfile(
            detail_level="HIGH",
            code_examples="REQUIRED",
            business_language="MINIMAL",
            technical_depth="MAXIMUM",
            expected_reduction="0-10%"
        )
        
        assert profile.detail_level == "HIGH"
        assert profile.code_examples == "REQUIRED"
        assert profile.expected_reduction == "0-10%"
    
    def test_profile_to_dict(self):
        """Test VerbosityProfile conversion to dictionary."""
        profile = VerbosityProfile(
            detail_level="MEDIUM",
            code_examples="OPTIONAL",
            business_language="BALANCED",
            technical_depth="MODERATE",
            expected_reduction="20-30%"
        )
        
        profile_dict = profile.to_dict()
        
        assert isinstance(profile_dict, dict)
        assert profile_dict["detail_level"] == "MEDIUM"
        assert profile_dict["expected_reduction"] == "20-30%"
