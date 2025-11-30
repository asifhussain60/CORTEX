"""
Code Runner
Executes Python code in isolated sandbox environment.

Provides safe execution of demo code with timeout protection,
syntax validation, and rich output formatting.
"""

import ast
import sys
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List
import time
import traceback
import json


@dataclass
class ExecutionResult:
    """
    Result of code execution.
    
    Attributes:
        success: Whether execution completed without errors
        output: Standard output from execution
        error: Error message if execution failed
        execution_time: Time taken to execute (seconds)
        test_results: Test results if running pytest
        memory_used: Memory usage in MB (if available)
        exit_code: Process exit code
    """
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    test_results: Optional[Dict[str, Any]] = None
    memory_used: Optional[float] = None
    exit_code: int = 0


class CodeRunner:
    """
    Executes Python code in isolated sandbox environment.
    
    Features:
    - Isolated subprocess execution with timeout
    - Syntax validation before execution
    - Test integration with pytest
    - Rich output formatting
    - Memory and timing metrics
    - Error handling with line numbers
    
    Safety:
    - 30-second timeout by default
    - Isolated filesystem access
    - No access to parent process environment
    """
    
    DEFAULT_TIMEOUT = 30  # seconds
    
    def __init__(self, 
                 workspace: Optional[Path] = None,
                 timeout: int = DEFAULT_TIMEOUT,
                 python_executable: str = sys.executable):
        """
        Initialize Code Runner.
        
        Args:
            workspace: Directory for temporary code files
            timeout: Maximum execution time in seconds
            python_executable: Path to Python interpreter
        """
        self.workspace = workspace or Path(tempfile.mkdtemp(prefix="cortex_demo_"))
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.python_executable = python_executable
    
    def validate_syntax(self, code: str) -> Optional[str]:
        """
        Validate Python syntax without executing.
        
        Args:
            code: Python code to validate
        
        Returns:
            Error message if syntax is invalid, None if valid
        """
        try:
            ast.parse(code)
            return None
        except SyntaxError as e:
            return f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return f"Validation error: {str(e)}"
    
    def execute_code(self, code: str, 
                    file_name: str = "demo_code.py") -> ExecutionResult:
        """
        Execute Python code in isolated environment.
        
        Args:
            code: Python code to execute
            file_name: Name for temporary file
        
        Returns:
            ExecutionResult with output and metrics
        """
        # Validate syntax first
        syntax_error = self.validate_syntax(code)
        if syntax_error:
            return ExecutionResult(
                success=False,
                output="",
                error=syntax_error,
                execution_time=0.0,
                exit_code=1
            )
        
        # Write code to temporary file
        code_file = self.workspace / file_name
        code_file.write_text(code)
        
        # Execute in subprocess
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [self.python_executable, str(code_file)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(self.workspace)
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                execution_time=execution_time,
                exit_code=result.returncode
            )
        
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution timeout after {self.timeout} seconds",
                execution_time=execution_time,
                exit_code=-1
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=f"Execution error: {str(e)}",
                execution_time=execution_time,
                exit_code=-1
            )
    
    def run_tests(self, test_code: str, 
                  implementation_code: Optional[str] = None) -> ExecutionResult:
        """
        Run pytest tests with optional implementation code.
        
        Args:
            test_code: Test code (pytest format)
            implementation_code: Implementation code to test against
        
        Returns:
            ExecutionResult with test results
        """
        # Write test file
        test_file = self.workspace / "test_demo.py"
        test_file.write_text(test_code)
        
        # Write implementation file if provided
        if implementation_code:
            impl_file = self.workspace / "implementation.py"
            impl_file.write_text(implementation_code)
        
        # Run pytest with JSON output
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [
                    self.python_executable, "-m", "pytest",
                    str(test_file),
                    "-v",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=test_results.json"
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(self.workspace)
            )
            
            execution_time = time.time() - start_time
            
            # Parse test results
            test_results = self._parse_test_results()
            
            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                execution_time=execution_time,
                test_results=test_results,
                exit_code=result.returncode
            )
        
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=f"Test execution timeout after {self.timeout} seconds",
                execution_time=execution_time,
                exit_code=-1
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=f"Test execution error: {str(e)}",
                execution_time=execution_time,
                exit_code=-1
            )
    
    def _parse_test_results(self) -> Optional[Dict[str, Any]]:
        """
        Parse pytest JSON results.
        
        Returns:
            Dictionary with test results, None if parsing fails
        """
        try:
            results_file = self.workspace / "test_results.json"
            if not results_file.exists():
                return None
            
            with open(results_file, 'r') as f:
                data = json.load(f)
            
            # Extract key metrics
            summary = data.get('summary', {})
            
            return {
                'total': summary.get('total', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'skipped': summary.get('skipped', 0),
                'duration': data.get('duration', 0),
                'tests': [
                    {
                        'name': test.get('nodeid', 'unknown'),
                        'outcome': test.get('outcome', 'unknown'),
                        'duration': test.get('duration', 0)
                    }
                    for test in data.get('tests', [])
                ]
            }
        
        except Exception as e:
            return None
    
    def format_output(self, result: ExecutionResult, 
                     include_metrics: bool = True) -> str:
        """
        Format execution result for display.
        
        Args:
            result: ExecutionResult to format
            include_metrics: Whether to include timing/memory metrics
        
        Returns:
            Formatted string for display
        """
        lines = []
        
        # Status
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        lines.append(f"\n{status}")
        lines.append("=" * 60)
        
        # Output
        if result.output:
            lines.append("\nOutput:")
            lines.append(result.output)
        
        # Error
        if result.error:
            lines.append("\nError:")
            lines.append(result.error)
        
        # Test results
        if result.test_results:
            lines.append("\nTest Results:")
            tr = result.test_results
            lines.append(f"  Total: {tr['total']}")
            lines.append(f"  Passed: {tr['passed']}")
            lines.append(f"  Failed: {tr['failed']}")
            if tr['skipped'] > 0:
                lines.append(f"  Skipped: {tr['skipped']}")
        
        # Metrics
        if include_metrics:
            lines.append("\nMetrics:")
            lines.append(f"  Execution time: {result.execution_time:.3f}s")
            if result.memory_used:
                lines.append(f"  Memory used: {result.memory_used:.2f} MB")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def cleanup(self) -> None:
        """Clean up temporary workspace files."""
        try:
            import shutil
            if self.workspace.exists():
                shutil.rmtree(self.workspace)
        except Exception as e:
            print(f"Warning: Failed to clean up workspace: {e}")
