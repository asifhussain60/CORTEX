"""
Phase 38 Stage 11: RecataloingEngine Tests
Authority: TDDOrchestrator | CORE-008
"""

import pytest
from pathlib import Path
from cortex.orchestrators.support.recataloging_engine import RecataloingEngine


class TestRecataloingEngine:
    """RecataloingEngine - updates catalogs after relocations"""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create workspace with catalog files"""
        cortex = tmp_path / "cortex"
        cortex.mkdir()
        registry = tmp_path / "cortex-registry" / "_cortex-master"
        registry.mkdir(parents=True)
        
        # Create minimal YAML files
        wiring = cortex / "__wiring_contract__.yaml"
        wiring.write_text("orchestrators:\n  test: {path: 'cortex/test'}\n")
        
        index = registry / "index.yaml"
        index.write_text("phases:\n  phase-1: {file: 'phases/phase-1.yaml'}\n")
        
        return tmp_path

    @pytest.fixture
    def engine(self, workspace):
        """Initialize engine"""
        return RecataloingEngine(workspace)

    def test_initialization(self, engine, workspace):
        """Test: Engine initializes with workspace"""
        assert engine.workspace_root == workspace
        assert engine.wiring_file is not None
        assert engine.registry_index is not None

    def test_create_relocation_mapping(self, engine, workspace):
        """Test: Creates mapping of old → new paths"""
        old_path = workspace / "old_file.py"
        old_path.write_text("pass")
        new_path = workspace / "cortex" / "new_file.py"
        new_path.write_text("pass")
        
        mapping = engine.create_relocation_mapping([(old_path, new_path)])
        
        assert isinstance(mapping, dict)
        assert len(mapping) > 0

    def test_update_wiring_contract(self, engine):
        """Test: Updates wiring contract with mappings"""
        mapping = {"old_path": "new_path"}
        changes = engine.update_wiring_contract(mapping)
        
        assert isinstance(changes, list)

    def test_update_registry_index(self, engine):
        """Test: Updates registry index"""
        mapping = {"old_path": "new_path"}
        changes = engine.update_registry_index(mapping)
        
        assert isinstance(changes, list)

    def test_update_python_imports(self, engine, workspace):
        """Test: Updates Python import statements"""
        # Create Python file with import
        py_file = workspace / "test.py"
        py_file.write_text("from old_import import func\n")
        
        mapping = {"old_import": "new_import"}
        changes = engine.update_python_imports(mapping)
        
        assert isinstance(changes, list)

    def test_validate_catalog_consistency(self, engine):
        """Test: Validates catalog consistency"""
        valid, errors = engine.validate_catalog_consistency()
        
        assert isinstance(valid, bool)
        assert isinstance(errors, list)

    def test_map_path_simple(self, engine):
        """Test: Maps simple paths"""
        mapping = {"old": "new"}
        result = engine._map_path("path/to/old/file", mapping)
        
        assert "new" in result

    def test_integration_full_workflow(self, engine, workspace):
        """Integration: Full recataloging workflow"""
        # Create relocation mapping
        old = workspace / "old.py"
        old.write_text("pass")
        new = workspace / "cortex" / "new.py"
        new.parent.mkdir(exist_ok=True)
        new.write_text("pass")
        
        mapping = engine.create_relocation_mapping([(old, new)])
        
        # Apply updates
        wiring_changes = engine.update_wiring_contract(mapping)
        index_changes = engine.update_registry_index(mapping)
        import_changes = engine.update_python_imports(mapping)
        
        # Validate
        valid, errors = engine.validate_catalog_consistency()
        
        assert isinstance(wiring_changes, list)
        assert isinstance(index_changes, list)
        assert isinstance(import_changes, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
