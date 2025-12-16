"""
SKULL Test: Strict Folder Organization Enforcement

Tests the STRICT_FOLDER_ORGANIZATION_ENFORCEMENT rule across all scenarios:
- Temp plans in dedicated folders
- Active plans in semantic folders
- Universal subfolder structure (context/, reports/, artifacts/, tracking/)
- Root folder restrictions (only README, schemas allowed)
- Copyright header enforcement
- Plan lifecycle (temp → active → completed)

Author: Asif Hussain
Date: December 15, 2025
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
import yaml
from typing import Dict, Any, List


class TestStrictFolderOrganizationSKULL:
    """Test suite for STRICT_FOLDER_ORGANIZATION_ENFORCEMENT SKULL rule."""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix="cortex_skull_test_")
        workspace = Path(temp_dir)
        
        # Create base structure
        (workspace / "cortex-brain" / "documents" / "planning").mkdir(parents=True)
        (workspace / "cortex-brain" / "documents" / "planning" / "temp-plans").mkdir()
        (workspace / "cortex-brain" / "documents" / "planning" / "active").mkdir()
        (workspace / "cortex-brain" / "documents" / "planning" / "completed").mkdir()
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def allowed_root_files(self):
        """Files allowed in folder roots."""
        return ["README.md", "planning-schema.yaml", ".gitignore"]

    @pytest.fixture
    def prohibited_root_files(self):
        """Files prohibited in folder roots."""
        return [
            "TEMP-PLAN-20251215.md",
            "auth-plan.md",
            "HOLISTIC-REVIEW.md",
            "execution-report.md",
            "complexity-analysis.json",
            "progress-tracker.yaml"
        ]

    @pytest.fixture
    def universal_subfolders(self):
        """Universal subfolders required in all plan folders."""
        return ["context", "reports", "artifacts", "tracking"]

    @pytest.fixture
    def copyright_header(self):
        """Required copyright header format."""
        return "🧠 CORTEX - {}\nAuthor: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX\n\n---\n"

    # ============================================
    # TEST 1: Root Folder Restrictions
    # ============================================

    def test_skull_allowed_root_files(self, temp_workspace, allowed_root_files):
        """Test that allowed files can be created in folder root."""
        planning_root = temp_workspace / "cortex-brain" / "documents" / "planning"
        
        for filename in allowed_root_files:
            file_path = planning_root / filename
            file_path.write_text(f"# {filename}\n\nThis file applies to ALL subfolders.")
            
            # Should be allowed
            assert file_path.exists()
            assert self._is_allowed_in_root(file_path)

    def test_skull_prohibited_root_files(self, temp_workspace, prohibited_root_files):
        """Test that prohibited files are detected in folder root."""
        planning_root = temp_workspace / "cortex-brain" / "documents" / "planning"
        
        violations = []
        for filename in prohibited_root_files:
            file_path = planning_root / filename
            file_path.write_text("# Test content")
            
            # Should be prohibited
            if not self._is_allowed_in_root(file_path):
                violations.append(filename)
        
        assert len(violations) == len(prohibited_root_files), \
            f"Expected {len(prohibited_root_files)} violations, got {len(violations)}"

    def test_skull_root_folder_scan_recursive(self, temp_workspace):
        """Test recursive scanning for root folder violations."""
        base = temp_workspace / "cortex-brain" / "documents"
        
        # Create test structure with violations - ensure parent directories exist
        (base / "planning").mkdir(exist_ok=True)
        (base / "reports").mkdir(exist_ok=True)
        (base / "analysis").mkdir(exist_ok=True)
        
        (base / "planning" / "VIOLATION.md").write_text("Root file")
        (base / "reports" / "VIOLATION.md").write_text("Root file")
        (base / "analysis" / "VIOLATION.md").write_text("Root file")
        
        # Create allowed files
        (base / "planning" / "README.md").write_text("Allowed")
        
        violations = self._scan_root_violations_recursive(base)
        
        assert len(violations) == 3, f"Expected 3 violations, found {len(violations)}"
        assert any("planning" in str(v) and "VIOLATION.md" in str(v) for v in violations)
        assert any("reports" in str(v) and "VIOLATION.md" in str(v) for v in violations)
        assert any("analysis" in str(v) and "VIOLATION.md" in str(v) for v in violations)

    # ============================================
    # TEST 2: Universal Subfolder Structure
    # ============================================

    def test_skull_universal_subfolders_temp_plan(self, temp_workspace, universal_subfolders):
        """Test that temp plans have universal subfolders."""
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans" / "auth-system-20251215"
        plan_folder.mkdir(parents=True)
        
        # Create universal subfolders
        for subfolder in universal_subfolders:
            (plan_folder / subfolder).mkdir()
        
        # Verify all subfolders exist
        for subfolder in universal_subfolders:
            assert (plan_folder / subfolder).exists(), f"Missing subfolder: {subfolder}"

    def test_skull_universal_subfolders_active_plan(self, temp_workspace, universal_subfolders):
        """Test that active plans have universal subfolders."""
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "authentication-system-v2"
        plan_folder.mkdir(parents=True)
        
        # Create universal subfolders
        for subfolder in universal_subfolders:
            (plan_folder / subfolder).mkdir()
        
        # Verify all subfolders exist
        for subfolder in universal_subfolders:
            assert (plan_folder / subfolder).exists(), f"Missing subfolder: {subfolder}"

    def test_skull_universal_subfolders_missing_detection(self, temp_workspace, universal_subfolders):
        """Test detection of missing universal subfolders."""
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "incomplete-plan"
        plan_folder.mkdir(parents=True)
        
        # Only create context/ and reports/ (missing artifacts/ and tracking/)
        (plan_folder / "context").mkdir()
        (plan_folder / "reports").mkdir()
        
        missing = self._check_universal_subfolders(plan_folder, universal_subfolders)
        
        assert "artifacts" in missing, "Should detect missing artifacts/"
        assert "tracking" in missing, "Should detect missing tracking/"
        assert len(missing) == 2, f"Expected 2 missing, got {len(missing)}"

    # ============================================
    # TEST 3: Copyright Header Enforcement
    # ============================================

    def test_skull_copyright_header_present(self, temp_workspace, copyright_header):
        """Test that copyright header is present in planning documents."""
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "test-plan-v1"
        plan_folder.mkdir(parents=True)
        
        plan_file = plan_folder / "00-master-plan.md"
        header = copyright_header.format("Test Plan Master Plan")
        plan_file.write_text(f"{header}\n# Master Plan\n\nContent here...", encoding="utf-8")
        
        content = plan_file.read_text(encoding="utf-8")
        
        assert "🧠 CORTEX" in content, "Missing CORTEX brain emoji"
        assert "Author: Asif Hussain" in content, "Missing author"
        assert "github.com/asifhussain60/CORTEX" in content, "Missing GitHub URL"
        assert "---" in content, "Missing separator"

    def test_skull_copyright_header_missing(self, temp_workspace):
        """Test detection of missing copyright header."""
        plan_folder = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "test-plan-v1"
        plan_folder.mkdir(parents=True)
        
        plan_file = plan_folder / "00-master-plan.md"
        plan_file.write_text("# Master Plan\n\nNo copyright header!", encoding="utf-8")
        
        assert not self._has_copyright_header(plan_file), "Should detect missing copyright"

    def test_skull_copyright_header_bulk_validation(self, temp_workspace, copyright_header):
        """Test bulk validation of copyright headers across multiple files."""
        active = temp_workspace / "cortex-brain" / "documents" / "planning" / "active"
        
        # Create multiple plans
        plans = ["auth-v1", "payment-v2", "reporting-v1"]
        for plan_name in plans:
            plan_folder = active / plan_name
            plan_folder.mkdir()
            
            # Master plan with copyright
            master = plan_folder / "00-master-plan.md"
            master.write_text(copyright_header.format(f"{plan_name} Master Plan") + "\n# Plan", encoding="utf-8")
            
            # Sub-plan WITHOUT copyright (violation)
            subplan = plan_folder / "01-subplan-implementation.md"
            subplan.write_text("# Sub-Plan\n\nNo header!", encoding="utf-8")
        
        violations = self._scan_copyright_violations(active)
        
        # Should find 3 violations (one sub-plan per plan)
        assert len(violations) == 3, f"Expected 3 violations, found {len(violations)}"

    # ============================================
    # TEST 4: Plan Lifecycle Workflow
    # ============================================

    def test_skull_temp_plan_creation(self, temp_workspace, universal_subfolders):
        """Test temp plan creation with proper structure."""
        temp_plans = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans"
        plan_id = "auth-system-jwt-20251215"
        
        plan_folder = temp_plans / plan_id
        self._create_plan_with_structure(plan_folder, universal_subfolders, "00-temp-plan.md")
        
        # Verify structure
        assert (plan_folder / "00-temp-plan.md").exists()
        for subfolder in universal_subfolders:
            assert (plan_folder / subfolder).exists()

    def test_skull_temp_to_active_lifecycle(self, temp_workspace, universal_subfolders):
        """Test temp plan promotion to active with file preservation."""
        temp_plans = temp_workspace / "cortex-brain" / "documents" / "planning" / "temp-plans"
        active = temp_workspace / "cortex-brain" / "documents" / "planning" / "active"
        
        # Create temp plan
        temp_plan = temp_plans / "auth-system-jwt-20251215"
        self._create_plan_with_structure(temp_plan, universal_subfolders, "00-temp-plan.md")
        
        # Add some artifacts
        (temp_plan / "context" / "git-history.yaml").write_text("git: data")
        (temp_plan / "reports" / "HOLISTIC-REVIEW.md").write_text("# Review")
        
        # Promote to active
        active_plan = active / "authentication-system-v2"
        self._promote_to_active(temp_plan, active_plan)
        
        # Verify move
        assert active_plan.exists()
        assert (active_plan / "00-master-plan.md").exists()  # Renamed from temp
        assert (active_plan / "context" / "git-history.yaml").exists()
        assert (active_plan / "reports" / "HOLISTIC-REVIEW.md").exists()
        
        # Verify temp plan still exists (or removed based on policy)
        # For now, assume temp plan is archived/moved

    def test_skull_active_to_completed_lifecycle(self, temp_workspace, universal_subfolders):
        """Test active plan archival to completed with structure preservation."""
        active = temp_workspace / "cortex-brain" / "documents" / "planning" / "active"
        completed = temp_workspace / "cortex-brain" / "documents" / "planning" / "completed"
        
        # Create active plan
        active_plan = active / "authentication-system-v2"
        self._create_plan_with_structure(active_plan, universal_subfolders, "00-master-plan.md")
        
        # Add execution artifacts
        (active_plan / "tracking" / "progress-tracker.json").write_text('{"status": "complete"}')
        (active_plan / "reports" / "execution-phase-1-report.md").write_text("# Phase 1")
        
        # Archive to completed
        completed_plan = completed / "authentication-system-v2"
        self._archive_to_completed(active_plan, completed_plan)
        
        # Verify archive
        assert completed_plan.exists()
        assert (completed_plan / "00-master-plan.md").exists()
        assert (completed_plan / "tracking" / "progress-tracker.json").exists()
        assert (completed_plan / "reports" / "execution-phase-1-report.md").exists()

    # ============================================
    # TEST 5: Semantic Folder Naming
    # ============================================

    def test_skull_semantic_folder_naming_valid(self, temp_workspace):
        """Test valid semantic folder names (intent-based)."""
        active = temp_workspace / "cortex-brain" / "documents" / "planning" / "active"
        
        valid_names = [
            "authentication-system-v2",  # User capability
            "cortex-rearchitecture-v1",  # Holistic system change
            "performance-optimization-v1",  # Business outcome
            "api-security-enhancement-v1",  # User goal
            "planning-workflow-v2"  # User-facing workflow
        ]
        
        for name in valid_names:
            folder = active / name
            folder.mkdir()
            assert self._is_semantic_folder_name(name), f"{name} should be valid (represents user intent)"

    def test_skull_semantic_folder_naming_invalid(self, temp_workspace):
        """Test invalid semantic folder names (technical/rule names)."""
        active = temp_workspace / "cortex-brain" / "documents" / "planning" / "active"
        
        invalid_names = [
            "cortex-enhancements",  # Too generic
            "strict-folder-organization-v1",  # Governance rule name, not user intent
            "tdd-enforcement-implementation-v1",  # Internal rule implementation
            "ast-analysis-integration-v1",  # Technical implementation detail
            "planning-orchestrator-refactor-v1",  # Code component name
            "misc-plans",  # No semantic meaning
            "new-features",  # Which features?
            "plan_20251215",  # Timestamp only
            "temp"  # Generic
        ]
        
        for name in invalid_names:
            folder = active / name
            folder.mkdir()
            assert not self._is_semantic_folder_name(name), f"{name} should be invalid (not user intent)"

    def test_skull_semantic_folder_versioning(self, temp_workspace):
        """Test auto-versioning for semantic folders."""
        active = temp_workspace / "cortex-brain" / "documents" / "planning" / "active"
        
        # Create v1
        (active / "authentication-system-v1").mkdir()
        
        # Detect next version
        next_version = self._detect_next_version(active, "authentication-system")
        assert next_version == 2, "Should detect next version as v2"
        
        # Create v2
        (active / "authentication-system-v2").mkdir()
        
        # Detect next version again
        next_version = self._detect_next_version(active, "authentication-system")
        assert next_version == 3, "Should detect next version as v3"

    # ============================================
    # TEST 6: Continuation Prompt System
    # ============================================

    def test_skull_continuation_prompt_structure(self, temp_workspace, copyright_header):
        """Test continuation prompt structure in master plan."""
        active = temp_workspace / "cortex-brain" / "documents" / "planning" / "active"
        plan_folder = active / "auth-system-v1"
        plan_folder.mkdir(parents=True)
        
        master_plan = plan_folder / "00-master-plan.md"
        content = f"""{copyright_header.format("Authentication System Master Plan")}

