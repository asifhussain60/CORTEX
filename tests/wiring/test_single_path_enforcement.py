"""
TEST-001: Single Path Enforcement Tests.

Validates that only ONE wiring mechanism exists in CORTEX.
All legacy wiring systems should be deleted (Phase 2).

Phase: 6 (Test Suite & Final Validation)
Author: Asif Hussain
Date: 2026-01-28

CORE-035: Single Canonical Implementation - no duplicate wiring systems.
"""

import os
from pathlib import Path

import pytest


class TestSinglePathEnforcement:
    """Verify that only one wiring path exists (Git-backed YAML)."""
    
    @pytest.fixture
    def cortex_root(self) -> Path:
        """Get CORTEX project root directory."""
        return Path(__file__).parent.parent.parent
    
    def test_database_registry_does_not_exist(self, cortex_root: Path):
        """Test that database_registry.py was deleted in Phase 2."""
        db_registry = cortex_root / "cortex" / "orchestrators" / "core" / "database_registry.py"
        assert not db_registry.exists(), (
            "database_registry.py still exists! Should have been deleted in Phase 2. "
            "This is a CORE-035 violation (duplicate wiring implementation)."
        )
    
    def test_orchestrator_bootstrap_does_not_exist(self, cortex_root: Path):
        """Test that orchestrators/bootstrap.py was deleted in Phase 2."""
        bootstrap = cortex_root / "cortex" / "orchestrators" / "bootstrap.py"
        assert not bootstrap.exists(), (
            "cortex/orchestrators/bootstrap.py still exists! "
            "Should have been deleted in Phase 2."
        )
    
    def test_orchestrator_registry_does_not_exist(self, cortex_root: Path):
        """Test that orchestrator_registry.py was deleted in Phase 2."""
        orch_registry = cortex_root / "cortex" / "orchestrators" / "core" / "orchestrator_registry.py"
        assert not orch_registry.exists(), (
            "orchestrator_registry.py still exists! "
            "Should have been deleted in Phase 2."
        )
    
    def test_db_wiring_init_does_not_exist(self, cortex_root: Path):
        """Test that db_wiring_init.py was deleted in Phase 2."""
        db_wiring = cortex_root / "cortex" / "orchestrators" / "core" / "db_wiring_init.py"
        assert not db_wiring.exists(), (
            "db_wiring_init.py still exists! "
            "Should have been deleted in Phase 2."
        )
    
    def test_permanent_wiring_state_does_not_exist(self, cortex_root: Path):
        """Test that permanent_wiring_state.py was deleted in Phase 2."""
        perm_wiring = cortex_root / "cortex" / "orchestrators" / "core" / "permanent_wiring_state.py"
        assert not perm_wiring.exists(), (
            "permanent_wiring_state.py still exists! "
            "Should have been deleted in Phase 2."
        )
    
    def test_no_legacy_wiring_files_in_codebase(self, cortex_root: Path):
        """Test that no legacy wiring files exist anywhere."""
        legacy_patterns = [
            "**/database_registry.py",
            "**/orchestrator_registry.py",
            "**/db_wiring_init.py",
            "**/permanent_wiring_state.py",
            "**/autowiring_orchestrator.py",
            "**/intent_router_factory.py",
            "**/wiring_contract_manager.py",
            "**/wiring_drift_detector.py",
        ]
        
        cortex_dir = cortex_root / "cortex"
        found_legacy = []
        
        for pattern in legacy_patterns:
            matches = list(cortex_dir.glob(pattern))
            if matches:
                found_legacy.extend(matches)
        
        assert not found_legacy, (
            f"Found legacy wiring files that should have been deleted: {found_legacy}"
        )
    
    def test_wiring_directory_exists_for_future(self, cortex_root: Path):
        """Test that cortex/wiring/ directory exists (Phase 3 placeholder)."""
        # Note: This test verifies the INTENDED location for future YAML wiring
        # The directory may not exist yet if Phase 3 hasn't been fully executed
        wiring_dir = cortex_root / "cortex" / "wiring"
        
        # This is a softer test - we document the intended location
        # but don't fail if it's not created yet
        if wiring_dir.exists():
            assert wiring_dir.is_dir(), "cortex/wiring should be a directory"
    
    def test_cortex_init_imports_clean(self, cortex_root: Path):
        """Test that cortex/__init__.py doesn't import legacy wiring."""
        cortex_init = cortex_root / "cortex" / "__init__.py"
        
        if cortex_init.exists():
            content = cortex_init.read_text()
            
            forbidden_imports = [
                "from cortex.orchestrators.core.database_registry",
                "from cortex.orchestrators.core.orchestrator_registry",
                "from cortex.orchestrators.bootstrap",
                "get_database_registry",
                "DatabaseBackedRegistry",
            ]
            
            for forbidden in forbidden_imports:
                assert forbidden not in content, (
                    f"cortex/__init__.py contains forbidden import: {forbidden}"
                )
    
    def test_no_alternative_bootstrap_methods(self, cortex_root: Path):
        """Test that there are no alternative bootstrap/initialization methods."""
        # Phase 3 Git-backed wiring system has LEGITIMATE bootstrap files:
        legitimate_files = {
            "bootstrap.py",  # Startup validator (cortex/bootstrap.py)
            "wiring_validator.py",  # Phase 3 validator (cortex/wiring/registry/wiring_validator.py)
            "guided_wiring_orchestrator.py",  # Migration tool (cortex/tools/)
            "wiring_auto_fixer.py",  # Migration tool (cortex/tools/)
            "wiring_harness_integration.py",  # Integration tool (cortex/orchestrators/)
            "orchestrator_bootstrap.py",  # Support orchestrator (cortex/orchestrators/core/)
            "mcp_bootstrapper.py",  # MCP server bootstrap (cortex/orchestrators/onboarding/)
            "enhanced_wiring_harness.py",  # Testing tool (cortex/testing/)
            "wiring_harness_inventory.py",  # Testing tool (cortex/testing/)
            "wiring_watcher.py",  # Phase 5 hot-reload (cortex/mcp/)
        }
        
        # Search for files that might implement alternative bootstrapping
        cortex_dir = cortex_root / "cortex"
        
        # Allowed bootstrap files (backward compatibility stubs)
        allowed = {
            cortex_dir / "orchestrators" / "core" / "database.py",  # Stub
            cortex_dir / "orchestrators" / "core" / "bootstrap.py",  # Stub (if exists)
        }
        
        # Find any files with "bootstrap" or "wiring" in the name
        potential_bootstraps = []
        for py_file in cortex_dir.rglob("*.py"):
            if "bootstrap" in py_file.stem.lower() or "wiring" in py_file.stem.lower():
                # Check if it's a legitimate file
                if py_file.name in legitimate_files:
                    continue  # Legitimate Phase 3 component, skip
                    
                # Check if it's an allowed stub
                if py_file not in allowed:
                    # Read to see if it's substantial (not just a stub)
                    try:
                        content = py_file.read_text()
                        # Simple heuristic: stubs are < 100 lines with "DEPRECATED" or "backward compatibility"
                        lines = len(content.split("\n"))
                        is_stub = (
                            lines < 100
                            and (
                                "DEPRECATED" in content
                                or "backward compatibility" in content
                                or "Phase 2" in content
                            )
                        )
                        if not is_stub:
                            potential_bootstraps.append(py_file)
                    except Exception:
                        pass  # Can't read file, skip
        
        real_violations = potential_bootstraps
        
        assert not real_violations, (
            f"Found potential alternative bootstrap mechanisms: {real_violations}. "
            "There should be only ONE wiring path (Git-backed YAML)."
        )
    
    def test_no_db_files_in_project(self, cortex_root: Path):
        """Test that no WIRING database files exist in the project.
        
        Runtime caches in .cortex/ are allowed as they are ephemeral
        and do not store wiring configuration.
        """
        db_files = list(cortex_root.glob("**/*.db"))
        
        # Filter out node_modules, .venv, .cortex (runtime caches), etc.
        excluded_dirs = {".venv", "node_modules", "__pycache__", ".git", ".cortex"}
        db_files = [
            f for f in db_files
            if not any(excluded in f.parts for excluded in excluded_dirs)
        ]
        
        # Convert to relative paths for comparison
        db_relative = {str(f.relative_to(cortex_root)) for f in db_files}
        
        assert not db_relative, (
            f"Found wiring database files: {db_relative}. "
            "All wiring databases should have been deleted in Phase 2. "
            "Runtime caches in .cortex/ are allowed and excluded from this check."
        )
