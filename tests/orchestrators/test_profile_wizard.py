"""
Tests for ProfileWizard - Quick-start wizard for governance profiles.

TDD Tests for project detection and profile suggestion.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestProfileWizardDetection:
    """Tests for project type detection."""

    def test_detect_finops_from_requirements(self, tmp_path):
        """Should detect FinOps project from pandas/numpy requirements."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        # Create requirements.txt with financial libraries
        requirements = tmp_path / "requirements.txt"
        requirements.write_text("pandas>=2.0\nnumpy>=1.24\nopenpyxl\nxlrd")
        
        wizard = ProfileWizard(tmp_path)
        project_type = wizard.detect_project_type()
        
        assert project_type == "finops"

    def test_detect_auth_from_structure(self, tmp_path):
        """Should detect Auth project from folder structure."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        # Create auth-related folder structure
        (tmp_path / "auth").mkdir()
        (tmp_path / "auth" / "session.py").write_text("# Session management")
        (tmp_path / "auth" / "jwt.py").write_text("# JWT handling")
        
        wizard = ProfileWizard(tmp_path)
        project_type = wizard.detect_project_type()
        
        assert project_type == "auth"

    def test_detect_ml_from_tensorflow(self, tmp_path):
        """Should detect ML project from tensorflow/torch requirements."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        requirements = tmp_path / "requirements.txt"
        requirements.write_text("tensorflow>=2.12\nkeras\nscikit-learn")
        
        wizard = ProfileWizard(tmp_path)
        project_type = wizard.detect_project_type()
        
        assert project_type == "ml"

    def test_detect_devops_from_ci_cd_files(self, tmp_path):
        """Should detect DevOps project from CI/CD configuration."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        # Create CI/CD configuration
        github_dir = tmp_path / ".github" / "workflows"
        github_dir.mkdir(parents=True)
        (github_dir / "ci.yml").write_text("name: CI Pipeline")
        
        wizard = ProfileWizard(tmp_path)
        project_type = wizard.detect_project_type()
        
        assert project_type == "devops"


class TestProfileWizardSuggestion:
    """Tests for profile suggestion."""

    def test_suggest_appropriate_profile(self, tmp_path):
        """Should suggest appropriate profile based on detection."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        requirements = tmp_path / "requirements.txt"
        requirements.write_text("pandas\nfinance-tools")
        
        wizard = ProfileWizard(tmp_path)
        suggestion = wizard.suggest_profile()
        
        assert suggestion["profile"] == "finops-v1.0"
        assert suggestion["confidence"] > 0.7

    def test_suggest_with_explanation(self, tmp_path):
        """Should provide explanation for suggestion."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        requirements = tmp_path / "requirements.txt"
        requirements.write_text("tensorflow\nkeras\nnumpy")
        
        wizard = ProfileWizard(tmp_path)
        suggestion = wizard.suggest_profile()
        
        assert "ml" in suggestion["profile"]
        assert "explanation" in suggestion
        assert len(suggestion["explanation"]) > 0


class TestProfileWizardCustomization:
    """Tests for profile customization."""

    def test_customize_profile_rules(self, tmp_path):
        """Should allow customizing profile rules."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        wizard = ProfileWizard(tmp_path)
        
        customization = wizard.customize_profile(
            profile="finops-v1.0",
            add_rules=["CUSTOM-001"],
            remove_rules=["FIN-003"]
        )
        
        assert "CUSTOM-001" in customization["rules"]
        assert "FIN-003" not in customization["rules"]

    def test_apply_profile_to_tier1(self, tmp_path):
        """Should apply profile to tier1 directory."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        wizard = ProfileWizard(tmp_path)
        result = wizard.apply_profile("finops-v1.0")
        
        assert result["success"] is True
        tier1_file = tmp_path / "cortex_brain" / "tier1" / "domain-rules.yaml"
        assert tier1_file.exists()


class TestProfileWizardWizardFlow:
    """Tests for complete wizard flow."""

    def test_full_wizard_flow(self, tmp_path):
        """Should complete full wizard flow."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        # Setup project
        requirements = tmp_path / "requirements.txt"
        requirements.write_text("pandas\nnumpy\nmatplotlib")
        
        wizard = ProfileWizard(tmp_path)
        
        # Detect
        project_type = wizard.detect_project_type()
        
        # Suggest
        suggestion = wizard.suggest_profile()
        
        # Apply
        result = wizard.apply_profile(suggestion["profile"])
        
        assert project_type in ["finops", "general"]
        assert result["success"] is True

    def test_list_available_profiles(self, tmp_path):
        """Should list all available profiles."""
        from cortex.orchestrators.profile_wizard import ProfileWizard
        
        wizard = ProfileWizard(tmp_path)
        profiles = wizard.list_available_profiles()
        
        assert len(profiles) >= 6
        assert any("finops" in p["name"].lower() for p in profiles)
        assert any("auth" in p["name"].lower() for p in profiles)
