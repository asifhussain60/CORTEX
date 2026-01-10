"""
CORTEX 6.0 - AC Traceability System

Provides test-to-acceptance-criteria mapping via @pytest.mark.ac_id() markers.

Components:
- ACTraceabilitySystem: Main orchestrator for scanning and analysis
- ACCoverageMatrix: AC→Test mapping data structure
- ACGapReport: Gap detection results (uncovered AC, orphaned tests)
- TraceabilityConfig: Configuration for traceability operations

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
import yaml
from datetime import datetime


@dataclass
class TraceabilityConfig:
    """Configuration for AC traceability system."""
    
    tests_root: Path
    registry_path: Path
    ac_definitions_path: Optional[Path] = None
    
    # Patterns for test file discovery
    test_file_patterns: List[str] = field(default_factory=lambda: [
        "test_*.py",
        "*_test.py"
    ])
    
    # AC-ID validation pattern
    ac_id_pattern: str = r"^AC-[A-Z]+-\d{3}$"
    
    def __post_init__(self):
        """Validate configuration."""
        # Don't require tests_root to exist (may be temp dir in tests)
        pass


@dataclass
class ACCoverageMatrix:
    """AC→Test coverage mapping."""
    
    coverage: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def coverage_percentage(self) -> float:
        """Calculate coverage percentage."""
        if 'total_ac_count' not in self.metadata:
            return 0.0
        
        total_ac = self.metadata['total_ac_count']
        covered_ac = len(self.coverage)
        
        if total_ac == 0:
            return 0.0
        
        return (covered_ac / total_ac) * 100
    
    def export_yaml(self, output_path: Path) -> None:
        """Export coverage matrix to YAML file."""
        data = {
            'metadata': self.metadata,
            'coverage': self.coverage,
            'statistics': {
                'total_ac': self.metadata.get('total_ac_count', 0),
                'covered_ac': len(self.coverage),
                'coverage_percentage': self.coverage_percentage,
                'total_tests': sum(len(tests) for tests in self.coverage.values())
            }
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


@dataclass
class ACGapReport:
    """Gap detection results."""
    
    uncovered_ac: Set[str] = field(default_factory=set)
    orphaned_tests: List[Dict[str, Any]] = field(default_factory=list)
    critical_gaps: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ACTraceabilitySystem:
    """
    Main system for AC traceability analysis.
    
    Scans test files for @pytest.mark.ac_id() markers and generates:
    - Coverage matrix (AC→Test mapping)
    - Gap reports (AC without tests, tests without AC)
    - Validation results (per-AC coverage status)
    """
    
    def __init__(self, config: TraceabilityConfig):
        """Initialize traceability system."""
        self.config = config
        self._scan_cache: Optional[Dict[str, List[Dict[str, Any]]]] = None
        self._ac_definitions: Optional[Dict[str, Any]] = None
    
    def scan_tests(self, force_refresh: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan test files for @pytest.mark.ac_id() markers.
        
        Returns:
            Dict mapping AC-ID to list of test locations
            Format: {
                'AC-GOV-001': [
                    {'file': 'tests/test_gov.py', 'line': 10, 'test': 'test_governance'},
                    ...
                ],
                ...
            }
        """
        if self._scan_cache is not None and not force_refresh:
            return self._scan_cache
        
        results: Dict[str, List[Dict[str, Any]]] = {}
        
        # Find all test files
        test_files = self._discover_test_files()
        
        # Scan each test file
        for test_file in test_files:
            markers = self._extract_markers_from_file(test_file)
            
            for marker_info in markers:
                ac_ids = marker_info['ac_ids']
                test_name = marker_info['test_name']
                line_number = marker_info['line_number']
                
                for ac_id in ac_ids:
                    if ac_id not in results:
                        results[ac_id] = []
                    
                    results[ac_id].append({
                        'file': str(test_file.relative_to(self.config.tests_root)),
                        'line': line_number,
                        'test': test_name
                    })
        
        self._scan_cache = results
        return results
    
    def generate_coverage_matrix(self) -> ACCoverageMatrix:
        """
        Generate coverage matrix from scan results.
        
        Returns:
            ACCoverageMatrix with AC→Test mappings and statistics
        """
        # Scan tests
        scan_results = self.scan_tests()
        
        # Load AC definitions if available
        total_ac_count = 0
        if self.config.ac_definitions_path and self.config.ac_definitions_path.exists():
            ac_defs = self._load_ac_definitions()
            total_ac_count = len(ac_defs.get('acceptance_criteria', []))
        
        # Build matrix
        matrix = ACCoverageMatrix(
            coverage=scan_results,
            metadata={
                'generated_at': datetime.now().isoformat(),
                'tests_root': str(self.config.tests_root),
                'total_ac_count': total_ac_count,
                'scan_file_count': len(self._discover_test_files())
            }
        )
        
        return matrix
    
    def detect_gaps(self) -> ACGapReport:
        """
        Detect gaps in test coverage.
        
        Returns:
            ACGapReport with uncovered AC and orphaned tests
        """
        # Scan tests
        scan_results = self.scan_tests()
        covered_ac = set(scan_results.keys())
        
        # Load AC definitions
        uncovered_ac = set()
        critical_gaps = set()
        
        if self.config.ac_definitions_path and self.config.ac_definitions_path.exists():
            ac_defs = self._load_ac_definitions()
            all_ac = set()
            
            for ac in ac_defs.get('acceptance_criteria', []):
                ac_id = ac['id']
                all_ac.add(ac_id)
                
                # Check if uncovered
                if ac_id not in covered_ac:
                    uncovered_ac.add(ac_id)
                    
                    # Check if critical
                    if ac.get('priority') == 'P0_CRITICAL':
                        critical_gaps.add(ac_id)
        
        # Find orphaned tests (tests without AC markers)
        orphaned_tests = self._find_orphaned_tests()
        
        return ACGapReport(
            uncovered_ac=uncovered_ac,
            orphaned_tests=orphaned_tests,
            critical_gaps=critical_gaps,
            metadata={
                'scan_date': datetime.now().isoformat(),
                'total_uncovered': len(uncovered_ac),
                'total_orphaned': len(orphaned_tests),
                'total_critical_gaps': len(critical_gaps)
            }
        )
    
    def validate_ac(self, ac_id: str, return_count: bool = False) -> Union[bool, int]:
        """
        Validate if an AC-ID has test coverage.
        
        Args:
            ac_id: AC-ID to validate
            return_count: If True, return count of covering tests instead of bool
        
        Returns:
            bool: True if covered, False otherwise
            int: Number of covering tests (if return_count=True)
        """
        scan_results = self.scan_tests()
        
        has_coverage = ac_id in scan_results
        
        if return_count:
            return len(scan_results.get(ac_id, []))
        
        return has_coverage
    
    def validate_ac_batch(self, ac_ids: List[str]) -> Dict[str, bool]:
        """
        Validate multiple AC-IDs in batch.
        
        Args:
            ac_ids: List of AC-IDs to validate
        
        Returns:
            Dict mapping AC-ID to coverage status (True/False)
        """
        scan_results = self.scan_tests()
        
        return {
            ac_id: (ac_id in scan_results)
            for ac_id in ac_ids
        }
    
    def generate_coverage_report(self, output_path: Path) -> None:
        """
        Generate comprehensive coverage report.
        
        Args:
            output_path: Path to save report (YAML format)
        """
        # Generate matrix and gaps
        matrix = self.generate_coverage_matrix()
        gap_report = self.detect_gaps()
        
        # Build comprehensive report
        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'generator': 'ACTraceabilitySystem',
                'version': '1.0.0'
            },
            'coverage': matrix.coverage,
            'gaps': {
                'uncovered_ac': sorted(list(gap_report.uncovered_ac)),
                'orphaned_tests': gap_report.orphaned_tests,
                'critical_gaps': sorted(list(gap_report.critical_gaps))
            },
            'statistics': {
                'total_ac': matrix.metadata.get('total_ac_count', 0),
                'covered_ac': len(matrix.coverage),
                'uncovered_ac': len(gap_report.uncovered_ac),
                'coverage_percentage': matrix.coverage_percentage,
                'total_tests': sum(len(tests) for tests in matrix.coverage.values()),
                'orphaned_tests': len(gap_report.orphaned_tests),
                'critical_gaps': len(gap_report.critical_gaps)
            }
        }
        
        # Save report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            yaml.dump(report, f, default_flow_style=False, sort_keys=False)
    
    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================
    
    def _discover_test_files(self) -> List[Path]:
        """Discover all test files in tests_root."""
        if not self.config.tests_root.exists():
            return []
        
        test_files = []
        
        for pattern in self.config.test_file_patterns:
            test_files.extend(self.config.tests_root.rglob(pattern))
        
        # Filter out conftest.py, __init__.py, and non-test files
        excluded_names = ('conftest.py', '__init__.py')
        test_files = [
            f for f in test_files
            if f.name not in excluded_names and self._is_test_file(f)
        ]
        
        return sorted(test_files)
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a valid test file."""
        name = file_path.name
        # Must match test_*.py or *_test.py patterns
        return name.startswith('test_') or name.endswith('_test.py')
    
    def _extract_markers_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract @pytest.mark.ac_id markers from a Python file.
        
        Returns:
            List of marker info dicts with ac_ids, test_name, line_number
        """
        try:
            source = file_path.read_text()
            tree = ast.parse(source, filename=str(file_path))
        except Exception:
            return []
        
        markers = []
        
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            
            # Check if it's a test function
            if not node.name.startswith('test_'):
                continue
            
            # Extract ac_id markers from decorators
            ac_ids = self._extract_ac_ids_from_decorators(node.decorator_list)
            
            if ac_ids:
                markers.append({
                    'ac_ids': ac_ids,
                    'test_name': node.name,
                    'line_number': node.lineno
                })
        
        return markers
    
    def _extract_ac_ids_from_decorators(self, decorators: List[ast.expr]) -> List[str]:
        """Extract AC-IDs from @pytest.mark.ac_id() decorators."""
        ac_ids = []
        
        for decorator in decorators:
            # Handle pytest.mark.ac_id("AC-XXX-001")
            if isinstance(decorator, ast.Call):
                if self._is_ac_id_marker(decorator.func):
                    # Extract string arguments
                    for arg in decorator.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            ac_ids.append(arg.value)
            
            # Handle @pytest.mark.ac_id (attribute access)
            elif isinstance(decorator, ast.Attribute):
                if decorator.attr == 'ac_id':
                    # This case needs argument extraction from parent
                    pass
        
        return ac_ids
    
    def _is_ac_id_marker(self, node: ast.expr) -> bool:
        """Check if AST node represents pytest.mark.ac_id."""
        if isinstance(node, ast.Attribute):
            if node.attr == 'ac_id':
                if isinstance(node.value, ast.Attribute):
                    if node.value.attr == 'mark':
                        if isinstance(node.value.value, ast.Name):
                            if node.value.value.id == 'pytest':
                                return True
        return False
    
    def _load_ac_definitions(self) -> Dict[str, Any]:
        """Load AC definitions from YAML file."""
        if self._ac_definitions is not None:
            return self._ac_definitions
        
        if not self.config.ac_definitions_path or not self.config.ac_definitions_path.exists():
            return {}
        
        with open(self.config.ac_definitions_path) as f:
            self._ac_definitions = yaml.safe_load(f)
        
        return self._ac_definitions
    
    def _find_orphaned_tests(self) -> List[Dict[str, Any]]:
        """Find test functions that don't have AC-ID markers."""
        orphaned = []
        test_files = self._discover_test_files()
        
        for test_file in test_files:
            try:
                source = test_file.read_text()
                tree = ast.parse(source, filename=str(test_file))
            except Exception:
                continue
            
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                
                if not node.name.startswith('test_'):
                    continue
                
                # Check if has ac_id marker
                ac_ids = self._extract_ac_ids_from_decorators(node.decorator_list)
                
                if not ac_ids:
                    orphaned.append({
                        'file': str(test_file.relative_to(self.config.tests_root)),
                        'line': node.lineno,
                        'test': node.name
                    })
        
        return orphaned
