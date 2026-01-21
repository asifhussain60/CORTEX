"""
Tests for pre-built governance profiles.

Validates structure and content of tier1 profile YAML files.

AC-ID: AC-DEP-006-04
"""

import pytest
from pathlib import Path
import yaml


class TestFinOpsProfile:
    """Tests for finops-v1.0.yaml profile."""
    
    @pytest.fixture
    def profile_path(self) -> Path:
        """Get path to finops profile."""
        return Path(__file__).parent.parent.parent / "cortex_brain" / "tier1" / "profiles" / "finops-v1.0.yaml"
    
    @pytest.fixture
    def profile_data(self, profile_path: Path) -> dict:
        """Load profile data."""
        return yaml.safe_load(profile_path.read_text())
    
    def test_profile_exists(self, profile_path: Path):
        """Test that finops profile file exists."""
        assert profile_path.exists(), "finops-v1.0.yaml should exist"
    
    def test_profile_has_required_fields(self, profile_data: dict):
        """Test profile has required metadata fields."""
        assert "profile" in profile_data
        assert "id" in profile_data["profile"]
        assert "name" in profile_data["profile"]
        assert "version" in profile_data["profile"]
        assert "rules" in profile_data
    
    def test_profile_has_minimum_rules(self, profile_data: dict):
        """Test profile has at least 15 rules."""
        rules = profile_data.get("rules", [])
        assert len(rules) >= 15, f"Expected at least 15 rules, got {len(rules)}"


class TestAuthProfile:
    """Tests for auth-v1.0.yaml profile."""
    
    @pytest.fixture
    def profile_path(self) -> Path:
        """Get path to auth profile."""
        return Path(__file__).parent.parent.parent / "cortex_brain" / "tier1" / "profiles" / "auth-v1.0.yaml"
    
    @pytest.fixture
    def profile_data(self, profile_path: Path) -> dict:
        """Load profile data."""
        return yaml.safe_load(profile_path.read_text())
    
    def test_profile_exists(self, profile_path: Path):
        """Test that auth profile file exists."""
        assert profile_path.exists(), "auth-v1.0.yaml should exist"
    
    def test_profile_has_required_fields(self, profile_data: dict):
        """Test profile has required metadata fields."""
        assert "profile" in profile_data
        assert "id" in profile_data["profile"]
        assert "name" in profile_data["profile"]
        assert "version" in profile_data["profile"]
        assert "rules" in profile_data
    
    def test_profile_has_minimum_rules(self, profile_data: dict):
        """Test profile has at least 12 rules."""
        rules = profile_data.get("rules", [])
        assert len(rules) >= 12, f"Expected at least 12 rules, got {len(rules)}"


class TestMLProfile:
    """Tests for ml-v1.0.yaml profile."""
    
    @pytest.fixture
    def profile_path(self) -> Path:
        """Get path to ML profile."""
        return Path(__file__).parent.parent.parent / "cortex_brain" / "tier1" / "profiles" / "ml-v1.0.yaml"
    
    @pytest.fixture
    def profile_data(self, profile_path: Path) -> dict:
        """Load profile data."""
        return yaml.safe_load(profile_path.read_text())
    
    def test_profile_exists(self, profile_path: Path):
        """Test that ML profile file exists."""
        assert profile_path.exists(), "ml-v1.0.yaml should exist"
    
    def test_profile_has_required_fields(self, profile_data: dict):
        """Test profile has required metadata fields."""
        assert "profile" in profile_data
        assert "id" in profile_data["profile"]
        assert "name" in profile_data["profile"]
        assert "version" in profile_data["profile"]
        assert "rules" in profile_data
    
    def test_profile_has_minimum_rules(self, profile_data: dict):
        """Test profile has at least 10 rules."""
        rules = profile_data.get("rules", [])
        assert len(rules) >= 10, f"Expected at least 10 rules, got {len(rules)}"


class TestDevOpsProfile:
    """Tests for devops-v1.0.yaml profile."""
    
    @pytest.fixture
    def profile_path(self) -> Path:
        """Get path to DevOps profile."""
        return Path(__file__).parent.parent.parent / "cortex_brain" / "tier1" / "profiles" / "devops-v1.0.yaml"
    
    @pytest.fixture
    def profile_data(self, profile_path: Path) -> dict:
        """Load profile data."""
        return yaml.safe_load(profile_path.read_text())
    
    def test_profile_exists(self, profile_path: Path):
        """Test that DevOps profile file exists."""
        assert profile_path.exists(), "devops-v1.0.yaml should exist"
    
    def test_profile_has_required_fields(self, profile_data: dict):
        """Test profile has required metadata fields."""
        assert "profile" in profile_data
        assert "id" in profile_data["profile"]
        assert "name" in profile_data["profile"]
        assert "version" in profile_data["profile"]
        assert "rules" in profile_data
    
    def test_profile_has_minimum_rules(self, profile_data: dict):
        """Test profile has at least 8 rules."""
        rules = profile_data.get("rules", [])
        assert len(rules) >= 8, f"Expected at least 8 rules, got {len(rules)}"


class TestHealthcareProfile:
    """Tests for healthcare-v1.0.yaml profile."""
    
    @pytest.fixture
    def profile_path(self) -> Path:
        """Get path to healthcare profile."""
        return Path(__file__).parent.parent.parent / "cortex_brain" / "tier1" / "profiles" / "healthcare-v1.0.yaml"
    
    @pytest.fixture
    def profile_data(self, profile_path: Path) -> dict:
        """Load profile data."""
        return yaml.safe_load(profile_path.read_text())
    
    def test_profile_exists(self, profile_path: Path):
        """Test that healthcare profile file exists."""
        assert profile_path.exists(), "healthcare-v1.0.yaml should exist"
    
    def test_profile_has_required_fields(self, profile_data: dict):
        """Test profile has required metadata fields."""
        assert "profile" in profile_data
        assert "id" in profile_data["profile"]
        assert "name" in profile_data["profile"]
        assert "version" in profile_data["profile"]
        assert "rules" in profile_data
    
    def test_profile_has_minimum_rules(self, profile_data: dict):
        """Test profile has at least 12 rules."""
        rules = profile_data.get("rules", [])
        assert len(rules) >= 12, f"Expected at least 12 rules, got {len(rules)}"


class TestLegalProfile:
    """Tests for legal-v1.0.yaml profile."""
    
    @pytest.fixture
    def profile_path(self) -> Path:
        """Get path to legal profile."""
        return Path(__file__).parent.parent.parent / "cortex_brain" / "tier1" / "profiles" / "legal-v1.0.yaml"
    
    @pytest.fixture
    def profile_data(self, profile_path: Path) -> dict:
        """Load profile data."""
        return yaml.safe_load(profile_path.read_text())
    
    def test_profile_exists(self, profile_path: Path):
        """Test that legal profile file exists."""
        assert profile_path.exists(), "legal-v1.0.yaml should exist"
    
    def test_profile_has_required_fields(self, profile_data: dict):
        """Test profile has required metadata fields."""
        assert "profile" in profile_data
        assert "id" in profile_data["profile"]
        assert "name" in profile_data["profile"]
        assert "version" in profile_data["profile"]
        assert "rules" in profile_data
    
    def test_profile_has_minimum_rules(self, profile_data: dict):
        """Test profile has at least 10 rules."""
        rules = profile_data.get("rules", [])
        assert len(rules) >= 10, f"Expected at least 10 rules, got {len(rules)}"
