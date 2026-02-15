"""
Golden Path Truth Tests for Change Coherence Engine.

AC_START: AC-ENH-101-013
Description: Truth tests with ZERO mocks - validates real-world behavior
Authority: ENH-101 Stage S6 - WAVE-10 Golden Path Testing
Compliance: 0 mocks for core logic, audit trail verification

Purpose:
    End-to-end tests using real content, real validation, real reports.
    No mocks. No stubs. Just truth.
"""

import pytest
from pathlib import Path

from cortex.orchestrators.coherence import (
    ChangeCoherenceEngine,
    CoherenceStatus,
    CoherenceValidator,
    DuplicateScanner,
    PreEditContext,
    StructureAnalyzer,
    ValidationConfig,
)
from cortex.mcp.tools.coherence_tools import cortex_validate_coherence


# =============================================================================
# GOLDEN PATH TRUTH TEST 1: Duplicate Prevention
# =============================================================================

@pytest.mark.asyncio
async def test_duplicate_prevention_truth() -> None:
    """
    TRUTH TEST: Duplicate detection prevents adding existing content.
    
    Scenario:
        1. Start with content containing "Installation" section
        2. Attempt to add another "Installation" section
        3. CCE detects duplicate and blocks it
        
    Validation:
        - ZERO mocks used
        - Real StructureAnalyzer detects sections
        - Real DuplicateScanner finds duplicates
        - Real CoherenceValidator reports failure
        - Audit trail: AC_START → AC_COMPLETE markers present
    """
    # AC_START: AC-ENH-101-TRUTH-001
    
    # Given: Original content with existing sections
    original_content = """# Project

## Installation

Run `pip install package`.

## Usage

Import and use:
```python
import package
```
"""
    
    # When: User attempts to add duplicate "Installation" section
    proposed_content = """# Project

## Installation

Run `pip install package`.

## Usage

Import and use:
```python
import package
```

## Installation

Use conda instead: `conda install package`.
"""
    
    # Then: CCE detects and reports duplicate
    result = await cortex_validate_coherence(
        file_path="README.md",
        content=proposed_content,
        pre_edit_content=original_content,
        orchestrator_context={
            "source": "MasterOrchestrator",
            "intent": "TEST",
            "request_id": "test_duplicate_prevention_truth",
        },
    )
    
    # TRUTH ASSERTIONS (no mocks)
    assert result["status"] in ("failed", "warning"), "Duplicate should trigger failure/warning"
    assert result["duplicates_found"] > 0, "Should detect at least 1 duplicate"
    
    # Verify specific duplicate reported
    dup_issues = [i for i in result["issues"] if i["type"] == "duplicate_section"]
    assert len(dup_issues) > 0, "Should report duplicate_section issue"
    assert "Installation" in str(dup_issues), "Should mention 'Installation' section"
    
    # Verify recommendations provided
    assert len(result["recommendations"]) > 0, "Should provide fix recommendations"
    assert any("consolidate" in r.lower() or "remove" in r.lower() or "merge" in r.lower() 
               for r in result["recommendations"]), "Should suggest consolidation/removal"
    
    # AC_COMPLETE: AC-ENH-101-TRUTH-001 ✅ Duplicate prevention validated


# =============================================================================
# GOLDEN PATH TRUTH TEST 2: Version Consistency
# =============================================================================

