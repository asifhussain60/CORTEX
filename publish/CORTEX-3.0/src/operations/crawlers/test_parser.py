"""
Test Parser Crawler

Analyzes test coverage and quality metrics.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, List
import re

from .base_crawler import BaseCrawler


class TestParserCrawler(BaseCrawler):
    """
    Analyzes test suite to extract:
    - Total tests (unit, integration, e2e)
    - Test pass/fail rates
    - Coverage percentage
    - Untested modules
    """
    
    def get_name(self) -> str:
        return "Test Parser"
    
    def crawl(self) -> Dict[str, Any]:
        """
        Analyze test suite and coverage.
        
        Returns:
            Dict containing test analysis
        """
        self.log_info("Starting test analysis")
        
        test_data = {
            'pytest_available': False,
            'total_tests': 0,
            'passing': 0,
            'failing': 0,
            'skipped': 0,
            'coverage': 0.0,
            'test_files': 0,
            'untested_modules': [],
            'test_types': {
                'unit': 0,
                'integration': 0,
                'e2e': 0
            }
        }
        
        # Check if pytest is available
        if not self._is_pytest_available():
            self.log_warning("pytest not available")
            return {"success": True, "data": test_data}
        
        test_data['pytest_available'] = True
        
        # Collect tests (don't run them, just collect)
        try:
            test_collection = self._collect_tests()
            test_data.update(test_collection)
            
            # Count test files
            test_data['test_files'] = self._count_test_files()
            
            # Try to get coverage info if available
            coverage_info = self._get_coverage_info()
            if coverage_info:
                test_data.update(coverage_info)
            
            self.log_info(
                f"Test analysis complete: {test_data['total_tests']} tests found, "
                f"{test_data['test_files']} test files"
            )
            
        except Exception as e:
            self.log_error(f"Test analysis failed: {e}")
            return {"success": False, "data": test_data, "error": str(e)}
        
        return {
            "success": True,
            "data": test_data
        }
    
    def _is_pytest_available(self) -> bool:
        """Check if pytest is available."""
        try:
            subprocess.run(
                ['pytest', '--version'],
                capture_output=True,
                check=True,
                cwd=self.project_root
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _collect_tests(self) -> Dict[str, Any]:
        """
        Collect tests without running them.
        
        Returns:
            Dict with test collection statistics
        """
        try:
            # Use pytest --collect-only to gather test info
            result = subprocess.run(
                ['pytest', '--collect-only', '-q'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30
            )
            
            output = result.stdout
            
            # Parse output for test counts
            total_tests = 0
            test_types = {'unit': 0, 'integration': 0, 'e2e': 0}
            
            # Look for test count line (e.g., "123 tests collected")
            match = re.search(r'(\d+)\s+tests?\s+collected', output)
            if match:
                total_tests = int(match.group(1))
            
            # Categorize by test path
            for line in output.split('\n'):
                if '::test_' in line:
                    if 'unit' in line.lower():
                        test_types['unit'] += 1
                    elif 'integration' in line.lower() or 'integration' in line:
                        test_types['integration'] += 1
                    elif 'e2e' in line.lower() or 'end_to_end' in line:
                        test_types['e2e'] += 1
                    else:
                        # Default to unit tests
                        test_types['unit'] += 1
            
            # If we didn't categorize all tests, put remainder in unit
            categorized = sum(test_types.values())
            if categorized < total_tests:
                test_types['unit'] += (total_tests - categorized)
            
            return {
                'total_tests': total_tests,
                'test_types': test_types
            }
            
        except Exception as e:
            self.log_warning(f"Could not collect tests: {e}")
            return {'total_tests': 0, 'test_types': {'unit': 0, 'integration': 0, 'e2e': 0}}
    
    def _count_test_files(self) -> int:
        """Count test files in project."""
        tests_dir = Path(self.project_root) / 'tests'
        
        if not tests_dir.exists():
            return 0
        
        test_files = list(tests_dir.rglob('test_*.py'))
        return len(test_files)
    
    def _get_coverage_info(self) -> Dict[str, Any]:
        """
        Try to get coverage information from .coverage file or pytest-cov.
        
        Returns:
            Dict with coverage info, or None if not available
        """
        coverage_file = Path(self.project_root) / '.coverage'
        
        if not coverage_file.exists():
            self.log_info("No coverage data found")
            return None
        
        try:
            # Try to run coverage report
            result = subprocess.run(
                ['coverage', 'report', '--format=text'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=10
            )
            
            output = result.stdout
            
            # Parse total coverage percentage
            # Look for "TOTAL" line with percentage
            for line in output.split('\n'):
                if 'TOTAL' in line:
                    match = re.search(r'(\d+)%', line)
                    if match:
                        coverage_pct = float(match.group(1))
                        return {
                            'coverage': coverage_pct,
                            'coverage_available': True
                        }
            
        except Exception as e:
            self.log_warning(f"Could not get coverage info: {e}")
        
        return None
