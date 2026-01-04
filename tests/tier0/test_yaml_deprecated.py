"""
SKULL Test: YAML Deprecated
Validates YAML files have been archived and removed from cortex-brain root.

C50-19: Brain Data Source Cutover
Phase 1: Archive YAML Files
"""
import pytest
from pathlib import Path


class TestYAMLDeprecated:
    """Test suite for YAML file archival."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.brain_root = Path("cortex-brain")
        self.archive_dir = self.brain_root / "archives/yaml-deprecated-2026-01-04"
    
    def test_yaml_files_archived(self):
        """Verify YAML files moved to archives (Phase 1 DoD)."""
        # YAML files should NOT exist in root
        assert not (self.brain_root / "conversation-context.jsonl").exists(), \
            "conversation-context.jsonl should be archived"
        assert not (self.brain_root / "knowledge-graph.yaml").exists(), \
            "knowledge-graph.yaml should be archived"
        assert not (self.brain_root / "development-context.yaml").exists(), \
            "development-context.yaml should be archived"
        
        # YAML files SHOULD exist in archives
        assert self.archive_dir.exists(), "Archive directory should exist"
        assert (self.archive_dir / "conversation-context.jsonl").exists(), \
            "conversation-context.jsonl should be in archives"
        assert (self.archive_dir / "knowledge-graph.yaml").exists(), \
            "knowledge-graph.yaml should be in archives"
        assert (self.archive_dir / "development-context.yaml").exists(), \
            "development-context.yaml should be in archives"
    
    def test_archive_readme_exists(self):
        """Verify deprecation notice created (Phase 1 DoD)."""
        readme = self.archive_dir / "README.md"
        assert readme.exists(), "Archive README.md should exist"
        
        content = readme.read_text()
        assert "DEPRECATED" in content, "README should mention deprecation"
        assert "2026-01-04" in content, "README should have deprecation date"
        assert "working_memory.db" in content, "README should mention replacement DB"
        assert "knowledge_graph.db" in content, "README should mention replacement DB"
