"""
Test Execution Manager for TDD Mastery

Purpose: Programmatic test execution with framework detection
Author: Asif Hussain
Created: 2025-11-24
Version: 1.0

Provides:
- Automatic framework detection (pytest/jest/xunit/unittest)
- Test discovery and execution
- JSON output parsing
- Structured result returns
- Exit code handling
"""

import subprocess
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, Optional, List
import re


class TestExecutionManager:
    """
    Programmatic test execution and result capture.
    
    Supports multiple test frameworks:
    - pytest (Python) with JSON report
    - unittest (Python) with custom runner
    - jest (JavaScript/TypeScript) with JSON output
    - xunit (C#/.NET) with TRX parsing
    
    Example:
        manager = TestExecutionManager("/path/to/project")
        
        # Auto-detect framework and run tests
        results = manager.run_tests()
        
        # Run specific test file
        results = manager.run_tests("tests/test_login.py")
        
        # Results structure
        {
            'framework': 'pytest',
            'passed': 5,
            'failed': 2,
            'skipped': 1,
            'errors': [...],
            'duration': 2.5,
            'exit_code': 1
        }
    """
    
    def __init__(self, workspace_root: str):
        """
        Initialize test execution manager.
        
        Args:
            workspace_root: Absolute path to project root
        """
        self.workspace_root = Path(workspace_root)
        self.framework = self._detect_framework()
    
    def _detect_framework(self) -> str:
        """
        Auto-detect test framework from project structure.
        
        Returns:
            Framework name: 'pytest'|'jest'|'xunit'|'unittest'
        """
        # Check for pytest
        pytest_indicators = [
            self.workspace_root / "pytest.ini",
            self.workspace_root / "pyproject.toml",
            self.workspace_root / "setup.cfg"
        ]
        for indicator in pytest_indicators:
            if indicator.exists():
                # Additional check for [tool.pytest] in pyproject.toml
                if indicator.name == "pyproject.toml":
                    content = indicator.read_text()
                    if "[tool.pytest" in content:
                        return "pytest"
                else:
                    return "pytest"
        
        # Check for Jest
        jest_indicators = [
            self.workspace_root / "jest.config.js",
            self.workspace_root / "jest.config.ts",
            self.workspace_root / "jest.config.json"
        ]
        for indicator in jest_indicators:
            if indicator.exists():
                return "jest"
        
        # Check package.json for jest
        package_json = self.workspace_root / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                if "jest" in data.get("devDependencies", {}) or "jest" in data.get("dependencies", {}):
                    return "jest"
            except:
                pass
        
        # Check for xUnit (.NET)
        csproj_files = list(self.workspace_root.glob("**/*.csproj"))
        for csproj in csproj_files:
            content = csproj.read_text()
            if "xunit" in content.lower():
                return "xunit"
        
        # Check for unittest (Python fallback)
        test_dirs = ["tests", "test", "__tests__"]
        for test_dir in test_dirs:
            test_path = self.workspace_root / test_dir
            if test_path.exists():
                for test_file in test_path.glob("test_*.py"):
                    content = test_file.read_text()
                    if "import unittest" in content:
                        return "unittest"
        
        # Default to pytest (most common Python framework)
        return "pytest"
    
    def run_tests(self, test_file: Optional[str] = None, verbose: bool = True) -> Dict[str, Any]:
        """
        Execute tests programmatically.
        
        Args:
            test_file: Specific test file to run (None = run all)
            verbose: Show detailed output
            
        Returns:
            Structured test results
            {
                'framework': 'pytest',
                'passed': 5,
                'failed': 2,
                'skipped': 1,
                'errors': [
                    {
                        'test': 'tests/test_login.py::test_invalid',
                        'message': 'AssertionError: ...'
                    }
                ],
                'duration': 2.5,
                'exit_code': 1,
                'raw_output': '...'
            }
        """
        if self.framework == "pytest":
            return self._run_pytest(test_file, verbose)
        elif self.framework == "jest":
            return self._run_jest(test_file, verbose)
        elif self.framework == "xunit":
            return self._run_xunit(test_file, verbose)
        elif self.framework == "unittest":
            return self._run_unittest(test_file, verbose)
        else:
            return {
                'error': f'Unsupported framework: {self.framework}',
                'framework': self.framework,
                'exit_code': -1
            }
    
    def _run_pytest(self, test_file: Optional[str], verbose: bool) -> Dict[str, Any]:
        """
        Run pytest with JSON report.
        
        Uses pytest-json-report plugin for structured output.
        If not available, falls back to pytest-json or manual parsing.
        """
        # Build command
        cmd = ["pytest"]
        
        # Add JSON report options
        json_report_file = self.workspace_root / ".pytest_report.json"
        cmd.extend([
            "--json-report",
            f"--json-report-file={json_report_file}",
            "--json-report-omit=log"  # Reduce output size
        ])
        
        if verbose:
            cmd.append("-v")
        
        if test_file:
            cmd.append(test_file)
        
        # Execute pytest
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse JSON report
            if json_report_file.exists():
                try:
                    with open(json_report_file) as f:
                        data = json.load(f)
                    
                    # Extract summary
                    summary = data.get("summary", {})
                    
                    # Extract failed tests
                    errors = []
                    for test in data.get("tests", []):
                        if test.get("outcome") == "failed":
                            errors.append({
                                'test': test.get("nodeid", "Unknown"),
                                'message': self._extract_pytest_error(test)
                            })
                    
                    return {
                        'framework': 'pytest',
                        'passed': summary.get("passed", 0),
                        'failed': summary.get("failed", 0),
                        'skipped': summary.get("skipped", 0),
                        'errors': errors,
                        'duration': summary.get("duration", 0.0),
                        'exit_code': result.returncode,
                        'raw_output': result.stdout
                    }
                finally:
                    # Clean up JSON file
                    json_report_file.unlink(missing_ok=True)
            
            # Fallback: Parse terminal output
            return self._parse_pytest_terminal_output(result.stdout, result.returncode)
        
        except subprocess.TimeoutExpired:
            return {
                'error': 'Test execution timeout (5 minutes)',
                'framework': 'pytest',
                'exit_code': -1
            }
        except FileNotFoundError:
            return {
                'error': 'pytest not found. Install with: pip install pytest pytest-json-report',
                'framework': 'pytest',
                'exit_code': -1
            }
        except Exception as e:
            return {
                'error': f'Test execution failed: {str(e)}',
                'framework': 'pytest',
                'exit_code': -1
            }
    
    def _run_jest(self, test_file: Optional[str], verbose: bool) -> Dict[str, Any]:
        """
        Run Jest with JSON output.
        
        Jest has built-in JSON reporter.
        """
        # Build command
        cmd = ["npm", "test", "--", "--json"]
        
        if verbose:
            cmd.append("--verbose")
        
        if test_file:
            cmd.append(test_file)
        
        # Execute Jest
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse JSON output
            try:
                data = json.loads(result.stdout)
                
                # Extract summary
                summary = data.get("numPassedTests", 0), data.get("numFailedTests", 0)
                
                # Extract failed tests
                errors = []
                for test_result in data.get("testResults", []):
                    for assertion in test_result.get("assertionResults", []):
                        if assertion.get("status") == "failed":
                            errors.append({
                                'test': f"{test_result.get('name', 'Unknown')}::{assertion.get('title', 'Unknown')}",
                                'message': "\n".join(assertion.get("failureMessages", []))
                            })
                
                return {
                    'framework': 'jest',
                    'passed': data.get("numPassedTests", 0),
                    'failed': data.get("numFailedTests", 0),
                    'skipped': data.get("numPendingTests", 0),
                    'errors': errors,
                    'duration': data.get("duration", 0) / 1000.0,  # Convert ms to seconds
                    'exit_code': result.returncode,
                    'raw_output': result.stdout
                }
            except json.JSONDecodeError:
                # Fallback: Parse terminal output
                return self._parse_jest_terminal_output(result.stdout, result.returncode)
        
        except subprocess.TimeoutExpired:
            return {
                'error': 'Test execution timeout (5 minutes)',
                'framework': 'jest',
                'exit_code': -1
            }
        except FileNotFoundError:
            return {
                'error': 'npm/jest not found. Install with: npm install --save-dev jest',
                'framework': 'jest',
                'exit_code': -1
            }
        except Exception as e:
            return {
                'error': f'Test execution failed: {str(e)}',
                'framework': 'jest',
                'exit_code': -1
            }
    
    def _run_xunit(self, test_file: Optional[str], verbose: bool) -> Dict[str, Any]:
        """
        Run xUnit tests with dotnet test.
        
        Uses TRX logger for structured output.
        """
        # Build command
        trx_file = self.workspace_root / "TestResults" / "test_results.trx"
        cmd = [
            "dotnet", "test",
            f"--logger:trx;LogFileName={trx_file.name}"
        ]
        
        if verbose:
            cmd.append("--verbosity=normal")
        
        if test_file:
            cmd.append(test_file)
        
        # Execute dotnet test
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse TRX file
            if trx_file.exists():
                try:
                    tree = ET.parse(trx_file)
                    root = tree.getroot()
                    
                    # Extract namespace
                    ns = {'ns': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
                    
                    # Find summary
                    summary = root.find('.//ns:ResultSummary/ns:Counters', ns)
                    passed = int(summary.get('passed', 0)) if summary is not None else 0
                    failed = int(summary.get('failed', 0)) if summary is not None else 0
                    
                    # Extract failed tests
                    errors = []
                    for test_result in root.findall('.//ns:UnitTestResult', ns):
                        if test_result.get('outcome') == 'Failed':
                            test_name = test_result.get('testName', 'Unknown')
                            message_elem = test_result.find('.//ns:Message', ns)
                            message = message_elem.text if message_elem is not None else "No error message"
                            
                            errors.append({
                                'test': test_name,
                                'message': message
                            })
                    
                    return {
                        'framework': 'xunit',
                        'passed': passed,
                        'failed': failed,
                        'skipped': int(summary.get('notExecuted', 0)) if summary else 0,
                        'errors': errors,
                        'duration': float(summary.get('duration', 0)) if summary else 0.0,
                        'exit_code': result.returncode,
                        'raw_output': result.stdout
                    }
                finally:
                    # Clean up TRX file
                    trx_file.unlink(missing_ok=True)
            
            # Fallback: Parse terminal output
            return self._parse_xunit_terminal_output(result.stdout, result.returncode)
        
        except subprocess.TimeoutExpired:
            return {
                'error': 'Test execution timeout (5 minutes)',
                'framework': 'xunit',
                'exit_code': -1
            }
        except FileNotFoundError:
            return {
                'error': 'dotnet not found. Install .NET SDK',
                'framework': 'xunit',
                'exit_code': -1
            }
        except Exception as e:
            return {
                'error': f'Test execution failed: {str(e)}',
                'framework': 'xunit',
                'exit_code': -1
            }
    
    def _run_unittest(self, test_file: Optional[str], verbose: bool) -> Dict[str, Any]:
        """
        Run Python unittest with custom JSON output.
        
        Uses unittest's TextTestRunner with custom result collector.
        """
        # Build command
        cmd = ["python", "-m", "unittest"]
        
        if verbose:
            cmd.append("-v")
        
        if test_file:
            # Convert file path to module notation
            module = test_file.replace("/", ".").replace("\\", ".").replace(".py", "")
            cmd.append(module)
        else:
            cmd.append("discover")
        
        # Execute unittest
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Parse terminal output
            return self._parse_unittest_terminal_output(result.stdout, result.returncode)
        
        except subprocess.TimeoutExpired:
            return {
                'error': 'Test execution timeout (5 minutes)',
                'framework': 'unittest',
                'exit_code': -1
            }
        except Exception as e:
            return {
                'error': f'Test execution failed: {str(e)}',
                'framework': 'unittest',
                'exit_code': -1
            }
    
    def _extract_pytest_error(self, test: Dict[str, Any]) -> str:
        """Extract error message from pytest JSON test result."""
        call = test.get("call", {})
        longrepr = call.get("longrepr", "")
        if longrepr:
            # Truncate long error messages
            return longrepr[:500] + "..." if len(longrepr) > 500 else longrepr
        return "No error message available"
    
    def _parse_pytest_terminal_output(self, output: str, exit_code: int) -> Dict[str, Any]:
        """Fallback parser for pytest terminal output."""
        result = {
            'framework': 'pytest',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'duration': 0.0,
            'exit_code': exit_code,
            'raw_output': output
        }
        
        # Extract summary line
        summary_pattern = r'(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?.*in\s+([\d.]+)s'
        match = re.search(summary_pattern, output)
        if match:
            result['passed'] = int(match.group(1))
            result['failed'] = int(match.group(2)) if match.group(2) else 0
            result['skipped'] = int(match.group(3)) if match.group(3) else 0
            result['duration'] = float(match.group(4))
        
        return result
    
    def _parse_jest_terminal_output(self, output: str, exit_code: int) -> Dict[str, Any]:
        """Fallback parser for Jest terminal output."""
        result = {
            'framework': 'jest',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'duration': 0.0,
            'exit_code': exit_code,
            'raw_output': output
        }
        
        # Extract summary
        passed_match = re.search(r'(\d+)\s+passed', output)
        failed_match = re.search(r'(\d+)\s+failed', output)
        
        if passed_match:
            result['passed'] = int(passed_match.group(1))
        if failed_match:
            result['failed'] = int(failed_match.group(1))
        
        return result
    
    def _parse_xunit_terminal_output(self, output: str, exit_code: int) -> Dict[str, Any]:
        """Fallback parser for xUnit terminal output."""
        result = {
            'framework': 'xunit',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'duration': 0.0,
            'exit_code': exit_code,
            'raw_output': output
        }
        
        # Extract summary
        summary_pattern = r'Failed:\s+(\d+),\s+Passed:\s+(\d+),\s+Skipped:\s+(\d+)'
        match = re.search(summary_pattern, output)
        if match:
            result['failed'] = int(match.group(1))
            result['passed'] = int(match.group(2))
            result['skipped'] = int(match.group(3))
        
        return result
    
    def _parse_unittest_terminal_output(self, output: str, exit_code: int) -> Dict[str, Any]:
        """Parser for unittest terminal output."""
        result = {
            'framework': 'unittest',
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': [],
            'duration': 0.0,
            'exit_code': exit_code,
            'raw_output': output
        }
        
        # Extract summary
        ran_match = re.search(r'Ran\s+(\d+)\s+test', output)
        if ran_match:
            total = int(ran_match.group(1))
            
            # Check for failures
            failed_match = re.search(r'FAILED\s+\(failures=(\d+)\)', output)
            if failed_match:
                result['failed'] = int(failed_match.group(1))
                result['passed'] = total - result['failed']
            else:
                result['passed'] = total
        
        return result
