"""
CORTEX Test Runner — Sequential batch execution with live terminal output.

All tests run sequentially in batches using CortexXdistPlugin for real-time
progress output in both the terminal and VS Code Copilot Chat sessions.

The batch reporter (registered via conftest.py) prints:
  - Batch headers with test range and count
  - Per-batch pass/fail/duration summaries
  - ASCII progress bars
  - Final aggregated summary table

Usage:
    python3 scripts/run_tests.py                  # unit tests (default)
    python3 scripts/run_tests.py smoke             # smoke tests (<30s)
    python3 scripts/run_tests.py unit              # unit tests
    python3 scripts/run_tests.py fast              # fast subset
    python3 scripts/run_tests.py integration       # integration tests
    python3 scripts/run_tests.py golden            # golden tests
    python3 scripts/run_tests.py batch             # full sequential batch run
    python3 scripts/run_tests.py all               # full suite (all dirs)
    python3 scripts/run_tests.py file <path>       # single file
    python3 scripts/run_tests.py dir <path>        # single directory

Environment:
    CORTEX_BATCH_SIZE    Tests per batch (default: 500)

Authority: CORE-008 | CORE-011 | CORE-012 | CORE-028
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
# Defaults
# ---------------------------------------------------------------------------
_DEFAULT_TIMEOUT: int = 30
_DEFAULT_MAXFAIL: int = 10
_DEFAULT_BATCH_SIZE: int = 500

# Directories always excluded to prevent collection failures.
# Keep in sync with pytest.ini norecursedirs.
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


def _python() -> str:
    """Return the current Python executable path.

    Returns:
        Absolute path to the running Python interpreter.
    """
    return sys.executable


def _run(args: List[str], env: Optional[dict] = None) -> int:
    """Run a subprocess command from PROJECT_ROOT and return exit code.

    Streams output in real-time to both terminal and VS Code Chat by
    inheriting stdout/stderr from the parent process.

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
    sep = "\u2501" * 58
    print(f"\n{sep}")
    print(f"  CORTEX Test Runner \u2014 {title}")
    print(f"{sep}\n", flush=True)


def _print_result(code: int) -> None:
    """Print a pass/fail/no-tests summary line.

    Args:
        code: pytest exit code (0=pass, 5=no tests collected, other=fail).
    """
    if code == 0:
        print("\n\u2705 All tests passed")
    elif code == 5:
        print("\n\u26a0\ufe0f  No tests collected")
    else:
        print(f"\n\u274c Tests failed (exit code: {code})")


def _base_cmd(
    timeout: int = _DEFAULT_TIMEOUT,
    maxfail: int = _DEFAULT_MAXFAIL,
) -> List[str]:
    """Build the base pytest command for sequential batch execution.

    Every mode shares these flags:
      -p no:xdist         -- disable parallel workers
      --tb=short          -- concise tracebacks
      --timeout=N         -- prevent hanging tests
      --maxfail=N         -- stop after N failures
      --no-header         -- suppress default pytest header
      --continue-on-collection-errors -- don't abort on import errors

    The CortexXdistPlugin (registered in conftest.py) provides batch
    progress output automatically via pytest hooks.

    Args:
        timeout: Per-test timeout in seconds.
        maxfail: Stop after this many failures.

    Returns:
        Partial argument list starting with the Python executable.
    """
    return [
        _python(), "-m", "pytest",
        "-p", "no:xdist",
        f"--timeout={timeout}",
        f"--maxfail={maxfail}",
        "--tb=short",
        "--no-header",
        "--continue-on-collection-errors",
    ]


