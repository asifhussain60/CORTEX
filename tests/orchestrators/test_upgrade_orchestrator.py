"""
Tests for UpgradeOrchestrator - differential upgrade system.

TDD Tests for intelligent version upgrades with augmentation strategy.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestUpgradeOrchestratorDownload:
    """Tests for downloading new versions."""

    def test_download_new_version(self, tmp_path):
        """Should download new version from GitHub/PyPI."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        with patch.object(orchestrator, '_download_from_github') as mock_download:
            mock_download.return_value = {"success": True, "path": tmp_path / "v7.3.0"}
            
            result = orchestrator.download_new_version("7.3.0")
            
            assert result["success"] is True

    def test_extract_release_notes(self, tmp_path):
        """Should extract release notes from CHANGELOG."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        # Create mock changelog
        changelog = tmp_path / "CHANGELOG.md"
        changelog.write_text("""
## [7.3.0] - 2026-01-21
### Added
- New CORE-030 rule
- Improved routing

### Fixed
- Memory leak in audit
""")
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        notes = orchestrator.extract_release_notes("7.3.0")
        
        assert "CORE-030" in str(notes)
        assert len(notes["added"]) >= 2


class TestUpgradeOrchestratorDiff:
    """Tests for computing upgrade diff."""

    def test_compute_upgrade_diff(self, tmp_path):
        """Should compute diff between versions."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        diff = orchestrator.compute_upgrade_diff(
            current_rules=["CORE-001", "CORE-008", "CORE-029"],
            new_rules=["CORE-001", "CORE-008", "CORE-029", "CORE-030"]
        )
        
        assert diff["new_rules"] == ["CORE-030"]
        assert diff["removed_rules"] == []
        assert diff["modified_rules"] == []

    def test_apply_delta_not_replace(self, tmp_path):
        """Should apply delta without replacing existing content."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        # Create existing tier0 rules
        tier0_dir = tmp_path / "cortex" / "core" / "governance"
        tier0_dir.mkdir(parents=True)
        (tier0_dir / "core-rules.yaml").write_text("""
rules:
  - id: CORE-001
    description: Existing rule
""")
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        result = orchestrator.apply_delta(
            new_rules=[{"id": "CORE-030", "description": "New rule"}],
            replace=False
        )
        
        assert result["success"] is True
        assert result["mode"] == "augment"

    def test_run_validation_tests(self, tmp_path):
        """Should run validation tests after upgrade."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        with patch.object(orchestrator, '_run_pytest') as mock_pytest:
            mock_pytest.return_value = {"passed": 100, "failed": 0}
            
            result = orchestrator.run_validation_tests()
            
            assert result["valid"] is True


class TestUpgradeOrchestratorAugmentation:
    """Tests for augmentation strategy."""

    def test_new_tier0_rules_append(self, tmp_path):
        """Should append new tier0 rules to existing."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        result = orchestrator.augment_tier0_rules(
            existing=["CORE-001", "CORE-029"],
            new=["CORE-030", "CORE-031"]
        )
        
        assert len(result["final_rules"]) == 4
        assert "CORE-001" in result["final_rules"]
        assert "CORE-030" in result["final_rules"]

    def test_tier1_rules_preserved(self, tmp_path):
        """Should preserve tier1 rules during upgrade."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        # Create tier1 rules
        tier1_dir = tmp_path / "cortex_brain" / "tier1"
        tier1_dir.mkdir(parents=True)
        (tier1_dir / "custom-rules.yaml").write_text("my_rule: preserve_this")
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        result = orchestrator.verify_tier1_preserved()
        
        assert result["preserved"] is True
        assert "custom-rules.yaml" in result["files"]

    def test_learned_patterns_merged(self, tmp_path):
        """Should merge learned patterns with new baselines."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        existing_patterns = {"CORE-008": 1247, "CORE-011": 982}
        new_patterns = {"CORE-030": 0, "CORE-011": 0}  # New baseline
        
        result = orchestrator.merge_learned_patterns(existing_patterns, new_patterns)
        
        # Existing preserved, new added
        assert result["CORE-008"] == 1247
        assert result["CORE-011"] == 982  # Preserved, not reset
        assert result["CORE-030"] == 0    # New baseline added

    def test_deprecated_rules_marked(self, tmp_path):
        """Should mark deprecated rules without deleting."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        result = orchestrator.mark_deprecated_rules(
            rules=["CORE-OLD-001"],
            version="7.3.0"
        )
        
        assert result["CORE-OLD-001"]["deprecated"] is True
        assert result["CORE-OLD-001"]["deprecated_in"] == "7.3.0"


class TestUpgradeOrchestratorZeroDowntime:
    """Tests for zero-downtime blue-green deployment."""

    def test_blue_green_parallel_run(self, tmp_path):
        """Should run old and new versions in parallel."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        result = orchestrator.start_blue_green("7.2.0", "7.3.0")
        
        assert result["blue"]["version"] == "7.2.0"
        assert result["green"]["version"] == "7.3.0"

    def test_validation_against_production(self, tmp_path):
        """Should validate new version against production workload."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        result = orchestrator.validate_production_workload(
            version="7.3.0",
            test_queries=["intent:build", "intent:review"]
        )
        
        assert result["validated"] is True

    def test_cutover_to_new_version(self, tmp_path):
        """Should switch traffic to new version."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        with patch.object(orchestrator, '_switch_active_version') as mock_switch:
            mock_switch.return_value = True
            
            result = orchestrator.cutover("7.3.0")
            
            assert result["success"] is True
            assert result["active_version"] == "7.3.0"

    def test_generate_upgrade_report(self, tmp_path):
        """Should generate post-upgrade report."""
        from cortex.orchestrators.upgrade_orchestrator import UpgradeOrchestrator
        
        orchestrator = UpgradeOrchestrator(tmp_path)
        
        report = orchestrator.generate_upgrade_report(
            from_version="7.2.0",
            to_version="7.3.0",
            changes={"new_rules": ["CORE-030"], "preserved": ["tier1/*"]}
        )
        
        assert "7.2.0" in report["from"]
        assert "7.3.0" in report["to"]
        assert "preserved" in report
