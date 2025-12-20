"""
Test Coverage Collector - Analyzes test coverage and quality metrics.

Features:
- Coverage by layer (presentation, business, data access)
- Coverage by file/module
- Test type classification (unit, integration, E2E)
- pytest integration for Python
- Optional Playwright integration for E2E tests
- Test quality metrics (assertions per test, test size)
- Uncovered hotspots identification

Author: Asif Hussain
Date: December 2025
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict
import subprocess

logger = logging.getLogger(__name__)


class TestCoverageCollector:
    """
    Analyzes test coverage and test quality.
    
    Features:
    - Discovers test files (test_*.py, *_test.py, *.test.js, etc.)
    - Classifies test types (unit/integration/E2E)
    - Runs pytest with coverage (optional)
    - Maps coverage to architecture layers
    - Identifies uncovered modules
    - Test quality metrics
    """
    
    def __init__(self):
        """Initialize test patterns."""
        self.test_file_patterns = [
            re.compile(r'test_.*\.py$'),
            re.compile(r'.*_test\.py$'),
            re.compile(r'.*\.test\.(js|ts|jsx|tsx)$'),
            re.compile(r'.*\.spec\.(js|ts|jsx|tsx)$'),
            re.compile(r'Test.*\.cs$'),
            re.compile(r'.*Tests?\.cs$'),
            re.compile(r'.*_test\.go$'),
        ]
        
        # Test type indicators
        self.test_type_patterns = {
            'unit': [
                re.compile(r'test.*unit', re.IGNORECASE),
                re.compile(r'unit.*test', re.IGNORECASE),
                re.compile(r'@pytest\.mark\.unit'),
            ],
            'integration': [
                re.compile(r'test.*integration', re.IGNORECASE),
                re.compile(r'integration.*test', re.IGNORECASE),
                re.compile(r'@pytest\.mark\.integration'),
            ],
            'e2e': [
                re.compile(r'test.*e2e', re.IGNORECASE),
                re.compile(r'e2e.*test', re.IGNORECASE),
                re.compile(r'@pytest\.mark\.e2e'),
                re.compile(r'playwright'),
            ],
        }
        
        # Assertion patterns
        self.assertion_patterns = [
            re.compile(r'\bassert\s+'),
            re.compile(r'\.assert[A-Z]\w+\('),
            re.compile(r'expect\(.*\)\.(to|toBe|toEqual)'),
            re.compile(r'Assert\.[A-Z]\w+\('),
        ]
        
    def collect(self, project_path: Path, run_coverage: bool = False) -> Dict[str, Any]:
        """
        Collect test coverage data from project.
        
        Args:
            project_path: Root path of project to analyze
            run_coverage: Whether to run pytest --cov (slower but accurate)
            
        Returns:
            Dictionary with:
            - total_tests: Number of test files found
            - tests_by_type: Dict[str, int] count per type
            - coverage_by_layer: Dict[str, float] coverage per architecture layer
            - coverage_summary: Overall coverage percentage
            - test_quality_metrics: Assertions per test, avg test size
            - uncovered_modules: List of modules without tests
            - test_distribution: Tests per module
        """
        logger.info(f"🧪 Starting test coverage analysis on: {project_path}")
        
        results = {
            'total_tests': 0,
            'tests_by_type': defaultdict(int),
            'coverage_by_layer': {},
            'coverage_summary': 0.0,
            'test_quality_metrics': {
                'avg_assertions_per_test': 0.0,
                'avg_test_size': 0.0,
                'total_assertions': 0,
            },
            'uncovered_modules': [],
            'test_distribution': {},
        }
        
        # Discover test files
        test_files = self._discover_tests(project_path)
        results['total_tests'] = len(test_files)
        
        # Analyze test files
        total_assertions = 0
        total_test_lines = 0
        
        for test_file in test_files:
            try:
                content = test_file.read_text(encoding='utf-8', errors='ignore')
                
                # Classify test type
                test_type = self._classify_test_type(content)
                results['tests_by_type'][test_type] += 1
                
                # Count assertions
                assertions = self._count_assertions(content)
                total_assertions += assertions
                
                # Count test lines
                lines = len([line for line in content.split('\n') if line.strip()])
                total_test_lines += lines
                
                # Map to tested module
                module_path = self._infer_tested_module(test_file, project_path)
                if module_path:
                    results['test_distribution'][str(module_path)] = {
                        'test_file': str(test_file),
                        'test_type': test_type,
                        'assertions': assertions,
                    }
                    
            except Exception as e:
                logger.warning(f"Could not analyze test file {test_file}: {e}")
        
        # Calculate quality metrics
        if results['total_tests'] > 0:
            results['test_quality_metrics']['avg_assertions_per_test'] = total_assertions / results['total_tests']
            results['test_quality_metrics']['avg_test_size'] = total_test_lines / results['total_tests']
            results['test_quality_metrics']['total_assertions'] = total_assertions
        
        # Run pytest coverage if requested
        if run_coverage:
            coverage_data = self._run_pytest_coverage(project_path)
            if coverage_data:
                results['coverage_summary'] = coverage_data.get('total_coverage', 0.0)
                results['coverage_by_layer'] = coverage_data.get('layer_coverage', {})
        else:
            # Static analysis fallback
            results['coverage_by_layer'] = self._estimate_coverage_by_layer(project_path, test_files)
            results['coverage_summary'] = self._estimate_overall_coverage(project_path, test_files)
        
        # Find uncovered modules
        results['uncovered_modules'] = self._find_uncovered_modules(project_path, results['test_distribution'])
        
        # Convert defaultdict for serialization
        results['tests_by_type'] = dict(results['tests_by_type'])
        
        logger.info(f"✅ Test coverage analysis complete: {results['total_tests']} tests found")
        return results
    
    def _discover_tests(self, project_path: Path) -> List[Path]:
        """Discover all test files in project."""
        test_files = []
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                for pattern in self.test_file_patterns:
                    if pattern.search(file_path.name):
                        # Exclude common directories
                        if not any(exclude in str(file_path) for exclude in ['node_modules', '.venv', 'venv', 'bin', 'obj']):
                            test_files.append(file_path)
                        break
        
        return test_files
    
    def _classify_test_type(self, content: str) -> str:
        """Classify test as unit, integration, or E2E."""
        for test_type, patterns in self.test_type_patterns.items():
            for pattern in patterns:
                if pattern.search(content):
                    return test_type
        
        # Default to unit tests
        return 'unit'
    
    def _count_assertions(self, content: str) -> int:
        """Count assertion statements in test."""
        count = 0
        for pattern in self.assertion_patterns:
            count += len(pattern.findall(content))
        return count
    
    def _infer_tested_module(self, test_file: Path, project_path: Path) -> Optional[Path]:
        """Infer which module is being tested based on file structure."""
        # Common patterns:
        # tests/test_module.py -> src/module.py
        # tests/module_test.py -> src/module.py
        # module.test.js -> module.js
        
        test_name = test_file.stem
        
        # Remove test prefix/suffix
        module_name = test_name.replace('test_', '').replace('_test', '').replace('.test', '').replace('.spec', '')
        
        # Search for corresponding module
        for src_file in project_path.rglob(f'{module_name}.*'):
            if src_file != test_file and src_file.suffix in ['.py', '.js', '.ts', '.cs']:
                return src_file
        
        return None
    
    def _run_pytest_coverage(self, project_path: Path) -> Optional[Dict[str, Any]]:
        """Run pytest with coverage and parse results."""
        try:
            # Run pytest with JSON coverage report
            result = subprocess.run(
                ['pytest', '--cov=src', '--cov-report=json', '--cov-report=term'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            # Parse coverage.json if it exists
            coverage_file = project_path / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0.0)
                
                # Map coverage to layers
                layer_coverage = self._map_coverage_to_layers(coverage_data, project_path)
                
                return {
                    'total_coverage': total_coverage,
                    'layer_coverage': layer_coverage,
                }
        
        except Exception as e:
            logger.warning(f"Could not run pytest coverage: {e}")
        
        return None
    
    def _map_coverage_to_layers(self, coverage_data: Dict[str, Any], project_path: Path) -> Dict[str, float]:
        """Map coverage percentages to architecture layers."""
        layer_patterns = {
            'presentation': [r'controllers?', r'views?', r'api', r'routes?'],
            'business': [r'services?', r'domain', r'core', r'business'],
            'data': [r'repositories?', r'dao', r'data', r'persistence'],
        }
        
        layer_coverage = defaultdict(list)
        
        files = coverage_data.get('files', {})
        for file_path, file_data in files.items():
            coverage_pct = file_data.get('summary', {}).get('percent_covered', 0.0)
            
            # Classify file to layer
            for layer, patterns in layer_patterns.items():
                if any(re.search(pattern, file_path, re.IGNORECASE) for pattern in patterns):
                    layer_coverage[layer].append(coverage_pct)
                    break
        
        # Average coverage per layer
        return {
            layer: sum(coverages) / len(coverages) if coverages else 0.0
            for layer, coverages in layer_coverage.items()
        }
    
    def _estimate_coverage_by_layer(self, project_path: Path, test_files: List[Path]) -> Dict[str, float]:
        """Estimate coverage by layer using static analysis."""
        # Count tested vs untested files per layer
        layer_patterns = {
            'presentation': [r'controllers?', r'views?', r'api', r'routes?'],
            'business': [r'services?', r'domain', r'core', r'business'],
            'data': [r'repositories?', r'dao', r'data', r'persistence'],
        }
        
        layer_files = defaultdict(set)
        tested_files = {self._infer_tested_module(tf, project_path) for tf in test_files}
        tested_files.discard(None)
        
        # Classify all source files
        for src_file in project_path.rglob('*.py'):
            if any(exclude in str(src_file) for exclude in ['node_modules', '.venv', 'venv', 'test']):
                continue
            
            for layer, patterns in layer_patterns.items():
                if any(re.search(pattern, str(src_file), re.IGNORECASE) for pattern in patterns):
                    layer_files[layer].add(src_file)
                    break
        
        # Calculate coverage percentage
        coverage = {}
        for layer, files in layer_files.items():
            if files:
                tested_count = len(files & tested_files)
                coverage[layer] = (tested_count / len(files)) * 100
            else:
                coverage[layer] = 0.0
        
        return coverage
    
    def _estimate_overall_coverage(self, project_path: Path, test_files: List[Path]) -> float:
        """Estimate overall coverage percentage."""
        # Count all source files
        all_src_files = set()
        for src_file in project_path.rglob('*.py'):
            if not any(exclude in str(src_file) for exclude in ['node_modules', '.venv', 'venv', 'test']):
                all_src_files.add(src_file)
        
        # Count tested files
        tested_files = {self._infer_tested_module(tf, project_path) for tf in test_files}
        tested_files.discard(None)
        
        if all_src_files:
            return (len(tested_files) / len(all_src_files)) * 100
        
        return 0.0
    
    def _find_uncovered_modules(self, project_path: Path, test_distribution: Dict[str, Any]) -> List[str]:
        """Find modules without test coverage."""
        tested_modules = set(test_distribution.keys())
        uncovered = []
        
        for src_file in project_path.rglob('*.py'):
            if any(exclude in str(src_file) for exclude in ['node_modules', '.venv', 'venv', 'test', '__init__']):
                continue
            
            if str(src_file) not in tested_modules:
                uncovered.append(str(src_file))
        
        return sorted(uncovered)