def _run_batch(
    test_dirs: List[str],
    timeout: int = _DEFAULT_TIMEOUT,
    maxfail: int = _DEFAULT_MAXFAIL,
    markers: Optional[str] = None,
    extra_ignores: bool = True,
    verbose: bool = False,
) -> int:
    """Execute a sequential batch test run.

    This is the single canonical method all modes call. It builds the
    command, sets CORTEX_BATCH_SIZE, and streams output to terminal.

    Args:
        test_dirs: List of test directories/files to run.
        timeout: Per-test timeout in seconds.
        maxfail: Stop after this many failures.
        markers: Optional pytest marker expression (e.g. 'smoke').
        extra_ignores: Whether to add _COMMON_IGNORES.
        verbose: Whether to add -v flag.

    Returns:
        pytest exit code.
    """
    cmd = _base_cmd(timeout=timeout, maxfail=maxfail)

    if extra_ignores:
        cmd.extend(_COMMON_IGNORES)

    cmd.extend(test_dirs)

    if markers:
        cmd.extend(["-m", markers])

    if verbose:
        cmd.append("-v")

    batch_size = _env_int("CORTEX_BATCH_SIZE", _DEFAULT_BATCH_SIZE)
    env = {"CORTEX_BATCH_SIZE": str(batch_size)}

    return _run(cmd, env=env)


# ---------------------------------------------------------------------------
# Mode implementations -- all delegate to _run_batch
# ---------------------------------------------------------------------------

def run_smoke() -> int:
    """Run smoke tests only -- target <30s total wall time.

    Returns:
        pytest exit code.
    """
    _print_header("Smoke Tests (<30s)")
    code = _run_batch(
        test_dirs=["tests/"],
        timeout=5,
        maxfail=3,
        markers="smoke",
    )
    _print_result(code)
    return code


def run_unit() -> int:
    """Run unit tests sequentially in batches.

    Returns:
        pytest exit code.
    """
    _print_header("Unit Tests (sequential batch)")
    code = _run_batch(test_dirs=["tests/unit/"])
    _print_result(code)
    return code


def run_fast() -> int:
    """Run fast unit tests -- exclude slow and integration markers.

    Returns:
        pytest exit code.
    """
    _print_header("Fast Tests (no slow, no integration)")
    code = _run_batch(
        test_dirs=["tests/unit/"],
        markers="not slow and not integration",
    )
    _print_result(code)
    return code


def run_integration() -> int:
    """Run integration tests with extended timeout.

    Returns:
        pytest exit code.
    """
    _print_header("Integration Tests")
    code = _run_batch(
        test_dirs=["tests/integration/"],
        timeout=60,
        maxfail=5,
    )
    _print_result(code)
    return code


def run_golden() -> int:
    """Run golden tests (expected output validation).

    Returns:
        pytest exit code.
    """
    _print_header("Golden Tests")
    code = _run_batch(
        test_dirs=["tests/golden/"],
        extra_ignores=False,
    )
    _print_result(code)
    return code


def run_batch() -> int:
    """Run full sequential batch -- the canonical CORTEX test method.

    Returns:
        pytest exit code.
    """
    batch_size = _env_int("CORTEX_BATCH_SIZE", _DEFAULT_BATCH_SIZE)
    _print_header(f"Full Batch Run (batch_size={batch_size})")
    code = _run_batch(
        test_dirs=["tests/"],
        timeout=60,
        maxfail=50,
        verbose=True,
    )
    _print_result(code)
    return code


def run_all() -> int:
    """Run full suite -- all test directories sequentially.

    Returns:
        pytest exit code.
    """
    _print_header("All Tests (full suite)")
    code = _run_batch(
        test_dirs=["tests/"],
        timeout=60,
        maxfail=100,
        extra_ignores=False,
    )
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
    code = _run_batch(
        test_dirs=[target],
        timeout=60,
        extra_ignores=False,
        verbose=True,
    )
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
    code = _run_batch(
        test_dirs=[target],
        extra_ignores=False,
    )
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
    "golden": run_golden,
    "batch": run_batch,
    "all": run_all,
}

_USAGE = """\
Usage: python3 scripts/run_tests.py [mode] [target]

Modes:
  smoke        Smoke tests only (<30s total)
  unit         Unit tests (sequential batch)  [default]
  fast         Fast subset (no slow/integration markers)
  integration  Integration tests with 60s timeout
  golden       Golden tests (expected output validation)
  batch        Full sequential batch run (canonical)
  all          Full suite (all test directories)
  file <path>  Run single test file
  dir <path>   Run tests in single directory

Environment:
  CORTEX_BATCH_SIZE     Tests per batch (default: 500)
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
