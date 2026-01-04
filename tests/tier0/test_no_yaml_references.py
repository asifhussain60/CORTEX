"""
SKULL Test: No YAML References in Source Code
Validates all YAML file references removed from src/.

C50-19: Brain Data Source Cutover  
Phase 2: Remove YAML Read Paths
"""
import pytest
import subprocess
from pathlib import Path


class TestNoYAMLReferences:
    """Test suite for YAML reference removal."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures."""
        self.src_dir = Path("src")
        self.yaml_files = [
            "conversation-context.jsonl",
            "knowledge-graph.yaml",
            "development-context.yaml"
        ]
    
    def test_no_yaml_references_in_source(self):
        """Verify no YAML file references in production code (Phase 2 DoD)."""
        for yaml_file in self.yaml_files:
            result = subprocess.run(
                ["grep", "-r", yaml_file, str(self.src_dir)],
                capture_output=True,
                text=True
            )
            
            # Exit code 1 = no matches (good)
            # Exit code 0 = matches found (bad)
            assert result.returncode == 1, \
                f"Found {yaml_file} references in src/:\n{result.stdout}"
    
    def test_database_references_exist(self):
        """Verify database references exist in code (Phase 2 DoD)."""
        db_files = ["working_memory.db", "knowledge_graph.db"]
        
        for db_file in db_files:
            result = subprocess.run(
                ["grep", "-r", db_file, str(self.src_dir)],
                capture_output=True,
                text=True
            )
            
            # Should find database references
            assert result.returncode == 0, \
                f"No {db_file} references found in src/ (should exist)"
            assert len(result.stdout.strip()) > 0, \
                f"{db_file} should be referenced in code"
    
    def test_tier0_integrity_checker_uses_db(self):
        """Verify integrity_checker.py uses database paths."""
        file_path = self.src_dir / "tier0" / "integrity_checker.py"
        
        if not file_path.exists():
            pytest.skip("integrity_checker.py not found")
        
        content = file_path.read_text()
        
        # Should have database references, not YAML
        assert "working_memory.db" in content or "knowledge_graph.db" in content, \
            "integrity_checker.py should reference databases"
        assert "knowledge-graph.yaml" not in content, \
            "integrity_checker.py should not reference YAML"
    
    def test_tier0_tier_validator_uses_db(self):
        """Verify tier_validator.py uses database paths."""
        file_path = self.src_dir / "tier0" / "tier_validator.py"
        
        if not file_path.exists():
            pytest.skip("tier_validator.py not found")
        
        content = file_path.read_text()
        
        # Should have database references, not YAML
        assert "knowledge_graph.db" in content or "working_memory.db" in content, \
            "tier_validator.py should reference databases"
        assert "knowledge-graph.yaml" not in content, \
            "tier_validator.py should not reference YAML"
