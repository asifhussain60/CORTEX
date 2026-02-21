"""
CORTEX Test Runner — Cross-platform canonical test execution script.

Replaces shell-only run-tests.sh logic with a Python implementation that
runs identically on macOS, Linux, and Windows (native / WSL / Git Bash).

Uses CortexXdistPlugin (registered via conftest.py) for batch-aware parallel
progress. Never adds -q or -o addopts= — those flags silence the batch reporter
or wipe pytest.ini's xdist configuration.

Usage:
    python3 scripts/run_tests.py                  # unit tests (default)
    python3 scripts/run_tests.py smoke             # smoke tests (<30s)
    python3 scripts/run_tests.py unit              # unit tests (parallel)
    python3 scripts/run_tests.py fast              # fast subset
    python3 scripts/run_tests.py integration       # integration tests
    python3 scripts/run_tests.py batch             # batch runner (canonical)
    python3 scripts/run_tests.py all               # full suite
    python3 scripts/run_tests.py file <path>       # single file
    python3 scripts/run_tests.py dir <path>        # single directory

Environment:
    CORTEX_BATCH_SIZE    Tests per batch (default: 500)
    CORTEX_TEST_WORKERS  Worker count override (default: auto)

Authority: CORE-008 | CORE-011 | CORE-012 | CORE-028
AC-ID: AC-TEST-PERF-001 | AC-TEST-PARALLEL-001
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = Path(__file__).parent.parent.resolve()

# ---------------------------------------------------------------------------
# Defaults — mirrors run-tests.sh values
# ---------------------------------------------------------------------------
_DEFAULT_TIMEOUT: int = 30
_DEFAULT_MAXFAIL: int = 10
_DEFAULT_BATCH_SIZE: int = 500
_DEFAULT_WORKERS: str = "auto"

# Directories always excluded to prevent collection failures.
# Keep in sync with pytest.ini norecursedirs and run-tests.sh COMMON_IGNORES.
_COMMON_IGNORES: List[str] = [
    "--ignore=tests/documentation",
    "--ignore=tests/cortex",
    "--ignore=tests/golden",
    "--ignore=tests/e2e",
    "--ignore=tests/_legacy_broken",
    "--ignore=tests/_skip",
    "--ignore=tests/_deprecated",
]


def _env_int(key: str, default: int) -> int:
    """Read an integer environment variable with a safe default.

    Args:
        key: Environment variable name.
        default: Value to use when the variable is absent or non-integer.

    Returns:
        Parsed integer value or default.
    """
    try:
        return int(os.environ[key])
    except (KeyError, ValueError):
        return default


def _env_str(key: str, default: str) -> str:
    """Read a string environment variable with a safe default.

    Args:
        key: Environment variable name.
        default: Value to use when the variable is absent.

    Returns:
        String value or default.
    """
    return os.environ.get(key, default)


def _python() -> str:
    """Return the current Python executable path.

    Returns:
        Absolute path to the running Python interpreter.
    """
    return sys.executable


def _run(args: List[str], env: Optional[dict] = None) -> int:
    """Run a subprocess command from PROJECT_ROOT and return exit code.

    Args:
        args: Command + argument list.
        env: Optional environment overrides merged with os.environ.

    Returns:
        Process exit code.
    """
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    result = subprocess.run(args, cwd=PROJECT_ROOT, env=merged_env)
    return result.returncode


def _print_header(title: str) -> None:
    """Print a section header to stdout.

    Args:
        title: Header text to display.
    """
    sep = "━" * 58
    print(f"\n{sep}")
    print(f"  CORTEX Test Runner — {title}")
    print(f"{sep}\n")


def _print_result(code: int) -> None:
    """Print a pass/fail/no-tests summary line.

    Args:
        code: pytest exit code (0=pass, 5=no tests collected, other=fail).
    """
    if code == 0:
        print("\n✅ All tests passed")
    elif code == 5:
        print("\n⚠️  No tests collected")
    else:
        print(f"\n❌ Tests failed (exit code: {code})")


def _pytest_base(
    timeout: int = _DEFAULT_TIMEOUT,
    maxfail: int = _DEFAULT_MAXFAIL,
    extra: Optional[List[str]] = None,
) -> List[str]:
    """Build the base pytest command shared by all modes.

    Args:
        timeout: Per-test timeout in seconds.
        maxfail: Stop after this many failures.
        extra: Additional pytest arguments appended after the base flags.

    Returns:
        Full argument list starting with the Python executable.
    """
    cmd = [
        _python(), "-m", "pytest",
        f"--timeout={timeout}",
        f"--maxfail={maxfail}",
        "--tb=short",
        "--no-header",
    ]
    cmd.extend(_COMMON_IGNORES)
    if extra:
        cmd.extend(extra)
    return cmd


# ---------------------------------------------------------------------------
# Mode implementations
# ---------------------------------------------------------------------------

def run_smoke() -> int:
    """Run smoke tests only — target <30s total wall time.

    Returns:
        pytest exit code.
    """
    _print_header("Smoke Tests (<30s)")
    workers = _env_str("CORTEX_TEST_WORKERS", _DEFAULT_WORKERS)
    cmd = _pytest_base(timeout=5, maxfail=3, extra=[
        "tests/unit/",
        "-m", "smoke",
        "-n", workers,
        "--dist", "loadfile",
    ])
    code = _run(cmd)
    _print_result(code)
    return code


def run_unit() -> int:
    """Run unit tests with full parallel execution via xdist.

    Returns:
        pytest exit code.
    """
    _print_header("Unit Tests (parallel)")
    workers = _env_str("CORTEX_TEST_WORKERS", _DEFAULT_WORKERS)
    cmd = _pytest_base(extra=[
        "tests/unit/",
        "-n", workers,
        "--dist", "loadscope",
    ])
    code = _run(cmd)
    _print_result(code)
    return code


def run_fast() -> int:
    """Run fast unit tests — exclude slow and integration markers.

    Returns:
        pytest exit code.
    """
    _print_header("Fast Tests (no slow, no integration)")
    workers = _env_str("CORTEX_TEST_WORKERS", _DEFAULT_WORKERS)
    cmd = _pytest_base(extra=[
        "tests/unit/",
        "-m", "not slow and not integration",
        "-n", workers,
        "--dist", "loadscope",
    ])
    code = _run(cmd)
    _print_result(code)
    return code


def run_integration() -> int:
    """Run integration tests with extended timeout.

    Returns:
        pytest exit code.
    """
    _print_header("Integration Tests")
    cmd = _pytest_base(timeout=60, maxfail=5, extra=["tests/integration/"])
    code = _run(cmd)
    _print_result(code)
    return code


def run_batch() -> int:
    """Run tests via CortexXdistPlugin — the canonical CORTEX batch method.

    Uses pytest.ini addopts (-n auto --dist loadscope) plus CortexXdistPlugin
    for real batch boundaries, live pass/fail counts, and a final summary table.
    CORTEX_BATCH_SIZE controls tests per batch (default: 500).

    Returns:
        pytest exit code.
    """
    batch_size = _env_int("CORTEX_BATCH_SIZE", _DEFAULT_BATCH_SIZE)
    workers = _env_str("CORTEX_TEST_WORKERS", _DEFAULT_WORKERS)
    _print_header("Batched Parallel Test Run (CortexXdistPlugin)")
    print(f"Batch size: {batch_size} | Workers: {workers} | Dist: loadscope\n")

    cmd = _pytest_base(extra=[
        "tests/unit/",
        "-n", workers,
        "--dist", "loadscope",
        "-v",
    ])
    env = {"CORTEX_BATCH_SIZE": str(batch_size)}
    code = _run(cmd, env=env)
    _print_result(code)
    return code


def run_all() -> int:
    """Run full suite — unit + integration with parallel execution.

    Returns:
        pytest exit code.
    """
    _print_header("All Tests (unit + integration)")
    workers = _env_str("CORTEX_TEST_WORKERS", _DEFAULT_WORKERS)
    cmd = _pytest_base(timeout=60, extra=[
        "tests/",
        "-n", workers,
        "--dist", "loadscope",
    ])
    code = _run(cmd)
    _print_result(code)
    return code


def run_file(target: str) -> int:
    """Run a single test file.

    Args:
        target: Path to the test file (relative or absolute).

    Returns:
        pytest exit code.
    """
    _print_header(f"Single File: {target}")
    cmd = _pytest_base(timeout=60, extra=[target, "-v"])
    code = _run(cmd)
    _print_result(code)
    return code


def run_dir(target: str) -> int:
    """Run all tests in a single directory.

    Args:
        target: Path to the test directory (relative or absolute).

    Returns:
        pytest exit code.
    """
    _print_header(f"Directory: {target}")
    cmd = _pytest_base(extra=[target])
    code = _run(cmd)
    _print_result(code)
    return code


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_MODES = {
    "smoke": run_smoke,
    "unit": run_unit,
    "fast": run_fast,
    "integration": run_integration,
    "batch": run_batch,
    "all": run_all,
}

_USAGE = """\
Usage: python3 scripts/run_tests.py [mode] [target]

