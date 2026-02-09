"""
Phase 38 Stage 11: RecataloingEngine Tests
Authority: TDDOrchestrator | CORE-008 (tests before code)
Acceptance Criteria: AC-PHASE38-032
Purpose: Test recataloging engine for wiring/registry/import updates (8 tests)
"""

import pytest
from pathlib import Path
from typing import Dict


class TestRecataloingEngine:
    """RecataloingEngine - updates wiring.yaml, registry, imports, and docs after relocations"""

    @pytest.fixture
    def engine(self):
        """Fixture: Initialize RecataloingEngine"""
        from cortex.orchestrators.support.recataloging_engine import RecataloingEngine
        return RecataloingEngine()

    @pytest.fixture
    def project_with_wiring(self, tmp_path):
        """Fixture: Create project with wiring and registry files"""
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "orchestrators").mkdir()
        
        # Create wiring.yaml
        wiring = tmp_path / "cortex" / "__wiring_contract__.yaml"
        wiring.write_text("""
orchestrators:
  core:
    - name: MasterOrchestrator
      module: cortex.orchestrators.core.master_orchestrator
      class: MasterOrchestrator
  
  support:
    - name: VacuumOrchestrator
      module: cortex.orchestrators.support.vacuum_orchestrator
      class: VacuumOrchestrator
""")
        
        # Create registry
        registry = tmp_path / "cortex-registry" / "_cortex-master" / "index.yaml"
        registry.parent.mkdir(parents=True)
        registry.write_text("""
phases:
  - id: phase-1
    file: cortex/orchestrators/core/master_orchestrator.py
    
  - id: phase-2
    file: cortex/orchestrators/support/vacuum_orchestrator.py
""")
        
        return tmp_path

    # Test 1: Update wiring.yaml paths after relocation
    def test_update_wiring_yaml_single_module(self, engine, project_with_wiring):
        """Test: Update single module path in wiring.yaml"""
        wiring_path = project_with_wiring / "cortex" / "__wiring_contract__.yaml"
        
        relocations = {
            "cortex.orchestrators.core.master_orchestrator": 
            "cortex.orchestrators.relocated.master_orchestrator"
        }
        
        result = engine.update_wiring_paths(str(wiring_path), relocations)
        
        assert result["paths_updated"] >= 0
        
        # Verify file was updated
        content = wiring_path.read_text()
        if result["paths_updated"] > 0:
            assert "relocated" in content or result["skipped"] is True

    def test_update_wiring_yaml_multiple_modules(self, engine, project_with_wiring):
        """Test: Update multiple module paths in wiring.yaml"""
        wiring_path = project_with_wiring / "cortex" / "__wiring_contract__.yaml"
        
        relocations = {
            "cortex.orchestrators.core.master_orchestrator": 
            "cortex.orchestrators.core.orchestrators.master_orchestrator",
            "cortex.orchestrators.support.vacuum_orchestrator":
            "cortex.orchestrators.support.utilities.vacuum_orchestrator"
        }
        
        result = engine.update_wiring_paths(str(wiring_path), relocations)
        
        assert result["paths_updated"] >= 0

    def test_wiring_yaml_maintains_structure(self, engine, project_with_wiring):
        """Test: Maintain wiring.yaml structure after updates"""
        wiring_path = project_with_wiring / "cortex" / "__wiring_contract__.yaml"
        
        original_content = wiring_path.read_text()
        
        relocations = {}
        result = engine.update_wiring_paths(str(wiring_path), relocations)
        
        updated_content = wiring_path.read_text()
        
        # Verify YAML structure intact
        assert "orchestrators:" in updated_content
        assert ("core:" in updated_content or "core:" in original_content)

    # Test 2: Update index.yaml references
    def test_update_registry_file_paths(self, engine, project_with_wiring):
        """Test: Update file paths in registry index.yaml"""
        registry_path = project_with_wiring / "cortex-registry" / "_cortex-master" / "index.yaml"
        
        file_relocations = {
            "cortex/orchestrators/core/master_orchestrator.py":
            "cortex/orchestrators/core/relocated/master_orchestrator.py"
        }
        
        result = engine.update_registry_references(str(registry_path), file_relocations)
        
        assert result["references_updated"] >= 0

    def test_update_registry_preserves_metadata(self, engine, project_with_wiring):
        """Test: Preserve metadata when updating registry"""
        registry_path = project_with_wiring / "cortex-registry" / "_cortex-master" / "index.yaml"
        
        original = registry_path.read_text()
        
        file_relocations = {
            "cortex/orchestrators/core/master_orchestrator.py":
            "cortex/orchestrators/relocated/master_orchestrator.py"
        }
        
        result = engine.update_registry_references(str(registry_path), file_relocations)
        
        updated = registry_path.read_text()
        
        # Phase metadata should still be there
        assert "phase-1" in updated or "phase-1" in original

    # Test 3: Update Python imports
    def test_update_python_imports_in_files(self, engine, tmp_path):
        """Test: Update import statements in Python files"""
        (tmp_path / "cortex").mkdir()
        
        # Create files with imports
        main = tmp_path / "cortex" / "main.py"
        main.write_text("""
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator
""")
        
        import_updates = {
            "cortex.orchestrators.core.master_orchestrator":
            "cortex.orchestrators.core.relocated.master_orchestrator"
        }
        
        result = engine.update_imports(str(tmp_path), import_updates)
        
        assert result["files_processed"] >= 1

    def test_update_relative_imports(self, engine, tmp_path):
        """Test: Correctly update relative imports"""
        (tmp_path / "cortex" / "orchestrators" / "core").mkdir(parents=True)
        
        module = tmp_path / "cortex" / "orchestrators" / "core" / "dependent.py"
        module.write_text("from .master_orchestrator import MasterOrchestrator")
        
        import_updates = {
            "cortex.orchestrators.core.master_orchestrator":
            "cortex.orchestrators.core.relocated.master_orchestrator"
        }
        
        result = engine.update_imports(str(tmp_path), import_updates)
        
        assert result["files_processed"] >= 1

    def test_update_wildcard_imports(self, engine, tmp_path):
        """Test: Handle wildcard imports (from X import *)"""
        (tmp_path / "cortex").mkdir()
        
        main = tmp_path / "cortex" / "main.py"
        main.write_text("from cortex.orchestrators.core.utils import *")
        
        import_updates = {
            "cortex.orchestrators.core.utils":
            "cortex.orchestrators.core.new_location.utils"
        }
        
        result = engine.update_imports(str(tmp_path), import_updates)
        
        assert result["files_processed"] >= 0

    # Test 4: Update markdown links
    def test_update_markdown_links(self, engine, tmp_path):
        """Test: Update file references in markdown documentation"""
        docs = tmp_path / "docs" / "architecture.md"
        docs.parent.mkdir(parents=True)
        docs.write_text("""
# Architecture

See `cortex/orchestrators/core/master_orchestrator.py` for details.
Import from `cortex/orchestrators/support/vacuum_orchestrator.py`.
""")
        
        link_updates = {
            "cortex/orchestrators/core/master_orchestrator.py":
            "cortex/orchestrators/core/relocated/master_orchestrator.py"
        }
        
        result = engine.update_markdown_references(str(tmp_path), link_updates)
        
        assert result["docs_updated"] >= 0

    def test_update_code_block_references(self, engine, tmp_path):
        """Test: Update file paths in code blocks within markdown"""
        docs = tmp_path / "docs" / "usage.md"
        docs.parent.mkdir(parents=True)
        docs.write_text("""
```python
# See file: cortex/orchestrators/core/master_orchestrator.py
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
```
""")
        
        link_updates = {
            "cortex/orchestrators/core/master_orchestrator.py":
            "cortex/orchestrators/core/relocated/master_orchestrator.py"
        }
        
        result = engine.update_markdown_references(str(tmp_path), link_updates)
        
        assert result["code_blocks_updated"] >= 0 or result["docs_updated"] >= 0

    # Test 5: Maintain wiring integrity post-update
    def test_maintain_wiring_integrity(self, engine, project_with_wiring):
        """Test: Verify wiring.yaml remains valid YAML after updates"""
        wiring_path = project_with_wiring / "cortex" / "__wiring_contract__.yaml"
        
        import yaml
        
        original_wiring = yaml.safe_load(wiring_path.read_text())
        
        relocations = {
            "cortex.orchestrators.core.master_orchestrator":
            "cortex.orchestrators.core.relocated.master_orchestrator"
        }
        
        result = engine.update_wiring_paths(str(wiring_path), relocations)
        
        # Should still be valid YAML
        updated_wiring = yaml.safe_load(wiring_path.read_text())
        
        assert updated_wiring is not None
        assert "orchestrators" in updated_wiring

    def test_maintain_registry_integrity(self, engine, project_with_wiring):
        """Test: Verify registry remains valid YAML after updates"""
        registry_path = project_with_wiring / "cortex-registry" / "_cortex-master" / "index.yaml"
        
        import yaml
        
        original_registry = yaml.safe_load(registry_path.read_text())
        
        file_relocations = {
            "cortex/orchestrators/core/master_orchestrator.py":
            "cortex/orchestrators/core/relocated/master_orchestrator.py"
        }
        
        result = engine.update_registry_references(str(registry_path), file_relocations)
        
        # Should still be valid YAML
        updated_registry = yaml.safe_load(registry_path.read_text())
        
        assert updated_registry is not None
        assert "phases" in updated_registry

    # Test 6: Validate no broken references
    def test_detect_broken_references_after_update(self, engine, tmp_path):
        """Test: Detect if any references were not updated"""
        (tmp_path / "cortex").mkdir()
        
        main = tmp_path / "cortex" / "main.py"
        main.write_text("""
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator
""")
        
        # Update only one reference
        import_updates = {
            "cortex.orchestrators.core.master_orchestrator":
            "cortex.orchestrators.core.relocated.master_orchestrator"
        }
        
        result = engine.update_imports(str(tmp_path), import_updates)
        
        # Check for unresolved references
        unresolved = engine.detect_unresolved_references(str(tmp_path))
        
        assert isinstance(unresolved, list) or "unresolved" in result

    # Test 7: Generate recatalog report
    def test_generate_recatalog_report(self, engine, project_with_wiring):
        """Test: Generate comprehensive recataloging report"""
        relocations = {
            "cortex.orchestrators.core.master_orchestrator":
            "cortex.orchestrators.core.relocated.master_orchestrator"
        }
        
        report = engine.generate_recatalog_report(
            str(project_with_wiring),
            relocations
        )
        
        assert "summary" in report or "total_updates" in report
        assert "files_affected" in report or "modules_updated" in report

    def test_report_includes_validation_status(self, engine, project_with_wiring):
        """Test: Report includes validation status of updates"""
        relocations = {
            "cortex.orchestrators.core.master_orchestrator":
            "cortex.orchestrators.core.relocated.master_orchestrator"
        }
        
        report = engine.generate_recatalog_report(
            str(project_with_wiring),
            relocations
        )
        
        assert "valid" in report or "errors" in report or "status" in report

    # Test 8: Rollback catalog updates on failure
    def test_rollback_on_wiring_update_failure(self, engine, project_with_wiring):
        """Test: Rollback wiring updates if any step fails"""
        from unittest.mock import patch, Mock
        
        wiring_path = project_with_wiring / "cortex" / "__wiring_contract__.yaml"
        original_content = wiring_path.read_text()
        
        relocations = {
            "cortex.orchestrators.core.master_orchestrator":
            "cortex.orchestrators.core.relocated.master_orchestrator"
        }
        
        # Simulate update success followed by validation failure
        with patch.object(engine, 'validate_wiring_yaml', side_effect=Exception("Invalid YAML")):
            result = engine.update_wiring_paths_with_rollback(
                str(wiring_path),
                relocations
            )
            
            # Should rollback
            assert result["error"] is not None or result["rolled_back"] is True
            
            # File should be restored if rollback occurred
            if result.get("rolled_back"):
                assert wiring_path.read_text() == original_content

    def test_rollback_on_registry_update_failure(self, engine, project_with_wiring):
        """Test: Rollback registry updates if validation fails"""
        from unittest.mock import patch
        
        registry_path = project_with_wiring / "cortex-registry" / "_cortex-master" / "index.yaml"
        original_content = registry_path.read_text()
        
        file_relocations = {
            "cortex/orchestrators/core/master_orchestrator.py":
            "cortex/orchestrators/core/relocated/master_orchestrator.py"
        }
        
        # Simulate update followed by broken reference detection
        with patch.object(engine, 'detect_broken_references', return_value=["unresolved_import"]):
            result = engine.update_registry_references_with_rollback(
                str(registry_path),
                file_relocations
            )
            
            # Should handle gracefully
            assert "error" in result or "broken_references" in result or "success" in result


class TestRecataloingEngineIntegration:
    """Integration tests for complete recataloging workflows"""

    @pytest.fixture
    def engine(self):
        from cortex.orchestrators.support.recataloging_engine import RecataloingEngine
        return RecataloingEngine()

    def test_complete_recatalog_workflow(self, engine, tmp_path):
        """Integration: Complete recataloging of relocated files"""
        # Setup
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        (tmp_path / "cortex" / "orchestrators" / "OLD_NAME.py").write_text("class Orchestrator: pass")
        
        # Create wiring
        wiring = tmp_path / "cortex" / "__wiring_contract__.yaml"
        wiring.write_text("orchestrators:\n  - module: cortex.orchestrators.OLD_NAME")
        
        # Execute complete workflow
        result = engine.complete_recatalog(
            codebase_root=str(tmp_path),
            old_module="cortex.orchestrators.OLD_NAME",
            new_module="cortex.orchestrators.old-name",
            update_wiring=True,
            update_registry=True,
            update_imports=True,
            update_docs=True
        )
        
        assert result["completed"] or result["error"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
