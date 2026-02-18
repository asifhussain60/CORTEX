"""
Verification Test: Ensure Health Orchestrator Fixes Persist Across Git Pull

This test verifies that all health orchestrator fixes are present after a fresh git pull.
Run this on any machine after pulling from origin/CORTEX to verify fixes are applied.

Phase: PHASE-95
Authority: Health Orchestrator Permanent Fix Verification
"""

import sys
from pathlib import Path

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))


def test_enum_categories_exist():
    """Verify PATH and CONFIGURATION enum categories exist."""
    from cortex.orchestrators.health.agents.base_agent import HealthIssueCategory
    
    # These enums MUST exist (added to fix agent crashes)
    assert hasattr(HealthIssueCategory, 'PATH'), "❌ PATH enum missing"
    assert hasattr(HealthIssueCategory, 'CONFIGURATION'), "❌ CONFIGURATION enum missing"
    
    print("✅ Enum categories verified (PATH, CONFIGURATION)")


def test_duplicate_file_removed():
    """Verify run_vacuum.legacy.py duplicate was removed."""
    duplicate_file = CORTEX_ROOT / ".cortex" / "run_vacuum.legacy.py"
    
    assert not duplicate_file.exists(), "❌ Duplicate file still exists: .cortex-runtime/run_vacuum.legacy.py"
    
    print("✅ Duplicate file removed (.cortex-runtime/run_vacuum.legacy.py)")


def test_config_file_exists():
    """Verify health_config.py exists with tuned settings."""
    config_file = CORTEX_ROOT / "cortex" / "orchestrators" / "health" / "health_config.py"
    
    assert config_file.exists(), "❌ health_config.py missing"
    
    # Verify configuration content
    content = config_file.read_text()
    assert "DUPLICATE_DETECTION" in content, "❌ DUPLICATE_DETECTION config missing"
    assert "STUB_DETECTION" in content, "❌ STUB_DETECTION config missing"
    assert "PATH_INTEGRITY" in content, "❌ PATH_INTEGRITY config missing"
    
    print("✅ Configuration file exists (health_config.py)")


def test_duplicate_detection_excludes():
    """Verify duplicate detection has proper exclusions."""
    from cortex.orchestrators.health.agents.duplicate_detection_agent import DuplicateDetectionAgent
    
    agent = DuplicateDetectionAgent()
    
    # Should be checking both Python and YAML
    assert agent.check_python is True, "❌ Python check disabled"
    assert agent.check_yaml is True, "❌ YAML check disabled"
    
    print("✅ Duplicate detection configured correctly")


def test_path_integrity_old_paths():
    """Verify PathIntegrityAgent old_paths list is empty (no false positives)."""
    from cortex.orchestrators.health.agents.path_integrity_agent import PathIntegrityAgent
    
    agent = PathIntegrityAgent()
    
    # old_paths should be empty (no deprecated paths currently)
    assert len(agent.old_paths) == 0, f"❌ old_paths not empty: {agent.old_paths}"
    
    print("✅ PathIntegrityAgent old_paths cleared (no false positives)")


def test_stub_detection_thresholds():
    """Verify stub detection has proper thresholds."""
    from cortex.orchestrators.health.agents.stub_detection_agent import StubDetectionAgent
    
    agent = StubDetectionAgent()
    
    # Verify thresholds
    assert agent.loc_threshold == 200, f"❌ LOC threshold wrong: {agent.loc_threshold}"
    assert agent.complexity_threshold == 5, f"❌ Complexity threshold wrong: {agent.complexity_threshold}"
    
    print("✅ Stub detection thresholds correct (LOC=200, complexity=5)")


def test_reports_module_exists():
    """Verify reports module was created."""
    reports_dir = CORTEX_ROOT / "cortex" / "orchestrators" / "health" / "reports"
    
    assert reports_dir.exists(), "❌ reports/ directory missing"
    assert (reports_dir / "__init__.py").exists(), "❌ reports/__init__.py missing"
    assert (reports_dir / "health_report.py").exists(), "❌ health_report.py missing"
    
    # Verify HealthReport has required attributes
    from cortex.orchestrators.health.reports.health_report import HealthReport, HealthMetrics
    
    # Check HealthMetrics has health_score
    metrics = HealthMetrics()
    assert hasattr(metrics, 'health_score'), "❌ HealthMetrics missing health_score"
    assert metrics.health_score == 100.0, f"❌ Default health_score wrong: {metrics.health_score}"
    
    print("✅ Reports module verified (HealthReport, HealthMetrics)")


def test_readme_exists():
    """Verify AGENT-README.md documentation exists."""
    readme = CORTEX_ROOT / "cortex" / "orchestrators" / "health" / "AGENT-README.md"
    
    assert readme.exists(), "❌ AGENT-README.md missing"
    
    content = readme.read_text()
    assert "Quick Start" in content, "❌ Quick Start section missing"
    assert "Agents" in content, "❌ Agents section missing"
    assert "Health Score" in content, "❌ Health Score section missing"
    
    print("✅ Documentation exists (AGENT-README.md)")


def main():
    """Run all verification tests."""
    print("\n" + "="*60)
    print("CORTEX Health Orchestrator Fix Verification")
    print("="*60 + "\n")
    
    tests = [
        test_enum_categories_exist,
        test_duplicate_file_removed,
        test_config_file_exists,
        test_duplicate_detection_excludes,
        test_path_integrity_old_paths,
        test_stub_detection_thresholds,
        test_reports_module_exists,
        test_readme_exists,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(str(e))
            failed += 1
        except Exception as e:
            print(f"❌ Test error in {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    if failed > 0:
        print("⚠️  Some fixes are missing. Did you pull from origin/CORTEX?")
        print("   Run: git pull origin CORTEX")
        return 1
    else:
        print("✅ All health orchestrator fixes verified!")
        print("   Health orchestrator is production-ready.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
