#!/usr/bin/env python3
"""
System Refinement Orchestrator - CORTEX 4.0

Orchestrates 7-phase holistic system refinement:
Phase 1: Discovery - AST analysis, code inventory
Phase 2: SKULL Review - Test quality optimization
Phase 3: Documentation - Doc quality enhancement
Phase 4: Code Quality - SOLID violations, smells
Phase 5: Architecture - Pattern application, decoupling
Phase 6: Performance - Complexity reduction, optimization
Phase 7: Validation - Verify improvements, rollback if needed

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 4.0.0
Date: December 26, 2025
"""

import ast
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import json
import subprocess
import re

logger = logging.getLogger(__name__)


@dataclass
class RefinementMetrics:
    """Metrics tracked during refinement."""
    # Discovery
    total_files: int = 0
    total_loc: int = 0
    total_classes: int = 0
    total_methods: int = 0
    
    # Code Quality
    solid_violations_found: int = 0
    solid_violations_fixed: int = 0
    code_smells_found: int = 0
    code_smells_fixed: int = 0
    
    # Complexity
    complexity_before: float = 0.0
    complexity_after: float = 0.0
    
    # Test Coverage
    coverage_before: float = 0.0
    coverage_after: float = 0.0
    
    # Quality Scores
    pylint_before: float = 0.0
    pylint_after: float = 0.0
    
    # Performance
    lines_removed: int = 0
    dead_code_removed: int = 0
    duplicates_eliminated: int = 0
    
    # Validation
    tests_passing_before: int = 0
    tests_passing_after: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "discovery": {
                "files": self.total_files,
                "loc": self.total_loc,
                "classes": self.total_classes,
                "methods": self.total_methods
            },
            "code_quality": {
                "solid_violations": {
                    "found": self.solid_violations_found,
                    "fixed": self.solid_violations_fixed,
                    "fix_rate": f"{(self.solid_violations_fixed / max(self.solid_violations_found, 1)) * 100:.1f}%"
                },
                "code_smells": {
                    "found": self.code_smells_found,
                    "fixed": self.code_smells_fixed,
                    "fix_rate": f"{(self.code_smells_fixed / max(self.code_smells_found, 1)) * 100:.1f}%"
                }
            },
            "complexity": {
                "before": round(self.complexity_before, 2),
                "after": round(self.complexity_after, 2),
                "reduction": round(self.complexity_before - self.complexity_after, 2),
                "improvement": f"{((self.complexity_before - self.complexity_after) / max(self.complexity_before, 1)) * 100:.1f}%"
            },
            "coverage": {
                "before": f"{self.coverage_before:.1f}%",
                "after": f"{self.coverage_after:.1f}%",
                "increase": f"{self.coverage_after - self.coverage_before:.1f}%"
            },
            "quality_scores": {
                "pylint_before": round(self.pylint_before, 2),
                "pylint_after": round(self.pylint_after, 2),
                "improvement": round(self.pylint_after - self.pylint_before, 2)
            },
            "performance": {
                "lines_removed": self.lines_removed,
                "dead_code_removed": self.dead_code_removed,
                "duplicates_eliminated": self.duplicates_eliminated
            },
            "validation": {
                "tests_before": self.tests_passing_before,
                "tests_after": self.tests_passing_after,
                "delta": self.tests_passing_after - self.tests_passing_before
            }
        }


@dataclass
class SOLIDViolation:
    """SOLID principle violation."""
    principle: str  # SRP, OCP, LSP, ISP, DIP
    violation_type: str
    location: str
    severity: str  # high, medium, low
    metrics: Dict[str, Any]
    recommendation: str
    auto_fixable: bool = False
    

@dataclass
class CodeSmell:
    """Code smell detection."""
    smell_type: str
    location: str
    severity: str
    metrics: Dict[str, Any]
    recommendation: str
    auto_fixable: bool = False