Modes:
  smoke        Smoke tests only (<30s total)
  unit         Unit tests with parallel execution  [default]
  fast         Fast subset (no slow/integration markers)
  integration  Integration tests with 60s timeout
  file <path>  Run single test file
  dir <path>   Run tests in single directory
  all          Full suite (unit + integration)
  batch        Canonical CORTEX batch runner (CortexXdistPlugin)

Environment:
  CORTEX_BATCH_SIZE     Tests per batch (default: 500)
  CORTEX_TEST_WORKERS   Worker count override (default: auto)
"""


def main() -> int:
    """Parse CLI arguments and dispatch to the appropriate test mode.

    Returns:
        Exit code to pass back to the OS.
    """
    argv = sys.argv[1:]
    mode = argv[0] if argv else "unit"

    if mode in ("--help", "-h", "help"):
        print(_USAGE)
        return 0

    if mode == "file":
        if len(argv) < 2:
            print("Error: 'file' mode requires a path argument.\n")
            print(_USAGE)
            return 1
        return run_file(argv[1])

    if mode == "dir":
        if len(argv) < 2:
            print("Error: 'dir' mode requires a path argument.\n")
            print(_USAGE)
            return 1
        return run_dir(argv[1])

    if mode not in _MODES:
        print(f"Error: unknown mode '{mode}'\n")
        print(_USAGE)
        return 1

    return _MODES[mode]()


if __name__ == "__main__":
    sys.exit(main())
