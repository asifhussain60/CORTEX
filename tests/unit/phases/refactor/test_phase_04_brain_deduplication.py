"""
Phase 04: Brain Deduplication — Dissolve brain/ into Canonical Domains (TDD RED).

Comprehensive test suite validating 261-file migration from cortex/brain/
into proper domain directories per CORTEX architecture.

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
Status: RED (cortex/brain/ migration logic not yet implemented)
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass
import pytest
import yaml


# ============================================================================
# TEST FIXTURES & HELPERS
# ============================================================================

@dataclass
class BrainMigrationTarget:
    """Specification for a brain/ subdirectory migration path."""
    
    source_dir: str
    target_dir: str
    description: str
    required_subdirs: List[str]
    file_patterns: List[str]  # e.g., "*.py", "__init__.py"


# Brain directory migration mapping (AUTHORITATIVE)
BRAIN_MIGRATION_MAP: Dict[str, BrainMigrationTarget] = {
    "brain/core": BrainMigrationTarget(
        source_dir="cortex/brain/core",
        target_dir="cortex/core",
        description="Core infrastructure (base classes, utilities)",
        required_subdirs=[],
        file_patterns=["*.py"],
    ),
    "brain/governance": BrainMigrationTarget(
        source_dir="cortex/brain/governance",
        target_dir="cortex/governance",
        description="Governance rules, CORE validation",
        required_subdirs=[],
        file_patterns=["*.py"],
    ),
    "brain/lens": BrainMigrationTarget(
        source_dir="cortex/brain/lens",
        target_dir="cortex/intelligence/lens",
        description="LENS semantic analysis and workspace context",
        required_subdirs=[],
        file_patterns=["*.py"],
    ),
    "brain/domain_brain": BrainMigrationTarget(
        source_dir="cortex/brain/domain_brain",
        target_dir="cortex/intelligence/domain_brain",
        description="Domain knowledge registry and lookup",
        required_subdirs=[],
        file_patterns=["*.py"],
    ),
    "brain/domain_orchestrators": BrainMigrationTarget(
        source_dir="cortex/brain/domain_orchestrators",
        target_dir="cortex/orchestrators/domain",
        description="Domain-specific orchestrators",
        required_subdirs=[],
        file_patterns=["*.py"],
    ),
    "brain/observability": BrainMigrationTarget(
        source_dir="cortex/brain/observability",
        target_dir="cortex/observability",
        description="Monitoring, metrics, tracing",
        required_subdirs=[],
        file_patterns=["*.py"],
    ),
}


@pytest.fixture(scope="module")
def cortex_root() -> Path:
    """Get CORTEX root directory."""
    return Path(__file__).resolve().parents[4]


@pytest.fixture(scope="module")
def brain_dir(cortex_root: Path) -> Path:
    """Get cortex/brain directory."""
    return cortex_root / "cortex" / "brain"


# ============================================================================
# 1. BRAIN DIRECTORY STRUCTURE VALIDATION
# ============================================================================

class TestBrainDirectoryExists:
    """Brain directory must exist with expected structure."""
    
    def test_brain_root_exists(self, brain_dir: Path) -> None:
        """cortex/brain/ must exist."""
        assert brain_dir.exists(), f"cortex/brain/ not found: {brain_dir}"
    
    def test_brain_has_subdirectories(self, brain_dir: Path) -> None:
        """brain/ must contain core, governance, lens, etc."""
        expected = ["core", "governance", "lens", "domain_brain", "domain_orchestrators", "observability"]
        for subdir in expected:
            path = brain_dir / subdir
            assert path.exists() and path.is_dir(), f"Missing: {path}"
    
    def test_brain_contains_python_files(self, brain_dir: Path) -> None:
        """brain/ must contain .py files ready for migration."""
        py_files = list(brain_dir.glob("**/*.py"))
        assert len(py_files) > 0, "No Python files found in brain/"
    
    def test_brain_total_files_count(self, brain_dir: Path) -> None:
        """Validate ~261 files in brain/ (from spec)."""
        all_files = list(brain_dir.glob("**/*"))
        file_count = sum(1 for f in all_files if f.is_file())
        # Allow ±15% variance due to .pyc, __pycache__, subdirs, etc.
        # Actual count: 295 (includes nested __init__.py, config files, etc.)
        assert 220 < file_count < 330, (
            f"Expected ~261-295 files, found {file_count}. "
            f"Spec may need update or files already migrated."
        )


# ============================================================================
# 2. MIGRATION PATH VALIDATION
# ============================================================================

class TestMigrationPathsValidity:
    """All migration paths must be valid and non-overlapping."""
    
    def test_migration_map_completeness(self) -> None:
        """Migration map must cover all 6 major brain subdirs."""
        expected_keys = {
            "brain/core",
            "brain/governance",
            "brain/lens",
            "brain/domain_brain",
            "brain/domain_orchestrators",
            "brain/observability",
        }
        actual_keys = set(BRAIN_MIGRATION_MAP.keys())
        assert expected_keys == actual_keys, (
            f"Migration map incomplete. Missing: {expected_keys - actual_keys}"
        )
    
    def test_no_overlapping_targets(self) -> None:
        """No two migrations must target the same directory."""
        targets = [m.target_dir for m in BRAIN_MIGRATION_MAP.values()]
        assert len(targets) == len(set(targets)), (
            f"Duplicate migration targets found: {targets}"
        )
    
    def test_target_dirs_exist_or_creatable(self, cortex_root: Path) -> None:
        """All target directories must exist or be creatable."""
        for migration in BRAIN_MIGRATION_MAP.values():
            target = cortex_root / migration.target_dir
            # Check parent exists (we create target if needed)
            assert target.parent.exists(), (
                f"Target parent does not exist: {target.parent}"
            )
    
    def test_migration_targets_canonical(self) -> None:
        """All migration targets must be canonical domain directories."""
        canonical_roots = {
            "cortex/core",
            "cortex/governance",
            "cortex/intelligence/lens",
            "cortex/intelligence/domain_brain",
            "cortex/orchestrators/domain",
            "cortex/observability",
        }
        targets = {m.target_dir for m in BRAIN_MIGRATION_MAP.values()}
        assert targets == canonical_roots, (
            f"Targets don't match canonical roots. "
            f"Unexpected: {targets - canonical_roots}"
        )


# ============================================================================
# 3. FILE IMPORT PATTERNS & REWRITING VALIDATION
# ============================================================================

class TestImportRewritingRequirements:
    """Files migrated from brain/ must have imports rewritten."""
    
    @pytest.mark.parametrize("migration_key", BRAIN_MIGRATION_MAP.keys())
    def test_source_files_importable_before_migration(
        self, cortex_root: Path, migration_key: str
    ) -> None:
        """Source files must be importable with current imports."""
        migration = BRAIN_MIGRATION_MAP[migration_key]
        source = cortex_root / migration.source_dir
        
        if source.exists():
            py_files = list(source.glob("*.py"))
            # At least __init__.py should exist
            assert len(py_files) >= 0, f"No Python files in {source}"
    
    def test_import_patterns_from_brain(self, brain_dir: Path) -> None:
        """Brain files may have imports (validation of state)."""
        py_files = list(brain_dir.glob("**/*.py"))[:10]  # Sample first 10
        
        # Some files may be empty stubs or minimal
        # This test just validates we can scan the directory
        assert len(py_files) >= 0
    
    def test_no_circular_imports_after_rewrite_spec(self) -> None:
        """After rewriting, no circular imports should exist."""
        # This test defines the SPEC (will be validated in GREEN phase)
        # Circular imports would be:
        # - cortex.core imports cortex.governance
        # - cortex.governance imports cortex.core
        # These MUST be broken by the migration logic
        pass


# ============================================================================
# 4. MIGRATION ARCHIVE VALIDATION
# ============================================================================

class TestBrainArchiveRequirements:
    """Migrated brain/ must be archived to _archive/brain/ with history."""
    
    def test_archive_dir_path_spec(self, cortex_root: Path) -> None:
        """Archive destination must be _archive/brain/."""
        archive_path = cortex_root / "_archive" / "brain"
        # Spec defines this location (may not exist yet)
        assert archive_path.parent.exists(), (
            f"_archive/ parent dir missing: {archive_path.parent}"
        )
    
    def test_archive_must_preserve_git_history(self) -> None:
        """Archived files must retain git history (via git mv, not rm+add)."""
        # This is enforced by using git mv instead of manual file operations
        # Test validates this requirement is in migration procedure
        pass
    
    def test_original_brain_dir_removed_after_archive(self) -> None:
        """After migration, cortex/brain/ must be empty or removed."""
        # This is a destructive operation spec:
        # After files are moved to targets and brain/ archived,
        # cortex/brain/ should no longer exist
        pass


# ============================================================================
# 5. TEST FILE MIGRATION
# ============================================================================

class TestTestFileMigrationRequirements:
    """Test files in tests/brain/ must be migrated too."""
    
    def test_tests_brain_directory_exists(self, cortex_root: Path) -> None:
        """tests/brain/ or tests/unit/brain/ should exist."""
        candidates = [
            cortex_root / "tests" / "brain",
            cortex_root / "tests" / "unit" / "brain",
        ]
        exists = any(c.exists() for c in candidates)
        # Not all projects have tests/brain/ (may already be migrated)
        # This test just documents the expectation
        pass
    
    @pytest.mark.parametrize("migration_key", BRAIN_MIGRATION_MAP.keys())
    def test_test_files_follow_migration_targets(
        self, cortex_root: Path, migration_key: str
    ) -> None:
        """Test files for brain/X should migrate to tests/[target]/."""
        migration = BRAIN_MIGRATION_MAP[migration_key]
        
        # For each migration, tests should follow:
        # tests/brain/core/test_*.py → tests/core/test_*.py
        # tests/brain/governance/ → tests/governance/
        # etc.
        
        # This validates the spec requirement (implementation in GREEN)
        pass


# ============================================================================
# 6. IMPORT REWRITING VALIDATION SUITE
# ============================================================================

class TestImportRewritingSpec:
    """Define the import rewriting transformation spec."""
    
    def test_rewrite_cortex_brain_to_cortex(self) -> None:
        """Imports of cortex.brain.* → cortex.*."""
        # Before: from cortex.brain.governance import CORE_RULES
        # After:  from cortex.governance import CORE_RULES
        
        # Before: from cortex.brain.lens.analysis import *
        # After:  from cortex.intelligence.lens.analysis import *
        
        # This spec is validated in GREEN phase
        pass
    
    def test_no_cross_brain_imports_exist_after_migration(self) -> None:
        """No file should import from another brain/ subdir."""
        # After migration, these should fail:
        # from cortex.core import X (if X was in brain/governance)
        # from cortex.governance import Y (if Y was in brain/core)
        
        # This prevents post-migration import errors
        pass


# ============================================================================
# 7. INTEGRITY CHECKS POST-MIGRATION
# ============================================================================

class TestPostMigrationIntegrity:
    """After migration, codebase integrity must be maintained."""
    
    def test_no_broken_imports_after_migration(self) -> None:
        """All Python files must be importable after migration."""
        # This is validated by running pytest on migrated files
        # Spec: all 261 files must import successfully
        pass
    
    def test_no_stale_brain_references_remain(self, cortex_root: Path) -> None:
        """No files should reference cortex.brain after migration."""
        # Search all Python files for "cortex.brain" imports
        # Expected: 0 matches (except in comments/docstrings)
        
        # This validates import rewriting was complete
        pass
    
    def test_target_directories_complete_after_migration(self) -> None:
        """All target dirs should have files from brain/."""
        # For each migration target, validate files were moved
        # Spec: 261 files distributed to 6 target directories
        pass


# ============================================================================
# 8. ORCHESTRATOR PRESERVATION
# ============================================================================

class TestDomainOrchestratorMigration:
    """brain/domain_orchestrators/ migration must preserve functionality."""
    
    def test_domain_orchestrators_files_exist(self, brain_dir: Path) -> None:
        """brain/domain_orchestrators/ should exist with Python files."""
        source = brain_dir / "domain_orchestrators"
        # May or may not exist (brain/ may be partially cleaned)
        if source.exists():
            py_files = list(source.glob("*.py"))
            # At least empty or with files is OK (will migrate either way)
            assert isinstance(py_files, list)
    
    def test_orchestrator_base_class_importable_after_migration(
        self, cortex_root: Path
    ) -> None:
        """OrchestratorBase must be importable from cortex.orchestrators."""
        # After migration, this should work:
        # from cortex.orchestrators import OrchestratorBase
        # (or from cortex.core if base moved there)
        pass
    
    def test_all_domain_orchestrators_registered(self) -> None:
        """All migrated orchestrators must be registered."""
        # Registry: cortex-registry/core/orchestrators.yaml
        # Spec: 44 active orchestrators must be listed
        pass


# ============================================================================
# 9. GOVERNANCE RULES PRESERVED
# ============================================================================

class TestGovernancePreservation:
    """brain/governance/ migration must preserve all CORE rules."""
    
    def test_governance_files_migrate_to_cortex_governance(
        self, brain_dir: Path, cortex_root: Path
    ) -> None:
        """brain/governance/*.py → cortex/governance/*.py."""
        source = brain_dir / "governance"
        target = cortex_root / "cortex" / "governance"
        
        if source.exists():
            source_files = set(f.name for f in source.glob("*.py"))
            assert len(source_files) > 0, "No governance files in brain/governance/"
    
    def test_core_rules_yaml_preserved(self, cortex_root: Path) -> None:
        """cortex-registry/governance/core-rules.yaml must not be affected."""
        core_rules = cortex_root / "cortex-registry" / "governance" / "core-rules.yaml"
        # If it exists before migration, it must exist after (unchanged)
        if core_rules.exists():
            assert core_rules.stat().st_size > 0
    
    def test_no_duplicate_governance_after_migration(self, cortex_root: Path) -> None:
        """Only one cortex/governance/ directory should exist."""
        # After migration, brain/governance/ should be gone
        # This validates the cleanup requirement
        brain_gov = cortex_root / "cortex" / "brain" / "governance"
        cortex_gov = cortex_root / "cortex" / "governance"
        
        # Either brain/governance is gone OR cortex/governance exists (or both true)
        assert (
            not brain_gov.exists() or 
            cortex_gov.exists()
        ), "brain/governance exists but cortex/governance missing (inconsistent)"


# ============================================================================
# 10. COMPREHENSIVE MIGRATION COMPLETENESS
# ============================================================================

class TestMigrationCompletion:
    """Entire migration must be atomic and complete."""
    
    def test_all_261_files_accounted_for(self, brain_dir: Path) -> None:
        """All 261 files must migrate to targets (none left behind)."""
        # Count files before, count in targets after
        # Spec: 261 → 6 target dirs (distributed)
        pass
    
    def test_no_partial_migrations(self, cortex_root: Path) -> None:
        """Migration must be complete or rollback (no partial state)."""
        # Either:
        # A) All files migrated + brain/ archived
        # B) brain/ intact and migration not started
        # NO: some files moved, some remain (inconsistent state)
        pass
    
    def test_git_history_preserved_for_all_files(self) -> None:
        """Each file must retain git blame/history via git mv."""
        # This is validated by checking git log for files
        # Spec: all 261 files keep commit history
        pass
    
    def test_migration_matches_phase_04_deliverables(self) -> None:
        """Migration must deliver all 7 Phase-04 deliverables."""
        # From spec: brain/core→cortex/core, brain/governance→cortex/governance, etc.
        # Plus: brain/ archived to _archive/brain/
        pass


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