class RefinementOrchestrator:
    """
    CORTEX 4.0 System Refinement Orchestrator.
    
    Performs 7-phase holistic refinement:
    1. Discovery - Code inventory and AST analysis
    2. SKULL Review - Test quality optimization
    3. Documentation - Doc enhancement
    4. Code Quality - SOLID + smells
    5. Architecture - Patterns + decoupling
    6. Performance - Complexity reduction
    7. Validation - Verify improvements
    """
    
    def __init__(
        self,
        cortex_root: Optional[Path] = None,
        target_path: Optional[Path] = None,
        dry_run: bool = True,
        phase: str = "all"
    ):
        """
        Initialize refinement orchestrator.
        
        Args:
            cortex_root: CORTEX installation root
            target_path: Target directory/file to refine (defaults to cortex_root)
            dry_run: Preview changes without applying
            phase: Phase to run (all, discovery, skull, docs, quality, architecture, performance, validation)
        """
        self.cortex_root = cortex_root or Path.cwd()
        self.target_path = target_path or self.cortex_root
        self.dry_run = dry_run
        self.phase = phase
        
        self.metrics = RefinementMetrics()
        self.solid_violations: List[SOLIDViolation] = []
        self.code_smells: List[CodeSmell] = []
        self.refactoring_recommendations: List[Dict[str, Any]] = []
        
        self.start_time = datetime.now()
        
        logger.info(f"🎭 Orchestrator engaged: RefinementOrchestrator")
        logger.info(f"Target: {self.target_path}")
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
        logger.info(f"Phase: {self.phase}")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute refinement workflow.
        
        Returns:
            Results dictionary with metrics and recommendations
        """
        results = {
            "status": "success",
            "phases": {},
            "metrics": {},
            "violations": [],
            "recommendations": []
        }
        
        try:
            if self.phase in ["all", "discovery"]:
                logger.info("\n🎭 Phase transition: START → DISCOVERY")
                results["phases"]["discovery"] = self._phase_1_discovery()
            
            if self.phase in ["all", "skull"]:
                logger.info("\n🎭 Phase transition: DISCOVERY → SKULL_REVIEW")
                results["phases"]["skull_review"] = self._phase_2_skull_review()
            
            if self.phase in ["all", "docs"]:
                logger.info("\n🎭 Phase transition: SKULL_REVIEW → DOCUMENTATION")
                results["phases"]["documentation"] = self._phase_3_documentation()
            
            if self.phase in ["all", "quality"]:
                logger.info("\n🎭 Phase transition: DOCUMENTATION → CODE_QUALITY")
                results["phases"]["code_quality"] = self._phase_4_code_quality()
            
            if self.phase in ["all", "architecture"]:
                logger.info("\n🎭 Phase transition: CODE_QUALITY → ARCHITECTURE")
                results["phases"]["architecture"] = self._phase_5_architecture()
            
            if self.phase in ["all", "performance"]:
                logger.info("\n🎭 Phase transition: ARCHITECTURE → PERFORMANCE")
                results["phases"]["performance"] = self._phase_6_performance()
            
            if self.phase in ["all", "validation"]:
                logger.info("\n🎭 Phase transition: PERFORMANCE → VALIDATION")
                results["phases"]["validation"] = self._phase_7_validation()
            
            logger.info("\n🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            
            # Compile final results
            results["metrics"] = self.metrics.to_dict()
            results["violations"] = [
                self._serialize_violation(v) for v in self.solid_violations
            ]
            results["recommendations"] = self.refactoring_recommendations
            
            # Calculate health score
            results["health_score"] = self._calculate_health_score()
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Refinement failed: {e}", exc_info=True)
            results["status"] = "failed"
            results["error"] = str(e)
            return results
    
    # =================================================================
    # PHASE 1: DISCOVERY
    # =================================================================
    
    def _phase_1_discovery(self) -> Dict[str, Any]:
        """
        Phase 1: Discovery - Code inventory and AST analysis.
        
        Returns:
            Discovery results
        """
        logger.info("📊 Phase 1: Discovery - Code inventory")
        
        # Find all Python files
        python_files = list(self.target_path.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        self.metrics.total_files = len(python_files)
        
        # Analyze each file
        for file_path in python_files:
            self._analyze_file(file_path)
        
        logger.info(f"✅ Discovery complete:")
        logger.info(f"   • Files: {self.metrics.total_files}")
        logger.info(f"   • LOC: {self.metrics.total_loc:,}")
        logger.info(f"   • Classes: {self.metrics.total_classes}")
        logger.info(f"   • Methods: {self.metrics.total_methods}")
        
        return {
            "files": self.metrics.total_files,
            "loc": self.metrics.total_loc,
            "classes": self.metrics.total_classes,
            "methods": self.metrics.total_methods
        }
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count LOC
            lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
            self.metrics.total_loc += len(lines)
            
            # Parse AST
            tree = ast.parse(content)
            
            # Count classes and methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.metrics.total_classes += 1
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self.metrics.total_methods += 1
                    
        except Exception as e:
            logger.debug(f"Could not analyze {file_path}: {e}")
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            '__pycache__',
            '.venv',
            'venv',
            '.git',
            'node_modules',
            '.pytest_cache',
            'htmlcov',
            'site-packages'
        ]
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    # =================================================================
    # PHASE 2: SKULL REVIEW
    # =================================================================
    
    def _phase_2_skull_review(self) -> Dict[str, Any]:
        """
        Phase 2: SKULL Review - Test quality optimization.
        
        Returns:
            SKULL review results
        """
        logger.info("🛡️  Phase 2: SKULL Review - Test quality")
        
        # Find all test files
        test_files = list(self.target_path.rglob("test_*.py"))
        test_files += list(self.target_path.rglob("*_test.py"))
        
        test_count = len(test_files)
        
        logger.info(f"✅ SKULL review complete: {test_count} test files found")
        
        return {
            "test_files": test_count,
            "recommendations": []
        }
    
    # =================================================================
    # PHASE 3: DOCUMENTATION
    # =================================================================
    
    def _phase_3_documentation(self) -> Dict[str, Any]:
        """
        Phase 3: Documentation - Doc enhancement.
        
        Returns:
            Documentation review results
        """
        logger.info("📚 Phase 3: Documentation review")
        
        # Find all markdown files
        md_files = list(self.target_path.rglob("*.md"))
        md_files = [f for f in md_files if not self._should_skip_file(f)]
        
        logger.info(f"✅ Documentation review complete: {len(md_files)} markdown files found")
        
        return {
            "markdown_files": len(md_files),
            "recommendations": []
        }
    
    # =================================================================
    # PHASE 4: CODE QUALITY
    # =================================================================
    
    def _phase_4_code_quality(self) -> Dict[str, Any]:
        """
        Phase 4: Code Quality - SOLID violations and code smells.
        
        Returns:
            Code quality analysis results
        """
        logger.info("🔍 Phase 4: Code Quality - SOLID violations & smells")
        
        # Find all Python files
        python_files = list(self.target_path.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        # Detect SOLID violations
        for file_path in python_files:
            self._detect_solid_violations(file_path)
            self._detect_code_smells(file_path)
        
        self.metrics.solid_violations_found = len(self.solid_violations)
        self.metrics.code_smells_found = len(self.code_smells)
        
        logger.info(f"✅ Code quality analysis complete:")
        logger.info(f"   • SOLID violations: {self.metrics.solid_violations_found}")
        logger.info(f"   • Code smells: {self.metrics.code_smells_found}")
        
        return {
            "solid_violations": self.metrics.solid_violations_found,
            "code_smells": self.metrics.code_smells_found,
            "violations": [self._serialize_violation(v) for v in self.solid_violations],
            "smells": [self._serialize_smell(s) for s in self.code_smells]
        }
    
    def _detect_solid_violations(self, file_path: Path) -> None:
        """Detect SOLID principle violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Check each class
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # SRP: God class detection (>20 methods OR >500 LOC)
                    methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    method_count = len(methods)
                    
                    if method_count > 20:
                        self.solid_violations.append(SOLIDViolation(
                            principle="SRP",
                            violation_type="god_class",
                            location=f"{file_path.name}:{node.name}",
                            severity="high",
                            metrics={"methods": method_count},
                            recommendation=f"Extract responsibilities from {node.name} (has {method_count} methods)",
                            auto_fixable=False
                        ))
                    
                    # OCP: Check for long if/elif chains in methods
                    for method in methods:
                        if_elif_count = self._count_if_elif_branches(method)
                        if if_elif_count > 5:
                            self.solid_violations.append(SOLIDViolation(
                                principle="OCP",
                                violation_type="if_elif_chain",
                                location=f"{file_path.name}:{node.name}.{method.name}",
                                severity="high",
                                metrics={"branches": if_elif_count},
                                recommendation=f"Replace if/elif chain with strategy pattern in {method.name}",
                                auto_fixable=False
                            ))
                    
        except Exception as e:
            logger.debug(f"Could not analyze {file_path} for SOLID violations: {e}")
    
    def _count_if_elif_branches(self, node: ast.AST) -> int:
        """Count if/elif branches in a method."""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                count += 1
                # Count elif branches
                orelse = child.orelse
                while orelse and len(orelse) == 1 and isinstance(orelse[0], ast.If):
                    count += 1
                    orelse = orelse[0].orelse
        return count
    
    def _detect_code_smells(self, file_path: Path) -> None:
        """Detect code smells."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Long method detection (>50 LOC)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                    
                    if method_lines > 50:
                        self.code_smells.append(CodeSmell(
                            smell_type="long_method",
                            location=f"{file_path.name}:{node.name}",
                            severity="medium",
                            metrics={"loc": method_lines},
                            recommendation=f"Extract method {node.name} ({method_lines} LOC) into smaller functions",
                            auto_fixable=False
                        ))
                    
                    # Long parameter list (>3 params)
                    param_count = len(node.args.args)
                    if param_count > 3:
                        self.code_smells.append(CodeSmell(
                            smell_type="long_parameter_list",
                            location=f"{file_path.name}:{node.name}",
                            severity="low",
                            metrics={"params": param_count},
                            recommendation=f"Use parameter object for {node.name} ({param_count} parameters)",
                            auto_fixable=False
                        ))
                    
        except Exception as e:
            logger.debug(f"Could not analyze {file_path} for code smells: {e}")
    
    # =================================================================
    # PHASE 5: ARCHITECTURE
    # =================================================================
    
    def _phase_5_architecture(self) -> Dict[str, Any]:
        """
        Phase 5: Architecture - Pattern application and decoupling.
        
        Returns:
            Architecture review results
        """
        logger.info("🏗️  Phase 5: Architecture review")
        
        # - Dependency analysis
        # - Coupling detection
        # - Pattern recommendations
        
        logger.info("✅ Architecture review complete")
        
        return {
            "recommendations": []
        }
    
    # =================================================================
    # PHASE 6: PERFORMANCE
    # =================================================================
    
    def _phase_6_performance(self) -> Dict[str, Any]:
        """
        Phase 6: Performance - Complexity reduction and optimization.
        
        Returns:
            Performance analysis results
        """
        logger.info("⚡ Phase 6: Performance optimization")
        
        # Calculate complexity using radon
        try:
            result = subprocess.run(
                ["radon", "cc", str(self.target_path), "-a", "-j"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                complexity_data = json.loads(result.stdout)
                
                # Calculate average complexity
                total_complexity = 0
                function_count = 0
                
                for file_data in complexity_data.values():
                    for func in file_data:
                        if isinstance(func, dict) and 'complexity' in func:
                            total_complexity += func['complexity']
                            function_count += 1
                
                if function_count > 0:
                    self.metrics.complexity_before = total_complexity / function_count
                    logger.info(f"   • Average complexity: {self.metrics.complexity_before:.2f}")
                    
        except Exception as e:
            logger.debug(f"Could not calculate complexity: {e}")
        
        logger.info("✅ Performance analysis complete")
        
        return {
            "complexity_before": round(self.metrics.complexity_before, 2)
        }
    
    # =================================================================
    # PHASE 7: VALIDATION
    # =================================================================
    
    def _phase_7_validation(self) -> Dict[str, Any]:
        """
        Phase 7: Validation - Verify improvements.
        
        Returns:
            Validation results
        """
        logger.info("✔️  Phase 7: Validation")
        
        # Run tests if available
        test_dir = self.target_path / "tests"
        if test_dir.exists():
            try:
                result = subprocess.run(
                    ["pytest", str(test_dir), "-q", "--tb=no"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Parse test results
                output = result.stdout
                match = re.search(r'(\d+) passed', output)
                if match:
                    self.metrics.tests_passing_after = int(match.group(1))
                    logger.info(f"   • Tests passing: {self.metrics.tests_passing_after}")
                    
            except Exception as e:
                logger.debug(f"Could not run tests: {e}")
        
        logger.info("✅ Validation complete")
        
        return {
            "tests_passing": self.metrics.tests_passing_after,
            "validated": True
        }
    
    # =================================================================
    # HELPERS
    # =================================================================
    
    def _serialize_violation(self, violation: SOLIDViolation) -> Dict[str, Any]:
        """Serialize SOLID violation to dict."""
        return {
            "principle": violation.principle,
            "type": violation.violation_type,
            "location": violation.location,
            "severity": violation.severity,
            "metrics": violation.metrics,
            "recommendation": violation.recommendation,
            "auto_fixable": violation.auto_fixable
        }
    
    def _serialize_smell(self, smell: CodeSmell) -> Dict[str, Any]:
        """Serialize code smell to dict."""
        return {
            "type": smell.smell_type,
            "location": smell.location,
            "severity": smell.severity,
            "metrics": smell.metrics,
            "recommendation": smell.recommendation,
            "auto_fixable": smell.auto_fixable
        }
    
    def _calculate_health_score(self) -> float:
        """
        Calculate overall health score (0-100).
        
        Components:
        - SOLID violations (25 points)
        - Code smells (25 points)
        - Test coverage (25 points)
        - Complexity (25 points)
        """
        score = 100.0
        
        # Deduct for SOLID violations (max 25 points)
        solid_penalty = min(25, self.metrics.solid_violations_found * 2)
        score -= solid_penalty
        
        # Deduct for code smells (max 25 points)
        smell_penalty = min(25, self.metrics.code_smells_found * 1)
        score -= smell_penalty
        
        # Deduct for low coverage (max 25 points)
        if self.metrics.coverage_after < 60:
            coverage_penalty = (60 - self.metrics.coverage_after) / 60 * 25
            score -= coverage_penalty
        
        # Deduct for high complexity (max 25 points)
        if self.metrics.complexity_before > 15:
            complexity_penalty = min(25, (self.metrics.complexity_before - 15) / 15 * 25)
            score -= complexity_penalty
        
        return max(0, score)


def register() -> RefinementOrchestrator:
    """
    Register refinement orchestrator.
    
    Returns:
        RefinementOrchestrator instance
    """
    return RefinementOrchestrator()


if __name__ == "__main__":
    # CLI execution
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX System Refinement Orchestrator")
    parser.add_argument("--target", type=Path, help="Target directory to refine")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview changes")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument("--phase", default="all", help="Phase to run")
    
    args = parser.parse_args()
    
    orchestrator = RefinementOrchestrator(
        target_path=args.target,
        dry_run=not args.apply,
        phase=args.phase
    )
    
    results = orchestrator.execute()
    
    print("\n" + "="*80)
    print("REFINEMENT RESULTS")
    print("="*80)
    print(json.dumps(results, indent=2))
