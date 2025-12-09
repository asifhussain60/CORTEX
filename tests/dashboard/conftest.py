"""
Dashboard test configuration with progress indicators.

Provides visual feedback for long-running tests to prevent appearance of hang.
"""

import pytest
import sys
from datetime import datetime


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Show test progress for long-running tests."""
    test_name = item.nodeid.split("::")[-1]
    
    # Print start marker for visibility (ASCII only for cross-platform compatibility)
    print(f"\n{'='*60}")
    print(f"[START] {test_name}")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    sys.stdout.flush()
    
    # Run the test
    yield
    
    # Print completion marker
    print(f"\n{'='*60}")
    print(f"[DONE] {test_name}")
    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")
    sys.stdout.flush()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Show phase progress (setup/call/teardown)."""
    outcome = yield
    report = outcome.get_result()
    
    if call.when == "call":
        test_name = item.nodeid.split("::")[-1]
        duration = f"{report.duration:.1f}s"
        
        if report.passed:
            print(f"   [PASS] Test execution completed in {duration}")
        elif report.failed:
            print(f"   [FAIL] Test failed after {duration}")
        elif report.skipped:
            print(f"   [SKIP] Test skipped")
        
        sys.stdout.flush()
