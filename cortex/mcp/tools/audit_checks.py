"""
MCP Tools for AUDIT checks - ENH-053.

Exposes dependency drift and test performance analysis via MCP.

AC_START: AC-ENH053-007
Description: MCP tool registration for new AUDIT checks
Author: Asif Hussain
Date: 2026-02-07
"""

from pathlib import Path

from cortex.mcp.decorators import mcp_tool
from cortex.orchestrators.audit.dependency_drift_detector import DependencyDriftDetector
from cortex.orchestrators.audit.test_performance_analyzer import TestPerformanceAnalyzer
from cortex.orchestrators.core.environment_validator import EnvironmentValidator


@mcp_tool(
    name="cortex_check_dependency_drift",
    description="Check for dependency drift between requirements.txt and installed packages"
)
async def cortex_check_dependency_drift(repo_path: str) -> dict:
    """
    Check for dependency drift between requirements.txt and installed packages.

    P0-027 AUDIT Check - Detects:
    - Missing packages (requirements.txt but not installed)
    - Extra packages (installed but not in requirements.txt)
    - Version mismatches (different versions)

    Args:
        repo_path: Absolute path to repository root

    Returns:
        Dictionary with drift analysis:
        - missing: List of missing packages
        - extra: List of extra packages
        - mismatched: List of version mismatches
        - severity: P0 (missing), P1 (mismatch), P2 (clean)
        - has_drift: Boolean indicator
        - fix_commands: List of pip commands to fix drift

    Example:
        result = await cortex_check_dependency_drift("/path/to/repo")
        if result["has_drift"]:
            print(f"Severity: {result['severity']}")
            for cmd in result["fix_commands"]:
                print(f"Fix: {cmd}")
    """
    detector = DependencyDriftDetector()
    result = detector.analyze(Path(repo_path))

    response = result.to_dict()
    response["fix_commands"] = detector.generate_fix_commands(result)

    return response


@mcp_tool(
    name="cortex_analyze_test_performance",
    description="Analyze test suite performance and identify slow tests"
)
async def cortex_analyze_test_performance(repo_path: str) -> dict:
    """
    Analyze test suite performance and identify slow tests.

    P1-028 AUDIT Check - Analyzes:
    - Total test suite execution time
    - Slow tests (>10s duration)
    - Performance regression vs baseline
    - Severity based on thresholds

    Thresholds:
    - P2: <120s (healthy)
    - P1: 120-300s (warning)
    - P0: >300s (critical)

    Args:
        repo_path: Absolute path to repository root

    Returns:
        Dictionary with performance analysis:
        - total_time: Total execution time in seconds
        - slow_tests: List of slow tests with durations
        - regression_percent: Percentage change from baseline
        - severity: P0/P1/P2 based on total_time
        - baseline_path: Path to baseline file

    Example:
        result = await cortex_analyze_test_performance("/path/to/repo")
        print(f"Total time: {result['total_time']}s")
        print(f"Regression: {result['regression_percent']}%")
        for test in result["slow_tests"]:
            print(f"Slow: {test['test_name']} ({test['duration']}s)")
    """
    analyzer = TestPerformanceAnalyzer()
    result = analyzer.analyze(Path(repo_path))

    response = result.to_dict()
    response["baseline_path"] = str(Path(repo_path) / ".cortex" / "metrics" / "test_performance_baseline.json")

    return response


@mcp_tool(
    name="cortex_validate_venv",
    description="Validate virtual environment activation"
)
async def cortex_validate_venv(repo_path: str) -> dict:
    """
    Validate virtual environment activation.

    PRE-FLIGHT Check - Validates:
    - Python executable matches expected venv path
    - VIRTUAL_ENV environment variable is set correctly
    - Provides activation command if not active

    Args:
        repo_path: Absolute path to repository root

    Returns:
        Dictionary with venv validation:
        - is_active: Boolean indicating if venv is active
        - expected_path: Path to expected .venv directory
        - current_path: Path to current python executable
        - activation_command: Command to activate venv
        - python_executable: Full path to python executable

    Example:
        result = await cortex_validate_venv("/path/to/repo")
        if not result["is_active"]:
            print(f"Venv not active!")
            print(f"Run: {result['activation_command']}")
    """
    validator = EnvironmentValidator()
    result = validator.validate_venv(Path(repo_path))

    return result.to_dict()


# AC_COMPLETE: AC-ENH053-007 ✅ 3 MCP tools registered
