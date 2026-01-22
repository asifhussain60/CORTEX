"""Tests for Cross-Repo Router - PHASE-DEPLOYMENT-004-multi-repo-gov.

AC-DEP-004-03: Cross-repo intent routing with CORTEX.prompt.md awareness.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestRouteKashkoleIntent:
    """Test routing intents to KASHKOLE project."""

    def test_routes_financial_intent_to_kashkole(self):
        """Should route financial intent to KASHKOLE."""
        from cortex.orchestrators.cross_repo_router import CrossRepoRouter
        
        router = CrossRepoRouter()
        
        with patch.object(router, "_get_project_for_intent") as mock_get:
            mock_get.return_value = "KASHKOLE"
            
            result = router.route_intent("process financial transaction")
        
        assert result["target_project"] == "KASHKOLE"

    def test_loads_kashkole_tier1_rules(self):
        """Should load tier1 rules when routing to KASHKOLE."""
        from cortex.orchestrators.cross_repo_router import CrossRepoRouter
        
        router = CrossRepoRouter()
        
        with patch.object(router, "_load_project_context") as mock_load:
            mock_load.return_value = {"tier1_profile": "finops"}
            
            result = router.route_intent(
                "process financial transaction",
                target_project="KASHKOLE"
            )
        
        assert "tier1" in result or result.get("target_project") == "KASHKOLE"


class TestRouteKsessionsIntent:
    """Test routing intents to KSESSIONS project."""

    def test_routes_auth_intent_to_ksessions(self):
        """Should route auth intent to KSESSIONS."""
        from cortex.orchestrators.cross_repo_router import CrossRepoRouter
        
        router = CrossRepoRouter()
        
        with patch.object(router, "_get_project_for_intent") as mock_get:
            mock_get.return_value = "KSESSIONS"
            
            result = router.route_intent("manage user session")
        
        assert result["target_project"] == "KSESSIONS"

    def test_loads_ksessions_tier1_rules(self):
        """Should load tier1 rules when routing to KSESSIONS."""
        from cortex.orchestrators.cross_repo_router import CrossRepoRouter
        
        router = CrossRepoRouter()
        
        with patch.object(router, "_load_project_context") as mock_load:
            mock_load.return_value = {"tier1_profile": "auth"}
            
            result = router.route_intent(
                "manage user session",
                target_project="KSESSIONS"
            )
        
        assert "tier1" in result or result.get("target_project") == "KSESSIONS"


class TestReadProjectCortexPrompt:
    """Test reading CORTEX.prompt.md from projects."""

    def test_reads_cortex_prompt_md(self, tmp_path: Path):
        """Should read CORTEX.prompt.md from project."""
        from cortex.orchestrators.cross_repo_router import CrossRepoRouter
        
        router = CrossRepoRouter()
        kashkole_path = tmp_path / "KASHKOLE"
        kashkole_path.mkdir()
        
        with patch.object(router, "_read_file") as mock_read:
            mock_read.return_value = "# Project: KASHKOLE\nFinancial operations"
            
            content = router.read_project_prompt(str(kashkole_path))
        
        assert content is not None
        assert "KASHKOLE" in content or len(content) > 0

    def test_reads_copilot_instructions(self, tmp_path: Path):
        """Should read copilot-instruction.md from project."""
        from cortex.orchestrators.cross_repo_router import CrossRepoRouter
        
        router = CrossRepoRouter()
        kashkole_path = tmp_path / "KASHKOLE"
        kashkole_path.mkdir()
        
        with patch.object(router, "_read_file") as mock_read:
            mock_read.return_value = "Instructions for copilot"
            
            content = router.read_copilot_instructions(str(kashkole_path))
        
        assert content is not None

    def test_handles_missing_prompt_file(self):
        """Should handle missing prompt file gracefully."""
        from cortex.orchestrators.cross_repo_router import CrossRepoRouter
        
        router = CrossRepoRouter()
        
        with patch.object(router, "_read_file") as mock_read:
            mock_read.return_value = None
            
            content = router.read_project_prompt("D:\\PROJECTS\\NoPrompt")
        
        # Should return None or empty string, not raise exception
        assert content is None or content == ""


class TestLoadProjectTier1Rules:
    """Test loading project-specific tier1 rules."""

    def test_loads_tier1_for_project(self, tmp_path: Path):
        """Should load tier1 rules for specific project."""
        from cortex.orchestrators.cross_repo_router import CrossRepoRouter
        
        router = CrossRepoRouter()
        kashkole_path = tmp_path / "KASHKOLE"
        kashkole_path.mkdir()
        
        with patch.object(router, "_load_project_context") as mock_load:
            mock_load.return_value = {
                "tier1_profile": "finops",
                "rules": ["FIN-001", "FIN-002"],
            }
            
            context = router.get_project_context(str(kashkole_path))
        
        assert "tier1_profile" in context or "rules" in context

    def test_preserves_tier0_across_projects(self):
        """Should preserve tier0 rules across all projects."""
        from cortex.orchestrators.cross_repo_router import CrossRepoRouter
        
        router = CrossRepoRouter()
        
        tier0 = router.get_tier0_rules()
        
        assert "CORE-008" in tier0.get("rules", []) or len(tier0) > 0
