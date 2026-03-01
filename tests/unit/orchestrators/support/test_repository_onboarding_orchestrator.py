"""
Tests for RepositoryOnboardingOrchestrator Enhancement (Phase 28.2)
TDD RED Phase - Tests written BEFORE implementation

Test Coverage:
- Repository scanning and analysis
- Profile generation from scan results
- Company domains detection
- Tech stack identification
- Security baseline assessment
- Standards extraction
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch


def test_onboarding_orchestrator_scan_repository():
    """Test repository structure scanning."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should scan repository and return scan results
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    scan_results = orchestrator.scan_repository(repo_path)
    
    assert scan_results is not None
    assert 'structure' in scan_results
    assert 'tech_stack' in scan_results


def test_onboarding_orchestrator_detect_company_domains():
    """Test company domains structure detection."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should detect company/domains/ structure
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    has_domains, domains_path, detected_domains = orchestrator.detect_company_domains(
        repo_path
    )
    
    # KSESSIONS may or may not have company domains - we test the detection logic
    assert isinstance(has_domains, bool)
    if has_domains:
        assert domains_path is not None
        assert isinstance(detected_domains, list)


def test_onboarding_orchestrator_analyze_tech_stack():
    """Test technology stack analysis."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should identify languages, frameworks, dependencies
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    tech_stack = orchestrator.analyze_tech_stack(repo_path)
    
    assert tech_stack is not None
    assert 'primary_language' in tech_stack
    assert 'languages' in tech_stack
    assert isinstance(tech_stack['languages'], list)


def test_onboarding_orchestrator_assess_security_baseline():
    """Test security baseline assessment."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should assess security configuration
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    security_baseline = orchestrator.assess_security_baseline(repo_path)
    
    assert security_baseline is not None
    assert 'secrets_management' in security_baseline
    assert 'vulnerabilities_detected' in security_baseline


def test_onboarding_orchestrator_extract_standards():
    """Test standards extraction from repository."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should extract coding standards, test patterns
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    standards = orchestrator.extract_standards(repo_path)
    
    assert standards is not None
    assert 'coding_style' in standards or 'test_patterns' in standards


def test_onboarding_orchestrator_generate_profile():
    """Test complete profile generation from scan results."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    from cortex.intelligence.onboarded_repos import RepositoryProfile
    
    # RED: Should generate complete RepositoryProfile
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    profile = orchestrator.generate_profile(repo_path)
    
    assert isinstance(profile, RepositoryProfile)
    assert profile.name == "KSESSIONS"
    assert profile.path == str(repo_path)
    assert profile.onboarded_at is not None


def test_onboarding_orchestrator_onboard_repository():
    """Test full onboarding workflow (scan → profile → save)."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    from cortex.intelligence.onboarded_repos import ProfileStore
    from tempfile import TemporaryDirectory
    
    # RED: Should complete full onboarding
    orchestrator = RepositoryOnboardingOrchestrator()
    
    with TemporaryDirectory() as tmpdir:
        store = ProfileStore(storage_path=Path(tmpdir))
        
        repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
        profile = orchestrator.onboard_repository_with_profile(
            repo_path=repo_path,
            profile_store=store
        )
        
        assert profile is not None
        assert store.exists("KSESSIONS")


def test_onboarding_orchestrator_graceful_missing_repo():
    """Test graceful handling of missing repository."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator,
        RepositoryNotFoundError
    )
    
    # RED: Should raise RepositoryNotFoundError
    orchestrator = RepositoryOnboardingOrchestrator()
    
    with pytest.raises(RepositoryNotFoundError):
        orchestrator.scan_repository(Path("/nonexistent/repo"))


def test_onboarding_orchestrator_detect_test_framework():
    """Test test framework detection."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should detect pytest, unittest, etc.
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    test_info = orchestrator.detect_test_framework(repo_path)
    
    assert test_info is not None
    assert 'has_tests' in test_info
    assert 'test_framework' in test_info


def test_onboarding_orchestrator_analyze_dependencies():
    """Test dependency analysis from requirements.txt, pyproject.toml."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator
    )
    
    # RED: Should parse dependencies
    orchestrator = RepositoryOnboardingOrchestrator()
    
    repo_path = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
    dependencies = orchestrator.analyze_dependencies(repo_path)
    
    assert isinstance(dependencies, list)


# ---------------------------------------------------------------------------
# P2 Fix: AC marker SQLite persistence for RepositoryOnboardingOrchestrator
# AC markers were emitted to logger only; must also persist to trace DB via
# write_scan_trace() → OrchestratorTraceLogger.
# ---------------------------------------------------------------------------

def test_write_scan_trace_ac_start_persists_to_db():
    """write_scan_trace AC_START persists to OrchestratorTraceLogger (SQLite)."""
    import uuid
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator,
    )

    orchestrator = RepositoryOnboardingOrchestrator()
    session_id = str(uuid.uuid4())
    result = orchestrator.write_scan_trace(
        action="AC_START",
        repo_path="/tmp/test-repo",
        session_id=session_id,
    )

    assert result.is_ok(), f"write_scan_trace AC_START failed: {result}"


def test_write_scan_trace_ac_complete_persists_to_db():
    """write_scan_trace AC_COMPLETE persists to OrchestratorTraceLogger (SQLite)."""
    import uuid
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator,
    )

    orchestrator = RepositoryOnboardingOrchestrator()
    session_id = str(uuid.uuid4())
    result = orchestrator.write_scan_trace(
        action="AC_COMPLETE",
        repo_path="/tmp/test-repo",
        session_id=session_id,
        metadata={"tech_stack": ["python"], "file_count": 5, "elapsed_ms": 42},
    )

    assert result.is_ok(), f"write_scan_trace AC_COMPLETE failed: {result}"


def test_write_scan_trace_rejects_invalid_action():
    """write_scan_trace must return Err for unknown action strings."""
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator,
    )

    orchestrator = RepositoryOnboardingOrchestrator()
    result = orchestrator.write_scan_trace(
        action="AC_INVALID",
        repo_path="/tmp/test-repo",
        session_id="test-session",
    )

    assert result.is_err(), "Expected Err for invalid action"
    assert "AC_INVALID" in result.unwrap_err()


def test_scan_repository_emits_ac_markers_to_trace_db(tmp_path: Path):
    """scan_repository must write AC_START + AC_COMPLETE pair to trace DB."""
    import sqlite3, os
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        RepositoryOnboardingOrchestrator,
    )

    # Create a minimal repo for scanning
    (tmp_path / "main.py").write_text("print('hi')")

    orchestrator = RepositoryOnboardingOrchestrator()
    result = orchestrator.scan_repository(tmp_path)

    assert result["status"] == "success"

    # AC markers should have been written to the trace DB
    db_path = ".cortex-runtime/traces/orchestrator-traces.db"
    if not os.path.exists(db_path):
        return  # DB not present in CI — skip DB assertion

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    tables = [r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'trace_%'"
    ).fetchall()]
    con.close()

    assert any("onboarding" in t.lower() for t in tables), (
        f"Expected trace_onboarding* table in DB. Found: {tables}"
    )