@pytest.mark.asyncio
async def test_version_consistency_truth() -> None:
    """
    TRUTH TEST: Version markers must be consistent across file.
    
    Scenario:
        1. File has version in header: "1.0.0"
        2. User edits footer to "2.0.0"
        3. CCE detects version mismatch
        
    Validation:
        - ZERO mocks used
        - Real VersionMarker detection in StructureAnalyzer
        - Real consistency check in CoherenceValidator
        - Reports specific line numbers of mismatches
    """
    # AC_START: AC-ENH-101-TRUTH-002
    
    # Given: Content with version in header
    original_content = """# Documentation

**Version:** 1.0.0 | **Author:** Test User

## Overview

This is version 1.0.0 of the project.

---

*v1.0.0 — Last updated: 2026-01-15*
"""
    
    # When: User updates footer version but forgets header
    proposed_content = """# Documentation

**Version:** 1.0.0 | **Author:** Test User

## Overview

This is version 1.0.0 of the project.

---

*v2.0.0 — Last updated: 2026-02-13*
"""
    
    # Then: CCE detects version inconsistency
    result = await cortex_validate_coherence(
        file_path="DOCS.md",
        content=proposed_content,
        pre_edit_content=original_content,
        orchestrator_context={
            "source": "MasterOrchestrator",
            "intent": "TEST",
            "request_id": "test_version_consistency_truth",
        },
    )
    
    # TRUTH ASSERTIONS (no mocks)
    version_issues = [i for i in result["issues"] if i["type"] == "version_mismatch"]
    assert len(version_issues) > 0, "Should detect version mismatch"
    assert not result["version_consistent"], "Version should NOT be consistent"
    
    # Verify issue contains version numbers
    issue_text = str(version_issues[0])
    assert "1.0.0" in issue_text or "2.0.0" in issue_text, "Should mention version numbers"
    
    # Verify location information
    assert version_issues[0]["location"], "Should provide line number location"
    
    # AC_COMPLETE: AC-ENH-101-TRUTH-002 ✅ Version consistency validated


# =============================================================================
# GOLDEN PATH TRUTH TEST 3: Structure Preservation
# =============================================================================

@pytest.mark.asyncio
async def test_structure_preservation_truth() -> None:
    """
    TRUTH TEST: File structure should be preserved during edits.
    
    Scenario:
        1. File has 3 main sections
        2. User accidentally deletes a section
        3. CCE detects structure degradation
        
    Validation:
        - ZERO mocks used
        - Real section detection across file types
        - Real before/after structure comparison
        - Warns about removed sections
    """
    # AC_START: AC-ENH-101-TRUTH-003
    
    # Given: Well-structured document
    original_content = """# API Documentation

## Authentication

How to authenticate...

## Endpoints

Available endpoints:
- GET /api/users
- POST /api/users
- DELETE /api/users

## Error Codes

Common error codes...

## Rate Limiting

Rate limit information...
"""
    
    # When: User accidentally removes "Error Codes" section
    proposed_content = """# API Documentation

## Authentication

How to authenticate...

## Endpoints

Available endpoints:
- GET /api/users
- POST /api/users
- DELETE /api/users

## Rate Limiting

Rate limit information...
"""
    
    # Then: CCE detects missing section
    result = await cortex_validate_coherence(
        file_path="API.md",
        content=proposed_content,
        pre_edit_content=original_content,
        orchestrator_context={
            "source": "MasterOrchestrator",
            "intent": "TEST",
            "request_id": "test_structure_preservation_truth",
        },
    )
    
    # TRUTH ASSERTIONS (no mocks)
    removed_issues = [i for i in result["issues"] if i["type"] == "section_removed"]
    assert len(removed_issues) > 0, "Should detect removed section"
    
    # Verify specific section named
    assert any("Error Codes" in i["message"] for i in removed_issues), \
        "Should identify 'Error Codes' was removed"
    
    # Verify suggestion to verify intentional
    assert any("intentional" in i["suggestion"].lower() for i in removed_issues), \
        "Should suggest verifying removal was intentional"
    
    # AC_COMPLETE: AC-ENH-101-TRUTH-003 ✅ Structure preservation validated


# =============================================================================
# GOLDEN PATH TRUTH TEST 4: Full Coherence Workflow
# =============================================================================

