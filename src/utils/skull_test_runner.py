"""
SKULL Test Runner Utility

Provides a reusable function to run the complete SKULL test suite
and return structured results. Used by CLI wrappers to validate
brain protection after critical operations.

SKULL tests validate:
- Test-before-claim enforcement
- Integration verification  
- Visual regression protection
- Retry-without-learning detection
- Transformation verification
- Brain protection rules
- Conversation tracking
- Context management
- Template architecture

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


def run_skull_tests(
    project_root: Optional[Path] = None,
    verbose: bool = False,
    timeout: int = 180
) -> Dict[str, Any]:
    """
    Run complete SKULL test suite (tests/tier0/).
    
    MANDATORY validation after:
    - optimize command
    - align command  
    - healthcheck command
    
    Args:
        project_root: Project root directory (defaults to cwd)
        verbose: Enable verbose pytest output
        timeout: Test execution timeout in seconds (default: 180)
        
    Returns:
        Dict with:
            - success: bool - All tests passed
            - tests_run: int - Total tests executed
            - tests_passed: int - Passed tests
            - tests_failed: int - Failed tests
            - duration_seconds: float - Execution time
            - output: str - pytest output
            - error: Optional[str] - Error message if execution failed
            - timestamp: str - ISO timestamp
    """
    if project_root is None:
        project_root = Path.cwd()
    
    start_time = datetime.now()
    
    logger.info("=" * 80)
    logger.info("MANDATORY SKULL TEST VALIDATION")
    logger.info("=" * 80)
    logger.info("Running brain protection test suite...")
    
    result = {
        'success': False,
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'duration_seconds': 0.0,
        'output': '',
        'error': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Build pytest command
        pytest_args = [
            'pytest',
            'tests/tier0/',
            '--tb=short',
            '-v' if verbose else '-q',
            '--disable-warnings'
        ]
        
        # Run pytest
        proc_result = subprocess.run(
            pytest_args,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # Capture output
        output = proc_result.stdout + proc_result.stderr
        result['output'] = output
        
        # Parse results from pytest summary line
        # Format: "===== X passed, Y failed, Z skipped, A xfailed, B xpassed in Xs ====="
        import re
        summary_pattern = r'=+\s*(\d+)\s+passed(?:,\s*(\d+)\s+failed)?'
        match = re.search(summary_pattern, output)
        
        if match:
            passed_count = int(match.group(1))
            failed_count = int(match.group(2)) if match.group(2) else 0
            total_count = passed_count + failed_count
        else:
            # Fallback: count individual test results (works with -v but not -q)
            passed_count = output.count(' PASSED')
            failed_count = output.count(' FAILED')
            total_count = passed_count + failed_count
        
        result['tests_run'] = total_count
        result['tests_passed'] = passed_count
        result['tests_failed'] = failed_count
        result['success'] = (failed_count == 0 and total_count > 0)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        result['duration_seconds'] = duration
        
        # Log results
        logger.info("")
        logger.info("SKULL TEST RESULTS:")
        logger.info(f"  Total:  {total_count}")
        logger.info(f"  Passed: {passed_count}")
        logger.info(f"  Failed: {failed_count}")
        logger.info(f"  Duration: {duration:.2f}s")
        
        if result['success']:
            logger.info("=" * 80)
            logger.info("✅ ALL SKULL TESTS PASSED - Brain protection intact")
            logger.info("=" * 80)
        else:
            logger.error("=" * 80)
            logger.error("❌ SKULL TESTS FAILED - Brain protection compromised!")
            logger.error("=" * 80)
            logger.error(f"Failed tests: {failed_count}/{total_count}")
            
            # Extract failure details
            if 'FAILED' in output:
                logger.error("\nFailure details:")
                for line in output.split('\n'):
                    if 'FAILED' in line or 'ERROR' in line or 'AssertionError' in line:
                        logger.error(f"  {line}")
        
        return result
        
    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start_time).total_seconds()
        result['duration_seconds'] = duration
        result['error'] = f'Test execution timeout after {timeout}s'
        
        logger.error("=" * 80)
        logger.error(f"❌ SKULL TESTS TIMEOUT after {timeout}s")
        logger.error("=" * 80)
        
        return result
        
    except FileNotFoundError:
        result['error'] = 'pytest not found - ensure pytest is installed'
        logger.error("=" * 80)
        logger.error("❌ pytest not found in environment")
        logger.error("=" * 80)
        logger.error("Install pytest: pip install pytest")
        
        return result
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        result['duration_seconds'] = duration
        result['error'] = str(e)
        
        logger.error("=" * 80)
        logger.error(f"❌ SKULL TEST EXECUTION ERROR: {e}")
        logger.error("=" * 80)
        
        return result


def format_skull_test_summary(result: Dict[str, Any]) -> str:
    """
    Format SKULL test results for display.
    
    Args:
        result: Result dict from run_skull_tests()
        
    Returns:
        Formatted string summary
    """
    if result.get('error'):
        return f"❌ SKULL Tests Error: {result['error']}"
    
    if result['success']:
        return (
            f"✅ SKULL Tests: {result['tests_passed']}/{result['tests_run']} passed "
            f"({result['duration_seconds']:.1f}s)"
        )
    else:
        return (
            f"❌ SKULL Tests: {result['tests_failed']}/{result['tests_run']} FAILED "
            f"({result['duration_seconds']:.1f}s)"
        )