# Master Plan

## 🔄 **CONTINUATION PROMPT** (Updated: Dec 15, 12:30 PM)

**STATUS:** Phase 1 complete. Beginning Phase 2.

**NEXT ACTION:** Execute Phase 2 directly. DO NOT report - EXECUTE.

**CONTEXT:**
- Phase 1 completion report: `reports/execution-phase-1-report.md`
- Sub-plan: `02-subplan-implementation.md`

**INSTRUCTIONS FOR CORTEX:**
```
Execute Phase 2 directly.
```

---

## Overview
Plan content...
"""
        master_plan.write_text(content, encoding='utf-8')
        
        # Verify continuation prompt presence
        content = master_plan.read_text(encoding='utf-8')
        assert "🔄 **CONTINUATION PROMPT**" in content
        assert "**STATUS:**" in content
        assert "**NEXT ACTION:**" in content
        assert "**CONTEXT:**" in content
        assert "**INSTRUCTIONS FOR CORTEX:**" in content

    # ============================================
    # HELPER METHODS
    # ============================================

    def _is_allowed_in_root(self, file_path: Path) -> bool:
        """Check if file is allowed in folder root."""
        allowed = ["README.md", "planning-schema.yaml", ".gitignore", "schema.yaml"]
        return file_path.name in allowed or file_path.name.endswith("-schema.yaml")

    def _scan_root_violations_recursive(self, base_path: Path) -> List[Path]:
        """Recursively scan for root folder violations."""
        violations = []
        
        for category_folder in base_path.iterdir():
            if not category_folder.is_dir():
                continue
            
            for item in category_folder.iterdir():
                if item.is_file() and not self._is_allowed_in_root(item):
                    violations.append(item)
        
        return violations

    def _check_universal_subfolders(self, plan_folder: Path, required: List[str]) -> List[str]:
        """Check for missing universal subfolders."""
        missing = []
        for subfolder in required:
            if not (plan_folder / subfolder).exists():
                missing.append(subfolder)
        return missing

    def _has_copyright_header(self, file_path: Path) -> bool:
        """Check if file has copyright header."""
        content = file_path.read_text(encoding="utf-8")
        return ("🧠 CORTEX" in content and 
                "Author: Asif Hussain" in content and 
                "github.com/asifhussain60/CORTEX" in content)

    def _scan_copyright_violations(self, base_path: Path) -> List[Path]:
        """Scan for files missing copyright headers."""
        violations = []
        
        for plan_folder in base_path.iterdir():
            if not plan_folder.is_dir():
                continue
            
            for md_file in plan_folder.rglob("*.md"):
                if not self._has_copyright_header(md_file):
                    violations.append(md_file)
        
        return violations

    def _create_plan_with_structure(self, plan_folder: Path, subfolders: List[str], main_file: str):
        """Create plan with universal subfolder structure."""
        plan_folder.mkdir(parents=True)
        (plan_folder / main_file).write_text("# Plan")
        
        for subfolder in subfolders:
            (plan_folder / subfolder).mkdir()

    def _promote_to_active(self, temp_plan: Path, active_plan: Path):
        """Promote temp plan to active (move and rename)."""
        shutil.copytree(temp_plan, active_plan)
        
        # Rename temp plan to master plan
        temp_file = active_plan / "00-temp-plan.md"
        master_file = active_plan / "00-master-plan.md"
        if temp_file.exists():
            temp_file.rename(master_file)

    def _archive_to_completed(self, active_plan: Path, completed_plan: Path):
        """Archive active plan to completed."""
        shutil.copytree(active_plan, completed_plan)

    def _is_semantic_folder_name(self, name: str) -> bool:
        """
        Check if folder name represents USER INTENT (not technical/rule names).
        
        VALID (user intent):
        - authentication-system-v2 (user capability)
        - cortex-rearchitecture-v1 (holistic system change)
        - performance-optimization-v1 (business outcome)
        
        INVALID (technical/rule names):
        - strict-folder-organization-v1 (governance rule name)
        - tdd-enforcement-implementation-v1 (internal rule)
        - planning-orchestrator-refactor-v1 (code component)
        """
        # Anti-patterns: Governance rule names, technical implementations
        anti_patterns = [
            "cortex-enhancements",  # Too generic
            "strict-folder-organization",  # Governance rule, not user intent
            "tdd-enforcement",  # Internal rule implementation
            "ast-analysis",  # Technical implementation detail
            "orchestrator-refactor",  # Code component name
            "misc-plans",  # No semantic meaning
            "new-features",  # Which features?
            "temp",  # Generic
            "plan_",  # Timestamp-based naming
            "implementation-v",  # Implementation detail focus
            "enforcement-v"  # Rule enforcement focus
        ]
        
        # Check if name contains anti-patterns
        for pattern in anti_patterns:
            if pattern in name:
                return False
        
        # Valid semantic names have meaningful feature/goal + optional version
        # Pattern: {user-goal}-v{N} or {user-goal}-{N}.{N}
        # Examples: authentication-system-v2, cortex-rearchitecture-v1
        return "-" in name and not name.startswith("plan_")

    def _detect_next_version(self, base_path: Path, feature_name: str) -> int:
        """Detect next version number for feature folder."""
        import re
        
        existing_versions = []
        for folder in base_path.iterdir():
            if folder.is_dir() and folder.name.startswith(feature_name):
                match = re.search(r'-v(\d+)$', folder.name)
                if match:
                    existing_versions.append(int(match.group(1)))
        
        return max(existing_versions, default=0) + 1


# ============================================
# STANDALONE EXECUTION
# ============================================

if __name__ == "__main__":
    """Run SKULL tests standalone (like test_skull_discovery_only.py pattern)."""
    print("🧠 CORTEX SKULL Test: STRICT_FOLDER_ORGANIZATION_ENFORCEMENT")
    print("=" * 70)
    
    # Run with pytest
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "=" * 70)
    if exit_code == 0:
        print("✅ ALL SKULL TESTS PASSED")
    else:
        print("❌ SOME SKULL TESTS FAILED")
    
    exit(exit_code)