@pytest.mark.asyncio
async def test_full_coherence_workflow_truth() -> None:
    """
    TRUTH TEST: End-to-end workflow from pre-edit to post-edit validation.
    
    Scenario:
        Complete workflow:
        1. Pre-edit: Analyze original file
        2. Edit: Make multiple changes
        3. Post-edit: Validate all coherence aspects
        4. Report: Generate comprehensive report
        
    Validation:
        - ZERO mocks used
        - All components work together
        - Real StructureAnalyzer → DuplicateScanner → CoherenceValidator chain
        - Complete CoherenceReport generated
        - Audit trail complete
    """
    # AC_START: AC-ENH-101-TRUTH-004
    
    # Given: Realistic file with multiple aspects to validate
    original_content = """# CORTEX Features

**Version:** 1.5.0

## TDD Orchestrator

Red-Green-Refactor cycle enforcement.

## Governance Engine

7-agent pre-execution gate.

## MCP Integration

All functionality via MCP tools.

---

*v1.5.0 — February 2026*
"""
    
    # When: User makes multiple edits (good and problematic)
    proposed_content = """# CORTEX Features

**Version:** 2.0.0

## TDD Orchestrator

Red-Green-Refactor cycle enforcement with enhanced test quality.

## Governance Engine

8-agent pre-execution gate including ChangeCoherenceEngine.

## MCP Integration

All functionality via MCP tools.

## TDD Orchestrator

Additional TDD features here.  ← DUPLICATE!

---

*v1.5.0 — February 2026*  ← VERSION MISMATCH!
"""
    
    # Then: Full validation workflow
    analyzer = StructureAnalyzer()
    scanner = DuplicateScanner()
    validator = CoherenceValidator()
    
    # Step 1: Analyze original (pre-edit)
    pre_structure = analyzer.analyze(original_content, "FEATURES.md")
    assert len(pre_structure.sections) >= 3, "Should detect main sections"
    assert len(pre_structure.version_markers) >= 1, "Should detect version markers"
    
    # Step 2: Build pre-context
    pre_scan = scanner.scan_sections(pre_structure.sections)
    pre_context = PreEditContext(
        file_path=Path("FEATURES.md"),
        original_content=original_content,
        structure=pre_structure,
        existing_duplicates=pre_scan.all_duplicates,
    )
    
    # Step 3: Validate post-edit
    validation_result = validator.validate(pre_context, proposed_content)
    
    # Step 4: Generate report
    report = validator.generate_report(pre_context, proposed_content)
    
    # TRUTH ASSERTIONS (no mocks - all real components)
    
    # Duplicate detection
    assert len(report.duplicates_found) > 0, "Should find TDD Orchestrator duplicate"
    dup_names = [d.original_section.name for d in report.duplicates_found]
    assert any("TDD" in name for name in dup_names), "Should identify TDD duplicate"
    
    # Version inconsistency
    assert not report.version_consistent, "Should detect version mismatch (2.0.0 vs 1.5.0)"
    
    # Overall status
    assert report.status in (CoherenceStatus.FAILED, CoherenceStatus.WARNING), \
        "Should fail or warn due to duplicate + version issues"
    
    # Report completeness
    assert len(report.validation_results) > 0, "Should have validation results"
    assert len(report.recommendations) > 0, "Should provide recommendations"
    
    # Summary generation
    summary = report.summary()
    assert "FEATURES.md" in summary, "Summary should mention filename"
    assert "Duplicates:" in summary, "Summary should report duplicates"
    assert "Version Consistent:" in summary, "Summary should report version status"
    
    # Verify specific issues in validation results
    all_issues = []
    for vr in report.validation_results:
        all_issues.extend(vr.details.get("issues", []))
    
    issue_types = {i["type"] for i in all_issues}
    assert "duplicate_section" in issue_types or "similar_section" in issue_types, \
        "Should report duplicate issue"
    assert "version_mismatch" in issue_types, "Should report version mismatch"
    
    # AC_COMPLETE: AC-ENH-101-TRUTH-004 ✅ Full workflow validated


# AC_COMPLETE: AC-ENH-101-013 ✅ Golden Path Truth Tests (4/4, 0 mocks)
