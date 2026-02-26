"""
CORTEX Test Runner — Three-layer optimised execution (cross-platform).

Performance Architecture:
  Layer 1 — Parallel:  pytest-xdist with -n auto --dist loadscope
                        10 workers on 10-core Mac → 3–4× speedup.
                        Falls back gracefully if xdist is unavailable.
  Layer 2 — Smart:     pytest-testmon with --testmon
                        Skips tests whose covered source lines didn't change.
                        Ideal for CORTEX's frequent mid-session TDD runs.
  Layer 3 — Import:    --import-mode=importlib (set in pytest.ini)
                        Cuts cold collection from ~17s → ~7s.

Cross-Platform:
  All modes use sys.executable — works on macOS, Linux, and Windows
  without shell wrappers, shebangs, or venv activation.

Modes:
    python3 scripts/run_tests.py                  # unit tests (default)
    python3 scripts/run_tests.py smoke             # smoke tests, parallel (<30s target)
    python3 scripts/run_tests.py changed           # testmon: only changed-file tests
    python3 scripts/run_tests.py unit              # unit tests, parallel
    python3 scripts/run_tests.py fast              # fast subset, parallel
    python3 scripts/run_tests.py parallel          # full suite, parallel workers
    python3 scripts/run_tests.py integration       # integration tests, sequential
    python3 scripts/run_tests.py golden            # golden tests, sequential
    python3 scripts/run_tests.py batch             # full sequential batch (canonical/safe)
    python3 scripts/run_tests.py all               # full suite, all dirs, sequential
    python3 scripts/run_tests.py file <path>       # single file
    python3 scripts/run_tests.py dir <path>        # single directory

Environment:
    CORTEX_BATCH_SIZE       Tests per batch (default: 500)
    CORTEX_WORKERS          xdist worker count (default: auto = all cores)
    CORTEX_DISABLE_PARALLEL Set to "true" to force sequential (CI override)
    CORTEX_DISABLE_TESTMON  Set to "true" to skip testmon DB (clean run)

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
# Cap at 8 — xdist has a known macOS scheduler race (KeyError on gw13+)
# when -n auto spawns >10 workers on M-series hardware.
# Override via CORTEX_WORKERS env var (e.g. CORTEX_WORKERS=4 for CI).
_DEFAULT_WORKERS: str = "8"

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


# ---------------------------------------------------------------------------
# Feature detection — graceful fallback if plugins absent
# ---------------------------------------------------------------------------

def _xdist_available() -> bool:
    """Return True if pytest-xdist is importable.

    Returns:
        True when parallel workers can be used.
    """
    if os.environ.get("CORTEX_DISABLE_PARALLEL", "").lower() == "true":
        return False
    try:
        import xdist  # noqa: F401
        return True
    except ImportError:
        return False


def _testmon_available() -> bool:
    """Return True if pytest-testmon is importable.

    Returns:
        True when change-aware test selection can be used.
    """
    if os.environ.get("CORTEX_DISABLE_TESTMON", "").lower() == "true":
        return False
    try:
        import testmon  # noqa: F401
        return True
    except ImportError:
        return False


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

    Cross-platform: uses sys.executable so it works correctly inside venvs
    on macOS, Linux, and Windows without hard-coded paths.

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
    """Build the base pytest command.

    Layer 3 (--import-mode=importlib) is enforced in pytest.ini.
    -p no:sugar is enforced in pytest.ini.
    This function emits only flags that vary per invocation.

    Args:
        timeout: Per-test timeout in seconds.
        maxfail: Stop after this many failures.

    Returns:
        Partial argument list starting with the Python executable.
    """
    return [
        _python(), "-m", "pytest",
        f"--timeout={timeout}",
        f"--maxfail={maxfail}",
        "--tb=short",
        "--no-header",
        "--continue-on-collection-errors",
    ]


def _parallel_flags(workers: Optional[str] = None) -> List[str]:
    """Return xdist parallel flags if xdist is available, else empty list.

    Uses --dist=loadscope so tests in the same module/class stay on the same
    worker — prevents fixture conflicts from singleton or shared-state objects.

    Args:
        workers: Worker count string (e.g. "auto", "4"). None = env or default.

    Returns:
        List of -n / --dist flags, or [] if xdist is unavailable.
    """
    if not _xdist_available():
        print("  ℹ️  xdist not available — running sequentially", flush=True)
        return ["-p", "no:xdist"]
    w = workers or os.environ.get("CORTEX_WORKERS", _DEFAULT_WORKERS)
    return ["-n", w, "--dist", "loadscope"]


def _testmon_flags() -> List[str]:
    """Return testmon flag if testmon is available, else empty list.

    testmon tracks which source lines each test covers and re-runs only
    tests whose covered files changed since the last run. The DB is stored
    in .testmondata at project root (cross-platform, git-ignored).

    Returns:
        ["--testmon"] or [] if testmon is unavailable.
    """
    if not _testmon_available():
        print("  ℹ️  testmon not available — running full suite", flush=True)
        return []
    return ["--testmon"]


def _run_batch(
    test_dirs: List[str],
    timeout: int = _DEFAULT_TIMEOUT,
    maxfail: int = _DEFAULT_MAXFAIL,
    markers: Optional[str] = None,
    extra_ignores: bool = True,
    verbose: bool = False,
    parallel: bool = False,
    workers: Optional[str] = None,
    use_testmon: bool = False,
) -> int:
    """Execute a test run with the configured layer strategy.

    Args:
        test_dirs: List of test directories/files to run.
        timeout: Per-test timeout in seconds.
        maxfail: Stop after this many failures.
        markers: Optional pytest marker expression (e.g. 'smoke').
        extra_ignores: Whether to add _COMMON_IGNORES.
        verbose: Whether to add -v flag.
        parallel: Whether to enable xdist parallel workers (Layer 1).
        workers: xdist worker count override (e.g. "4", "auto").
        use_testmon: Whether to enable testmon smart selection (Layer 2).

    Returns:
        pytest exit code.
    """
    cmd = _base_cmd(timeout=timeout, maxfail=maxfail)

    # Layer 1 — Parallel or sequential
    if parallel:
        cmd.extend(_parallel_flags(workers))
    else:
        cmd.extend(["-p", "no:xdist"])

    # Layer 2 — Smart change-aware selection
    if use_testmon:
        cmd.extend(_testmon_flags())

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
# Mode implementations — all delegate to _run_batch
# ---------------------------------------------------------------------------

def run_smoke() -> int:
    """Run smoke tests in parallel — target <30s total wall time.

    Uses xdist parallel workers (Layer 1) since smoke tests are all tagged
    concurrent_safe by conftest_optimize.py.

    Returns:
        pytest exit code.
    """
    _print_header("Smoke Tests — parallel (<30s target)")
    # Cap at 8 workers — xdist has a known macOS scheduler race (KeyError: gw13+)
    # when -n auto spawns >10 workers on M-series hardware. 8 is stable and fast.
    # Override with CORTEX_WORKERS env var if needed.
    code = _run_batch(
        test_dirs=["tests/"],
        timeout=5,
        maxfail=3,
        markers="smoke",
        parallel=True,
        workers=os.environ.get("CORTEX_WORKERS", "8"),
    )
    _print_result(code)
    return code


def run_changed() -> int:
    """Run only tests affected by source changes since last run (testmon).

    Layer 2 — pytest-testmon tracks which source lines each test covers.
    Only tests whose covered files were modified since the last ``run_changed``
    invocation are executed. The testmon DB is stored at ``.testmondata``
    in the project root (cross-platform, should be git-ignored).

    Ideal for: TDD inner loop — after every file save, CORTEX reruns only
    the tests that could possibly be broken by that change.

    Falls back to full sequential unit run if testmon is unavailable.

    Returns:
        pytest exit code.
    """
    if not _testmon_available():
        _print_header("Changed Tests — testmon unavailable, running unit tests")
        return run_unit()
    _print_header("Changed Tests — testmon smart selection (only diff'd tests)")
    code = _run_batch(
        test_dirs=["tests/"],
        timeout=30,
        maxfail=20,
        use_testmon=True,
        parallel=False,  # testmon is incompatible with xdist workers
    )
    _print_result(code)
    return code


def run_unit() -> int:
    """Run unit tests in parallel using xdist loadscope distribution.

    Returns:
        pytest exit code.
    """
    _print_header("Unit Tests — parallel (xdist loadscope)")
    code = _run_batch(
        test_dirs=["tests/unit/"],
        parallel=True,
        workers=os.environ.get("CORTEX_WORKERS", "8"),
    )
    _print_result(code)
    return code


def run_fast() -> int:
    """Run fast unit tests in parallel — exclude slow and integration markers.

    Returns:
        pytest exit code.
    """
    _print_header("Fast Tests — parallel (no slow, no integration)")
    code = _run_batch(
        test_dirs=["tests/unit/"],
        markers="not slow and not integration",
        parallel=True,
        workers=os.environ.get("CORTEX_WORKERS", "8"),
    )
    _print_result(code)
    return code


def run_parallel() -> int:
    """Run full test suite in parallel — maximum throughput.

    Equivalent to ``batch`` but with all available CPU cores engaged.
    Use this for pre-commit full-suite validation when time matters.

    Returns:
        pytest exit code.
    """
    workers = os.environ.get("CORTEX_WORKERS", "8")
    _print_header(f"Parallel Full Suite — xdist -n {workers} --dist loadscope")
    code = _run_batch(
        test_dirs=["tests/"],
        timeout=60,
        maxfail=50,
        parallel=True,
        workers=workers,
        verbose=True,
    )
    _print_result(code)
    return code


def run_integration() -> int:
    """Run integration tests sequentially with extended timeout.

    Integration tests are NOT parallelised — they may share databases,
    file handles, or singleton state that makes xdist unsafe for them.

    Returns:
        pytest exit code.
    """
    _print_header("Integration Tests — sequential (shared-state safe)")
    code = _run_batch(
        test_dirs=["tests/integration/"],
        timeout=60,
        maxfail=5,
        parallel=False,
    )
    _print_result(code)
    return code


def run_golden() -> int:
    """Run golden tests (expected output validation) sequentially.

    Returns:
        pytest exit code.
    """
    _print_header("Golden Tests — sequential")
    code = _run_batch(
        test_dirs=["tests/golden/"],
        extra_ignores=False,
        parallel=False,
    )
    _print_result(code)
    return code


def run_batch() -> int:
    """Run full sequential batch — the safe canonical CORTEX test method.

    Identical behaviour to pre-optimisation: no xdist, no testmon.
    Use this in CI, for audit gates, or when debugging test ordering issues.
    Use ``parallel`` mode for speed during local development.

    Returns:
        pytest exit code.
    """
    batch_size = _env_int("CORTEX_BATCH_SIZE", _DEFAULT_BATCH_SIZE)
    _print_header(f"Full Batch Run — sequential (batch_size={batch_size})")
    code = _run_batch(
        test_dirs=["tests/"],
        timeout=60,
        maxfail=50,
        verbose=True,
        parallel=False,
    )
    _print_result(code)
    return code


def run_all() -> int:
    """Run full suite — all test directories, sequential.

    Returns:
        pytest exit code.
    """
    _print_header("All Tests — full suite, sequential")
    code = _run_batch(
        test_dirs=["tests/"],
        timeout=60,
        maxfail=100,
        extra_ignores=False,
        parallel=False,
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
        parallel=False,
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
        parallel=False,
    )
    _print_result(code)
    return code


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

_MODES = {
    "smoke":       run_smoke,
    "changed":     run_changed,
    "unit":        run_unit,
    "fast":        run_fast,
    "parallel":    run_parallel,
    "integration": run_integration,
    "golden":      run_golden,
    "batch":       run_batch,
    "all":         run_all,
}

_USAGE = """\
Usage: python3 scripts/run_tests.py [mode] [target]

Modes (fastest → safest):
  changed      testmon: only tests whose source files changed   ← TDD inner loop
  smoke        Smoke tests, parallel xdist (<30s target)        ← quick sanity
  fast         Fast unit tests, parallel (no slow/integration)
  unit         All unit tests, parallel (xdist loadscope)       [default]
  parallel     Full suite, parallel workers (max throughput)
  integration  Integration tests, sequential (shared-state safe)
  golden       Golden tests, sequential
  batch        Full suite, sequential (canonical / CI safe)
  all          Full suite, all dirs, sequential
  file <path>  Run single test file
  dir <path>   Run tests in single directory

Environment overrides:
  CORTEX_BATCH_SIZE        Tests per batch (default: 500)
  CORTEX_WORKERS           xdist worker count (default: auto = all cores)
  CORTEX_DISABLE_PARALLEL  Set "true" to force sequential (CI override)
  CORTEX_DISABLE_TESTMON   Set "true" to skip testmon DB lookup (clean run)

Cross-platform: works on macOS, Linux, and Windows via sys.executable.
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
