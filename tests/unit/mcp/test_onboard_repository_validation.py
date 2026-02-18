"""
Test validation in onboard_repository_tool to prevent creating directories with function repr.

Authority: CORE-008 (TDD), Fix for root directory pollution
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.mcp.tools.onboard_repository import onboard_repository_tool


class TestOnboardRepositoryValidation:
    """Test input validation for onboard_repository_tool."""

    def test_rejects_function_object_as_test_output_dir(self, tmp_path):
        """Should reject function object passed as test_output_dir."""
        # Create a dummy function to simulate the fixture reference issue
        def dummy_fixture():
            return tmp_path
        
        with pytest.raises(ValueError, match="test_output_dir must be a string or Path"):
            onboard_repository_tool(
                repository_path=str(tmp_path),
                test_mode=True,
                test_output_dir=dummy_fixture,  # Function object instead of path
                generate_artifacts=True
            )

    def test_rejects_function_repr_string_as_test_output_dir(self, tmp_path):
        """Should reject string that looks like function repr."""
        with pytest.raises(ValueError, match="appears to be a function object"):
            onboard_repository_tool(
                repository_path=str(tmp_path),
                test_mode=True,
                test_output_dir="<function test_output_dir at 0x10b57a280>",
                generate_artifacts=True
            )

    def test_accepts_valid_path_string_as_test_output_dir(self, tmp_path):
        """Should accept valid path string."""
        test_repo = tmp_path / "test_repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Mock the onboarding analysis to avoid full execution
        with patch("cortex.mcp.tools.onboard_repository.OnboardingOrchestrator") as mock_orchestrator:
            mock_instance = MagicMock()
            mock_instance.onboard_repository.return_value = {
                "status": "success",
                "repository_path": str(test_repo),
                "analysis": {}
            }
            mock_orchestrator.return_value = mock_instance
            
            result = onboard_repository_tool(
                repository_path=str(test_repo),
                test_mode=True,
                test_output_dir=str(output_dir),
                generate_artifacts=True,
                capture_learning=False,
                apply_brain_enhancement=False
            )
            
            assert result["status"] == "success"

    def test_accepts_path_object_as_test_output_dir(self, tmp_path):
        """Should accept Path object."""
        test_repo = tmp_path / "test_repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        
        # Mock the onboarding analysis to avoid full execution
        with patch("cortex.mcp.tools.onboard_repository.OnboardingOrchestrator") as mock_orchestrator:
            mock_instance = MagicMock()
            mock_instance.onboard_repository.return_value = {
                "status": "success",
                "repository_path": str(test_repo),
                "analysis": {}
            }
            mock_orchestrator.return_value = mock_instance
            
            result = onboard_repository_tool(
                repository_path=str(test_repo),
                test_mode=True,
                test_output_dir=output_dir,  # Path object
                generate_artifacts=True,
                capture_learning=False,
                apply_brain_enhancement=False
            )
            
            assert result["status"] == "success"

    def test_production_mode_ignores_test_output_dir(self, tmp_path):
        """In production mode, test_output_dir should be ignored."""
        test_repo = tmp_path / "test_repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")
        
        # Mock the onboarding analysis
        with patch("cortex.mcp.tools.onboard_repository.OnboardingOrchestrator") as mock_orchestrator:
            mock_instance = MagicMock()
            mock_instance.onboard_repository.return_value = {
                "status": "success",
                "repository_path": str(test_repo),
                "analysis": {}
            }
            mock_orchestrator.return_value = mock_instance
            
            # Even with a bad test_output_dir, should work in production mode
            result = onboard_repository_tool(
                repository_path=str(test_repo),
                test_mode=False,  # Production mode
                test_output_dir="<function bad>",  # Should be ignored
                generate_artifacts=False,
                capture_learning=False,
                apply_brain_enhancement=False
            )
            
            assert result["status"] == "success"
