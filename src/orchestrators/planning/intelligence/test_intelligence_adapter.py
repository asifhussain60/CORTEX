"""
Test Intelligence Adapter - Test Coverage Analysis for Planning System

Purpose: Analyzes test coverage, discovers test gaps, and provides intelligent recommendations
for test strategy within feature plans.

Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-24 (Week 9 Day 1)

Responsibilities:
- Test file discovery and mapping
- Coverage calculation and gap analysis  
- Test distribution analysis (unit/integration/e2e)
- Critical path test identification
- Test strategy recommendations

Integration Points:
- Planning System: Injects test coverage requirements into plans
- TDD Orchestrator: Provides test file targets
- Coverage Tracker (Tier 3): Retrieves coverage metrics
- Knowledge Graph (Tier 2): Learns test patterns

Week 9 Target: 400 LOC
"""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import json
import subprocess

logger = logging.getLogger(__name__)


@dataclass
class TestFile:
    """Representation of a test file."""
    path: Path
    test_count: int
    test_type: str  # unit, integration, e2e
    coverage_percentage: float = 0.0
    target_module: Optional[Path] = None


@dataclass
class TestCoverageAnalysis:
    """Results of test coverage analysis."""
    total_files: int = 0
    test_files: int = 0
    overall_coverage: float = 0.0
    unit_test_coverage: float = 0.0
    integration_test_coverage: float = 0.0
    e2e_test_coverage: float = 0.0
    
    uncovered_modules: List[Path] = field(default_factory=list)
    critical_gaps: List[str] = field(default_factory=list)
    test_distribution: Dict[str, int] = field(default_factory=dict)
    
    recommendations: List[str] = field(default_factory=list)


@dataclass
class TestGap:
    """Represents a test coverage gap."""
    module_path: Path
    severity: str  # critical, high, medium, low
    gap_type: str  # missing_tests, low_coverage, no_edge_cases
    recommendation: str
    estimated_tests_needed: int


