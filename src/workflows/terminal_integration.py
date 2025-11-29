"""
Terminal Integration for TDD Mastery

Purpose: Bridge TDD workflow with GitHub Copilot terminal tools
Author: Asif Hussain
Created: 2025-11-24
Version: 1.0

Integrates with:
- #terminal_last_command: Detect test execution
- #get_terminal_output: Capture test results
- Automatic test output parsing
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path


class TerminalIntegration:
    """
    Terminal integration for TDD Mastery workflow.
    
    Provides automatic detection of test execution and result capture
    using GitHub Copilot terminal tools.
    
    Example:
        terminal = TerminalIntegration()
        
        # Auto-detect test execution
        test_execution = terminal.detect_test_execution()
        
        if test_execution:
            # Capture results
            results = terminal.capture_test_results()
            print(f"Tests: {results['passed']} passed, {results['failed']} failed")
    """
    
    # Test command patterns
    TEST_COMMAND_PATTERNS = {
        'pytest': [
            r'^pytest\b',
            r'^python\s+-m\s+pytest\b',
            r'^py\.test\b'
        ],
        'jest': [
            r'^jest\b',
            r'^npm\s+test\b',
            r'^npm\s+run\s+test\b',
            r'^yarn\s+test\b'
        ],
        'xunit': [
            r'^dotnet\s+test\b',
            r'^vstest\.console\b'
        ],
        'unittest': [
            r'^python\s+-m\s+unittest\b'
        ]
    }
    
    def __init__(self, cache_duration_seconds: int = 60):
        """
        Initialize terminal integration.
        
        Args:
            cache_duration_seconds: How long to cache terminal data
        """
        self.cache_duration = cache_duration_seconds
        self.last_command_cache: Optional[Dict[str, Any]] = None
        self.output_cache: Optional[str] = None
        self.cache_timestamp: Optional[datetime] = None
    
    def detect_test_execution(self) -> Optional[Dict[str, Any]]:
        """
        Detect if user just ran tests in terminal.
        
        This method should be called by GitHub Copilot which has access to
        terminal_last_command tool. In standalone usage, it returns None.
        
        Returns:
            Dictionary with command details if test-related, None otherwise
            {
                'framework': 'pytest'|'jest'|'xunit'|'unittest',
                'command': 'pytest tests/test_login.py -v',
                'working_directory': '/path/to/project',
                'exit_code': 0|1,
                'timestamp': datetime
            }
        """
        # NOTE: This is a placeholder that will be called by GitHub Copilot
        # Copilot will inject the actual terminal_last_command data
        
        # Check if cache is still valid
        if self._is_cache_valid():
            return self.last_command_cache
        
        # In standalone mode, return None (requires Copilot integration)
        return None
    
    def parse_terminal_command(self, command: str, exit_code: int, 
                               working_directory: str) -> Optional[Dict[str, Any]]:
        """
        Parse terminal command to detect test execution.
        
        This method is called by GitHub Copilot with terminal_last_command data.
        
        Args:
            command: The command executed in terminal
            exit_code: Exit code of the command
            working_directory: Directory where command was executed
            
        Returns:
            Parsed command details if test-related, None otherwise
        """
        # Detect test framework
        framework = self._detect_framework(command)
        
        if not framework:
            return None
        
        # Cache the result
        self.last_command_cache = {
            'framework': framework,
            'command': command,
            'working_directory': working_directory,
            'exit_code': exit_code,
            'timestamp': datetime.now()
        }
        self.cache_timestamp = datetime.now()
        
        return self.last_command_cache
    
    def capture_test_results(self, terminal_output: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture test execution results from terminal.
        
        This method should be called by GitHub Copilot which has access to
        get_terminal_output tool.
        
        Args:
            terminal_output: Raw terminal output (provided by Copilot)
            
        Returns:
            Structured test results
            {
                'framework': 'pytest',
                'passed': 5,
                'failed': 2,
                'skipped': 1,
                'errors': [
                    {
                        'test': 'tests/test_login.py::test_invalid_password',
                        'message': 'AssertionError: Expected False, got True'
                    }
                ],
                'exit_code': 1,
                'raw_output': '...',
                'duration': 2.5
            }
        """
        # Get cached command info
        if not self.last_command_cache:
            return {
                'error': 'No recent test execution detected',
                'suggestion': 'Run tests in terminal first (pytest/npm test/dotnet test)'
            }
        
        framework = self.last_command_cache['framework']
        
        # Use provided output or cached output
        if terminal_output:
            self.output_cache = terminal_output
        elif not self.output_cache:
            return {
                'error': 'No terminal output available',
                'suggestion': 'Terminal output could not be captured'
            }
        
        # Parse output based on framework
        if framework == 'pytest':
            return self._parse_pytest_output(self.output_cache)
        elif framework == 'jest':
            return self._parse_jest_output(self.output_cache)
        elif framework == 'xunit':
            return self._parse_xunit_output(self.output_cache)
        elif framework == 'unittest':
            return self._parse_unittest_output(self.output_cache)
        
        return {'error': f'Unsupported framework: {framework}'}
    
    def _detect_framework(self, command: str) -> Optional[str]:
        """Detect test framework from command."""
        for framework, patterns in self.TEST_COMMAND_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return framework
        return None
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        if not self.cache_timestamp or not self.last_command_cache:
            return False
        
        elapsed = (datetime.now() - self.cache_timestamp).total_seconds()
        return elapsed < self.cache_duration
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """
        Parse pytest terminal output.
        
        Example pytest output:
        ============================= test session starts ==============================
        collected 8 items
        
        tests/test_login.py::test_valid_login PASSED                             [ 12%]
        tests/test_login.py::test_invalid_password FAILED                        [ 25%]
        ...
        =========================== short test summary info ============================
        FAILED tests/test_login.py::test_invalid_password - AssertionError: ...
        ========================= 5 passed, 2 failed, 1 skipped in 2.50s ===============
        """
        result = {
            'framework': 'pytest',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'exit_code': self.last_command_cache.get('exit_code', 1),
            'raw_output': output,
            'duration': 0.0
        }
        
        # Extract summary line (e.g., "5 passed, 2 failed, 1 skipped in 2.50s")
        summary_pattern = r'(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?.*in\s+([\d.]+)s'
        summary_match = re.search(summary_pattern, output)
        
        if summary_match:
            result['passed'] = int(summary_match.group(1))
            result['failed'] = int(summary_match.group(2)) if summary_match.group(2) else 0
            result['skipped'] = int(summary_match.group(3)) if summary_match.group(3) else 0
            result['duration'] = float(summary_match.group(4))
        
        # Extract failed test details
        failed_pattern = r'FAILED\s+([\w\./]+::\w+)\s+-\s+(.+?)(?=\nFAILED|\n=|$)'
        for match in re.finditer(failed_pattern, output, re.DOTALL):
            result['errors'].append({
                'test': match.group(1),
                'message': match.group(2).strip()
            })
        
        return result
    
    def _parse_jest_output(self, output: str) -> Dict[str, Any]:
        """
        Parse Jest terminal output.
        
        Example Jest output:
        PASS  tests/login.test.js
          ✓ valid login (50ms)
          ✕ invalid password (25ms)
        
        Test Suites: 1 passed, 1 total
        Tests:       5 passed, 2 failed, 7 total
        Time:        2.5s
        """
        result = {
            'framework': 'jest',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'exit_code': self.last_command_cache.get('exit_code', 1),
            'raw_output': output,
            'duration': 0.0
        }
        
        # Extract summary
        summary_pattern = r'Tests:\s+(\d+)\s+passed(?:,\s+(\d+)\s+failed)?.*?Time:\s+([\d.]+)s'
        summary_match = re.search(summary_pattern, output)
        
        if summary_match:
            result['passed'] = int(summary_match.group(1))
            result['failed'] = int(summary_match.group(2)) if summary_match.group(2) else 0
            result['duration'] = float(summary_match.group(3))
        
        # Extract failed test details
        failed_pattern = r'✕\s+(.+?)\s+\((\d+)ms\)'
        for match in re.finditer(failed_pattern, output):
            result['errors'].append({
                'test': match.group(1),
                'message': f'Test failed ({match.group(2)}ms)'
            })
        
        return result
    
    def _parse_xunit_output(self, output: str) -> Dict[str, Any]:
        """
        Parse xUnit/dotnet test terminal output.
        
        Example dotnet test output:
        Passed!  - Failed:     2, Passed:     5, Skipped:     1, Total:     8, Duration: 2.5 s
        """
        result = {
            'framework': 'xunit',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'exit_code': self.last_command_cache.get('exit_code', 1),
            'raw_output': output,
            'duration': 0.0
        }
        
        # Extract summary
        summary_pattern = r'Failed:\s+(\d+),\s+Passed:\s+(\d+),\s+Skipped:\s+(\d+).*Duration:\s+([\d.]+)\s+s'
        summary_match = re.search(summary_pattern, output)
        
        if summary_match:
            result['failed'] = int(summary_match.group(1))
            result['passed'] = int(summary_match.group(2))
            result['skipped'] = int(summary_match.group(3))
            result['duration'] = float(summary_match.group(4))
        
        # Extract failed test details (xUnit format)
        failed_pattern = r'\[FAIL\]\s+(.+?)\r?\n\s+(.+?)(?=\[|$)'
        for match in re.finditer(failed_pattern, output, re.DOTALL):
            result['errors'].append({
                'test': match.group(1).strip(),
                'message': match.group(2).strip()
            })
        
        return result
    
    def _parse_unittest_output(self, output: str) -> Dict[str, Any]:
        """
        Parse Python unittest terminal output.
        
        Example unittest output:
        ......F.F
        ======================================================================
        FAIL: test_invalid_password (test_login.TestLogin)
        ----------------------------------------------------------------------
        AssertionError: Expected False, got True
        
        Ran 8 tests in 2.500s
        FAILED (failures=2)
        """
        result = {
            'framework': 'unittest',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'exit_code': self.last_command_cache.get('exit_code', 1),
            'raw_output': output,
            'duration': 0.0
        }
        
        # Extract summary
        summary_pattern = r'Ran\s+(\d+)\s+tests?\s+in\s+([\d.]+)s'
        summary_match = re.search(summary_pattern, output)
        
        if summary_match:
            total_tests = int(summary_match.group(1))
            result['duration'] = float(summary_match.group(2))
            
            # Extract failures
            failures_pattern = r'FAILED\s+\(failures=(\d+)\)'
            failures_match = re.search(failures_pattern, output)
            
            if failures_match:
                result['failed'] = int(failures_match.group(1))
                result['passed'] = total_tests - result['failed']
            else:
                result['passed'] = total_tests
        
        # Extract failed test details
        failed_pattern = r'FAIL:\s+(\w+)\s+\((.+?)\)\r?\n-+\r?\n(.+?)(?=\n={70}|$)'
        for match in re.finditer(failed_pattern, output, re.DOTALL):
            result['errors'].append({
                'test': f"{match.group(2)}.{match.group(1)}",
                'message': match.group(3).strip()
            })
        
        return result
    
    def format_test_summary(self, results: Dict[str, Any]) -> str:
        """
        Format test results for display.
        
        Args:
            results: Test results dictionary
            
        Returns:
            Formatted summary string
        """
        if 'error' in results:
            return f"❌ {results['error']}\n💡 {results.get('suggestion', '')}"
        
        framework = results['framework']
        passed = results['passed']
        failed = results['failed']
        skipped = results.get('skipped', 0)
        duration = results['duration']
        
        # Overall status
        status = "✅ PASSED" if failed == 0 else "❌ FAILED"
        
        summary = f"{status} - {framework.upper()} Results\n"
        summary += f"  Passed:  {passed} ✓\n"
        summary += f"  Failed:  {failed} ✗\n"
        
        if skipped > 0:
            summary += f"  Skipped: {skipped} ⊘\n"
        
        summary += f"  Duration: {duration:.2f}s\n"
        
        # Show failed tests
        if failed > 0 and results.get('errors'):
            summary += "\nFailed Tests:\n"
            for error in results['errors'][:5]:  # Show first 5
                summary += f"  • {error['test']}\n"
                summary += f"    {error['message'][:100]}...\n"
        
        return summary


# GitHub Copilot Integration Functions
# These are called by Copilot with tool data

def on_terminal_command_executed(command: str, exit_code: int, 
                                  working_directory: str) -> Optional[Dict[str, Any]]:
    """
    Called by GitHub Copilot when terminal_last_command is available.
    
    Args:
        command: The command executed
        exit_code: Exit code of command
        working_directory: Directory where command ran
        
    Returns:
        Parsed command details if test-related
    """
    terminal = TerminalIntegration()
    return terminal.parse_terminal_command(command, exit_code, working_directory)


def on_terminal_output_available(output: str) -> Dict[str, Any]:
    """
    Called by GitHub Copilot when get_terminal_output is available.
    
    Args:
        output: Raw terminal output
        
    Returns:
        Parsed test results
    """
    terminal = TerminalIntegration()
    return terminal.capture_test_results(output)