class TestIntelligenceAdapter:
    """
    Adapter for test coverage intelligence within Planning System.
    
    Provides deep insights into test coverage, gaps, and recommendations
    for feature plans.
    
    Usage:
        adapter = TestIntelligenceAdapter(project_root)
        analysis = adapter.analyze_project_coverage()
        gaps = adapter.identify_critical_gaps()
        recommendations = adapter.generate_test_strategy(feature_scope)
    """
    
    def __init__(self, project_root: Path, cortex_root: Optional[Path] = None):
        """
        Initialize test intelligence adapter.
        
        Args:
            project_root: Root of project to analyze
            cortex_root: Root of CORTEX (for internal analysis)
        """
        self.project_root = Path(project_root)
        self.cortex_root = Path(cortex_root) if cortex_root else None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cache for performance
        self._test_file_cache: Dict[Path, TestFile] = {}
        self._coverage_cache: Optional[TestCoverageAnalysis] = None
    
    # ========== Core Analysis Methods ==========
    
    def analyze_project_coverage(self, force_refresh: bool = False) -> TestCoverageAnalysis:
        """
        Analyze overall test coverage for project.
        
        Args:
            force_refresh: Force re-analysis (ignore cache)
            
        Returns:
            Comprehensive test coverage analysis
        """
        if not force_refresh and self._coverage_cache:
            return self._coverage_cache
        
        self.logger.info(f"Analyzing test coverage for {self.project_root}")
        
        # Discover all test files
        test_files = self._discover_test_files()
        
        # Calculate coverage metrics
        coverage_data = self._calculate_coverage_metrics(test_files)
        
        # Analyze test distribution
        distribution = self._analyze_test_distribution(test_files)
        
        # Identify gaps
        uncovered_modules = self._find_uncovered_modules(test_files)
        critical_gaps = self._identify_critical_gaps(uncovered_modules)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            coverage_data,
            distribution,
            critical_gaps
        )
        
        analysis = TestCoverageAnalysis(
            total_files=len(list(self.project_root.rglob("*.py"))),
            test_files=len(test_files),
            overall_coverage=coverage_data.get("overall", 0.0),
            unit_test_coverage=coverage_data.get("unit", 0.0),
            integration_test_coverage=coverage_data.get("integration", 0.0),
            e2e_test_coverage=coverage_data.get("e2e", 0.0),
            uncovered_modules=uncovered_modules,
            critical_gaps=critical_gaps,
            test_distribution=distribution,
            recommendations=recommendations
        )
        
        self._coverage_cache = analysis
        return analysis
    
    def identify_critical_gaps(self, target_modules: Optional[List[Path]] = None) -> List[TestGap]:
        """
        Identify critical test coverage gaps.
        
        Args:
            target_modules: Specific modules to analyze (None = all)
            
        Returns:
            List of test gaps prioritized by severity
        """
        gaps: List[TestGap] = []
        
        modules_to_check = target_modules if target_modules else self._find_all_modules()
        
        for module in modules_to_check:
            # Check if module has tests
            test_file = self._find_test_file_for_module(module)
            
            if not test_file:
                # Critical gap: No tests
                gaps.append(TestGap(
                    module_path=module,
                    severity="critical",
                    gap_type="missing_tests",
                    recommendation=f"Create test file: tests/{module.stem}_test.py",
                    estimated_tests_needed=self._estimate_test_count(module)
                ))
            else:
                # Check coverage level
                coverage = self._get_module_coverage(module)
                
                if coverage < 50:
                    gaps.append(TestGap(
                        module_path=module,
                        severity="high",
                        gap_type="low_coverage",
                        recommendation=f"Increase coverage from {coverage}% to 80%+",
                        estimated_tests_needed=int((80 - coverage) / 10)
                    ))
                
                # Check for edge case testing
                if not self._has_edge_case_tests(test_file):
                    gaps.append(TestGap(
                        module_path=module,
                        severity="medium",
                        gap_type="no_edge_cases",
                        recommendation="Add edge case and error handling tests",
                        estimated_tests_needed=3
                    ))
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        gaps.sort(key=lambda g: severity_order[g.severity])
        
        return gaps
    
    def generate_test_strategy(
        self,
        feature_scope: Dict[str, Any],
        target_coverage: float = 85.0
    ) -> Dict[str, Any]:
        """
        Generate intelligent test strategy for feature plan.
        
        Args:
            feature_scope: Feature information (files affected, complexity, etc.)
            target_coverage: Desired coverage percentage
            
        Returns:
            Test strategy with recommendations
        """
        strategy = {
            "target_coverage": target_coverage,
            "test_types": {},
            "test_files_to_create": [],
            "estimated_test_count": 0,
            "tdd_recommended": False,
            "reasoning": []
        }
        
        files_affected = feature_scope.get("files_affected", [])
        complexity = feature_scope.get("complexity", "medium")
        
        # Analyze each file
        for file_path in files_affected:
            module_path = Path(file_path)
            
            # Determine test type based on file location
            if "api" in str(module_path) or "views" in str(module_path):
                strategy["test_types"][str(module_path)] = ["unit", "integration"]
                strategy["reasoning"].append(f"{module_path.name}: API endpoint - needs unit + integration tests")
            elif "models" in str(module_path) or "entities" in str(module_path):
                strategy["test_types"][str(module_path)] = ["unit"]
                strategy["reasoning"].append(f"{module_path.name}: Data model - unit tests sufficient")
            elif "orchestrator" in str(module_path):
                strategy["test_types"][str(module_path)] = ["unit", "integration", "e2e"]
                strategy["reasoning"].append(f"{module_path.name}: Orchestrator - needs full test suite")
            else:
                strategy["test_types"][str(module_path)] = ["unit"]
            
            # Calculate test file path
            test_file = self._generate_test_file_path(module_path)
            if not test_file.exists():
                strategy["test_files_to_create"].append(str(test_file))
        
        # Calculate estimated test count
        strategy["estimated_test_count"] = len(files_affected) * 8  # ~8 tests per module
        
        # TDD recommendation
        if complexity in ["high", "complex"] or len(files_affected) > 3:
            strategy["tdd_recommended"] = True
            strategy["reasoning"].append("TDD recommended: High complexity or multiple files affected")
        
        return strategy
    
    # ========== Discovery Methods ==========
    
    def _discover_test_files(self) -> List[TestFile]:
        """Discover all test files in project."""
        test_files: List[TestFile] = []
        
        # Common test patterns
        test_dirs = ["tests", "test"]
        test_patterns = ["test_*.py", "*_test.py", "*_tests.py"]
        
        for test_dir in test_dirs:
            test_path = self.project_root / test_dir
            if not test_path.exists():
                continue
            
            for pattern in test_patterns:
                for test_file_path in test_path.rglob(pattern):
                    if test_file_path.is_file():
                        test_file = self._analyze_test_file(test_file_path)
                        test_files.append(test_file)
                        self._test_file_cache[test_file_path] = test_file
        
        return test_files
    
    def _analyze_test_file(self, file_path: Path) -> TestFile:
        """Analyze a single test file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            # Count test functions
            test_count = sum(
                1 for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')
            )
            
            # Determine test type from path
            test_type = self._determine_test_type(file_path)
            
            # Try to find target module
            target_module = self._find_target_module(file_path)
            
            return TestFile(
                path=file_path,
                test_count=test_count,
                test_type=test_type,
                target_module=target_module
            )
        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_path}: {e}")
            return TestFile(
                path=file_path,
                test_count=0,
                test_type="unknown"
            )
    
    def _determine_test_type(self, test_path: Path) -> str:
        """Determine if test is unit, integration, or e2e."""
        path_str = str(test_path).lower()
        
        if "integration" in path_str or "e2e" in path_str:
            return "integration"
        elif "unit" in path_str:
            return "unit"
        else:
            # Heuristic: tests in subdirectories are likely integration tests
            depth = len(test_path.relative_to(self.project_root / "tests").parts)
            return "integration" if depth > 1 else "unit"
    
    def _find_target_module(self, test_path: Path) -> Optional[Path]:
        """Find the module this test file is testing."""
        # Common patterns: test_module.py → module.py
        test_name = test_path.stem
        
        if test_name.startswith("test_"):
            module_name = test_name[5:] + ".py"
        elif test_name.endswith("_test"):
            module_name = test_name[:-5] + ".py"
        else:
            module_name = test_name + ".py"
        
        # Search in src directories
        for src_dir in ["src", "lib", self.project_root]:
            for module_path in Path(src_dir).rglob(module_name):
                if module_path.is_file():
                    return module_path
        
        return None
    
    # ========== Coverage Calculation ==========
    
    def _calculate_coverage_metrics(self, test_files: List[TestFile]) -> Dict[str, float]:
        """Calculate coverage metrics by test type."""
        # Try to get actual coverage from pytest-cov if available
        try:
            result = subprocess.run(
                ["pytest", "--cov", "--cov-report", "json", "--quiet"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                coverage_file = self.project_root / "coverage.json"
                if coverage_file.exists():
                    with open(coverage_file) as f:
                        data = json.load(f)
                        return {
                            "overall": data.get("totals", {}).get("percent_covered", 0.0),
                            "unit": 0.0,  # Would need detailed breakdown
                            "integration": 0.0,
                            "e2e": 0.0
                        }
        except Exception as e:
            self.logger.debug(f"Could not get pytest coverage: {e}")
        
        # Fallback: Estimate based on test distribution
        unit_tests = sum(1 for t in test_files if t.test_type == "unit")
        integration_tests = sum(1 for t in test_files if t.test_type == "integration")
        
        total_modules = len(list(self.project_root.rglob("src/**/*.py")))
        
        if total_modules == 0:
            return {"overall": 0.0, "unit": 0.0, "integration": 0.0, "e2e": 0.0}
        
        # Rough estimate: 1 test file covers ~3 modules at 80%
        estimated_coverage = min((len(test_files) * 3 * 0.8) / total_modules * 100, 100)
        
        return {
            "overall": estimated_coverage,
            "unit": (unit_tests / total_modules * 100) if total_modules > 0 else 0,
            "integration": (integration_tests / total_modules * 50) if total_modules > 0 else 0,
            "e2e": 0.0
        }
    
    # ========== Gap Analysis ==========
    
    def _find_uncovered_modules(self, test_files: List[TestFile]) -> List[Path]:
        """Find modules without test coverage."""
        tested_modules = {t.target_module for t in test_files if t.target_module}
        all_modules = set(self.project_root.rglob("src/**/*.py"))
        
        uncovered = [m for m in all_modules if m not in tested_modules]
        return sorted(uncovered)
    
    def _identify_critical_gaps(self, uncovered_modules: List[Path]) -> List[str]:
        """Identify critical gaps that need immediate attention."""
        critical = []
        
        for module in uncovered_modules:
            module_str = str(module)
            
            # Critical: orchestrators, agents, core modules
            if any(keyword in module_str for keyword in ["orchestrator", "agent", "core", "api"]):
                critical.append(f"Critical: {module.name} has no tests")
            
            # High complexity files without tests
            if self._estimate_complexity(module) > 10:
                critical.append(f"High complexity: {module.name} needs test coverage")
        
        return critical[:10]  # Top 10 most critical
    
    # ========== Helpers ==========
    
    def _analyze_test_distribution(self, test_files: List[TestFile]) -> Dict[str, int]:
        """Analyze distribution of test types."""
        distribution = {"unit": 0, "integration": 0, "e2e": 0, "unknown": 0}
        
        for test_file in test_files:
            distribution[test_file.test_type] = distribution.get(test_file.test_type, 0) + test_file.test_count
        
        return distribution
    
    def _generate_recommendations(
        self,
        coverage_data: Dict[str, float],
        distribution: Dict[str, int],
        critical_gaps: List[str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        overall_coverage = coverage_data.get("overall", 0)
        
        if overall_coverage < 70:
            recommendations.append(f"⚠️ Overall coverage ({overall_coverage:.1f}%) below 70% - prioritize test creation")
        
        if distribution.get("unit", 0) < distribution.get("integration", 0):
            recommendations.append("📊 More integration tests than unit tests - balance pyramid")
        
        if critical_gaps:
            recommendations.append(f"🔥 {len(critical_gaps)} critical modules need tests immediately")
        
        if distribution.get("e2e", 0) == 0:
            recommendations.append("🎯 No E2E tests found - consider adding smoke tests")
        
        return recommendations
    
    def _find_all_modules(self) -> List[Path]:
        """Find all Python modules in project."""
        return list(self.project_root.rglob("src/**/*.py"))
    
    def _find_test_file_for_module(self, module_path: Path) -> Optional[TestFile]:
        """Find test file corresponding to module."""
        # Check cache first
        for test_file in self._test_file_cache.values():
            if test_file.target_module == module_path:
                return test_file
        return None
    
    def _get_module_coverage(self, module_path: Path) -> float:
        """Get coverage percentage for specific module."""
        # Simplified: Would integrate with coverage.py for actual data
        test_file = self._find_test_file_for_module(module_path)
        return 75.0 if test_file and test_file.test_count > 5 else 30.0
    
    def _has_edge_case_tests(self, test_file: TestFile) -> bool:
        """Check if test file includes edge case testing."""
        try:
            with open(test_file.path, 'r') as f:
                content = f.read().lower()
                return any(keyword in content for keyword in ["edge", "boundary", "invalid", "error"])
        except Exception:
            return False
    
    def _estimate_test_count(self, module_path: Path) -> int:
        """Estimate number of tests needed for module."""
        complexity = self._estimate_complexity(module_path)
        return max(5, complexity * 2)  # 2 tests per complexity point, min 5
    
    def _estimate_complexity(self, module_path: Path) -> int:
        """Estimate module complexity (simple heuristic)."""
        try:
            with open(module_path, 'r') as f:
                lines = f.readlines()
                # Simple heuristic: functions + classes
                functions = sum(1 for line in lines if line.strip().startswith("def "))
                classes = sum(1 for line in lines if line.strip().startswith("class "))
                return functions + classes * 3
        except Exception:
            return 5  # Default complexity
    
    def _generate_test_file_path(self, module_path: Path) -> Path:
        """Generate expected test file path for module."""
        return self.project_root / "tests" / f"test_{module_path.stem}.py"
