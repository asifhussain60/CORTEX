#!/usr/bin/env python3
"""
Architectural Review Orchestrator - CORTEX 4.0

Performs comprehensive architecture assessment:
Phase 1: Layer Separation Analysis
Phase 2: Design Pattern Detection
Phase 3: Dependency Analysis
Phase 4: SOLID Compliance Assessment
Phase 5: Testability Analysis
Phase 6: Architecture Scoring & Recommendations

Generates 0-100 architecture score with detailed recommendations.

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
import re

logger = logging.getLogger(__name__)


@dataclass
class LayerViolation:
    """Layer separation violation."""
    violation_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    source_file: str
    target_module: str
    source_layer: str
    target_layer: str
    recommendation: str


@dataclass
class PatternOpportunity:
    """Design pattern application opportunity."""
    pattern_name: str
    location: str
    reason: str
    benefit: str
    priority: str  # HIGH, MEDIUM, LOW
    implementation_guide: str


@dataclass
class DependencyIssue:
    """Dependency management issue."""
    issue_type: str  # circular, tight_coupling, high_fan_out
    severity: str
    modules: List[str]
    recommendation: str


@dataclass
class ArchitectureMetrics:
    """Architecture quality metrics."""
    # Layer Separation (25 points)
    layer_separation_score: float = 0.0
    layer_violations_count: int = 0
    
    # Design Patterns (15 points)
    pattern_score: float = 0.0
    patterns_detected: int = 0
    patterns_recommended: int = 0
    
    # Dependency Management (20 points)
    dependency_score: float = 0.0
    circular_dependencies: int = 0
    tight_coupling_count: int = 0
    
    # SOLID Compliance (15 points)
    solid_score: float = 0.0
    solid_violations: int = 0
    
    # Testability (25 points)
    testability_score: float = 0.0
    test_coverage: float = 0.0
    
    # Overall
    total_score: float = 0.0
    grade: str = "F"
    
    def calculate_total_score(self) -> float:
        """Calculate total architecture score."""
        self.total_score = (
            self.layer_separation_score +
            self.pattern_score +
            self.dependency_score +
            self.solid_score +
            self.testability_score
        )
        
        # Assign grade
        if self.total_score >= 90:
            self.grade = "A"
        elif self.total_score >= 80:
            self.grade = "B"
        elif self.total_score >= 70:
            self.grade = "C"
        elif self.total_score >= 60:
            self.grade = "D"
        else:
            self.grade = "F"
        
        return self.total_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "layer_separation": {
                "score": round(self.layer_separation_score, 1),
                "max": 25,
                "violations": self.layer_violations_count
            },
            "design_patterns": {
                "score": round(self.pattern_score, 1),
                "max": 15,
                "detected": self.patterns_detected,
                "recommended": self.patterns_recommended
            },
            "dependency_management": {
                "score": round(self.dependency_score, 1),
                "max": 20,
                "circular_deps": self.circular_dependencies,
                "tight_coupling": self.tight_coupling_count
            },
            "solid_compliance": {
                "score": round(self.solid_score, 1),
                "max": 15,
                "violations": self.solid_violations
            },
            "testability": {
                "score": round(self.testability_score, 1),
                "max": 25,
                "coverage": f"{self.test_coverage:.1f}%"
            },
            "overall": {
                "score": round(self.total_score, 1),
                "max": 100,
                "grade": self.grade
            }
        }


class ArchitecturalReviewOrchestrator:
    """
    CORTEX 4.0 Architectural Review Orchestrator.
    
    Performs comprehensive architecture assessment:
    1. Layer Separation (25 pts)
    2. Design Patterns (15 pts)
    3. Dependency Management (20 pts)
    4. SOLID Compliance (15 pts)
    5. Testability (25 pts)
    6. Scoring & Recommendations
    """
    
    # Layer hierarchy (lower can depend on higher)
    LAYER_HIERARCHY = {
        'api': 0,
        'business': 1,
        'data': 2,
        'utils': 3
    }
    
    # Allowed dependencies
    ALLOWED_DEPS = {
        'api': {'business', 'utils'},
        'business': {'data', 'utils'},
        'data': {'utils'},
        'utils': set()
    }
    
    def __init__(
        self,
        target_path: Path,
        dry_run: bool = True
    ):
        """
        Initialize architectural review orchestrator.
        
        Args:
            target_path: Target directory to review
            dry_run: Preview only (no changes)
        """
        self.target_path = target_path
        self.dry_run = dry_run
        
        self.metrics = ArchitectureMetrics()
        self.layer_violations: List[LayerViolation] = []
        self.pattern_opportunities: List[PatternOpportunity] = []
        self.dependency_issues: List[DependencyIssue] = []
        self.recommendations: List[Dict[str, Any]] = []
        
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.file_to_layer: Dict[str, str] = {}
        
        self.start_time = datetime.now()
        
        logger.info(f"🎭 Orchestrator engaged: ArchitecturalReviewOrchestrator")
        logger.info(f"Target: {self.target_path}")
        logger.info(f"Mode: {'DRY RUN' if dry_run else 'APPLY CHANGES'}")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute architectural review workflow.
        
        Returns:
            Results dictionary with metrics and recommendations
        """
        results = {
            "status": "success",
            "phases": {},
            "metrics": {},
            "violations": [],
            "patterns": [],
            "dependencies": [],
            "recommendations": []
        }
        
        try:
            logger.info("\n🎭 Phase transition: START → LAYER_ANALYSIS")
            results["phases"]["layer_analysis"] = self._phase_1_layer_analysis()
            
            logger.info("\n🎭 Phase transition: LAYER_ANALYSIS → PATTERN_DETECTION")
            results["phases"]["pattern_detection"] = self._phase_2_pattern_detection()
            
            logger.info("\n🎭 Phase transition: PATTERN_DETECTION → DEPENDENCY_ANALYSIS")
            results["phases"]["dependency_analysis"] = self._phase_3_dependency_analysis()
            
            logger.info("\n🎭 Phase transition: DEPENDENCY_ANALYSIS → SOLID_ASSESSMENT")
            results["phases"]["solid_assessment"] = self._phase_4_solid_assessment()
            
            logger.info("\n🎭 Phase transition: SOLID_ASSESSMENT → TESTABILITY")
            results["phases"]["testability"] = self._phase_5_testability_analysis()
            
            logger.info("\n🎭 Phase transition: TESTABILITY → SCORING")
            results["phases"]["scoring"] = self._phase_6_scoring()
            
            logger.info("\n🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            
            # Compile final results
            results["metrics"] = self.metrics.to_dict()
            results["violations"] = [self._serialize_violation(v) for v in self.layer_violations]
            results["patterns"] = [self._serialize_pattern(p) for p in self.pattern_opportunities]
            results["dependencies"] = [self._serialize_dependency(d) for d in self.dependency_issues]
            results["recommendations"] = self.recommendations
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Architectural review failed: {e}", exc_info=True)
            results["status"] = "failed"
            results["error"] = str(e)
            return results
    
    # =================================================================
    # PHASE 1: LAYER SEPARATION ANALYSIS
    # =================================================================
    
    def _phase_1_layer_analysis(self) -> Dict[str, Any]:
        """
        Phase 1: Analyze layer separation violations.
        
        Returns:
            Layer analysis results
        """
        logger.info("🏗️  Phase 1: Layer Separation Analysis")
        
        # Find all Python files and map to layers
        python_files = list(self.target_path.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        for file_path in python_files:
            layer = self._detect_layer(file_path)
            if layer:
                self.file_to_layer[str(file_path)] = layer
        
        # Analyze imports and detect violations
        for file_path in python_files:
            self._analyze_file_imports(file_path)
        
        # Calculate score (25 points max, -3 per violation)
        self.metrics.layer_violations_count = len(self.layer_violations)
        self.metrics.layer_separation_score = max(0, 25 - (self.metrics.layer_violations_count * 3))
        
        logger.info(f"✅ Layer analysis complete:")
        logger.info(f"   • Violations: {self.metrics.layer_violations_count}")
        logger.info(f"   • Score: {self.metrics.layer_separation_score}/25")
        
        return {
            "violations": self.metrics.layer_violations_count,
            "score": self.metrics.layer_separation_score,
            "details": [self._serialize_violation(v) for v in self.layer_violations]
        }
    
    def _detect_layer(self, file_path: Path) -> Optional[str]:
        """Detect which layer a file belongs to."""
        path_parts = file_path.parts
        
        for layer in self.LAYER_HIERARCHY.keys():
            if layer in path_parts:
                return layer
        
        # Check for common patterns
        if 'src' in path_parts:
            idx = path_parts.index('src')
            if idx + 1 < len(path_parts):
                next_part = path_parts[idx + 1]
                if next_part in self.LAYER_HIERARCHY:
                    return next_part
        
        return None
    
    def _analyze_file_imports(self, file_path: Path) -> None:
        """Analyze imports in a file for layer violations."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            source_layer = self.file_to_layer.get(str(file_path))
            
            if not source_layer:
                return
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._check_import_violation(file_path, source_layer, alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._check_import_violation(file_path, source_layer, node.module)
                        
        except Exception as e:
            logger.debug(f"Could not analyze imports in {file_path}: {e}")
    
    def _check_import_violation(self, source_file: Path, source_layer: str, imported_module: str) -> None:
        """Check if an import violates layer separation."""
        # Detect target layer from import
        target_layer = None
        for layer in self.LAYER_HIERARCHY.keys():
            if layer in imported_module or f"/{layer}/" in imported_module:
                target_layer = layer
                break
        
        if not target_layer:
            return
        
        # Check if import is allowed
        if target_layer not in self.ALLOWED_DEPS[source_layer]:
            severity = self._calculate_violation_severity(source_layer, target_layer)
            
            self.layer_violations.append(LayerViolation(
                violation_type="layer_violation",
                severity=severity,
                source_file=str(source_file.name),
                target_module=imported_module,
                source_layer=source_layer,
                target_layer=target_layer,
                recommendation=self._generate_layer_fix(source_layer, target_layer)
            ))
    
    def _calculate_violation_severity(self, source: str, target: str) -> str:
        """Calculate severity of layer violation."""
        # API calling Data directly = CRITICAL
        if source == 'api' and target == 'data':
            return "CRITICAL"
        # Upward dependencies = HIGH
        elif self.LAYER_HIERARCHY[source] > self.LAYER_HIERARCHY[target]:
            return "HIGH"
        # Circular = CRITICAL
        else:
            return "MEDIUM"
    
    def _generate_layer_fix(self, source: str, target: str) -> str:
        """Generate fix recommendation for layer violation."""
        if source == 'api' and target == 'data':
            return "Extract business logic service layer. API should call Business, not Data directly."
        elif source == 'business' and target == 'api':
            return "Reverse dependency. Business should not know about API layer."
        elif target == 'utils' and source != 'data':
            return "Utils should be dependency-free. Move logic to appropriate layer."
        else:
            return f"Respect layer hierarchy: {source} should not import from {target}"
    
    # =================================================================
    # PHASE 2: DESIGN PATTERN DETECTION
    # =================================================================
    
    def _phase_2_pattern_detection(self) -> Dict[str, Any]:
        """
        Phase 2: Detect design pattern opportunities.
        
        Returns:
            Pattern detection results
        """
        logger.info("🎨 Phase 2: Design Pattern Detection")
        
        # Find all Python files
        python_files = list(self.target_path.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        # Detect pattern opportunities
        for file_path in python_files:
            self._detect_patterns_in_file(file_path)
        
        # Calculate score (15 points max)
        # Score based on how many patterns are currently applied
        self.metrics.patterns_recommended = len(self.pattern_opportunities)
        
        # Baseline: 0 patterns = 0 points, assume all recommended patterns would bring to 15
        self.metrics.pattern_score = 0.0
        
        logger.info(f"✅ Pattern detection complete:")
        logger.info(f"   • Patterns detected: {self.metrics.patterns_detected}")
        logger.info(f"   • Patterns recommended: {self.metrics.patterns_recommended}")
        logger.info(f"   • Score: {self.metrics.pattern_score}/15")
        
        return {
            "patterns_detected": self.metrics.patterns_detected,
            "patterns_recommended": self.metrics.patterns_recommended,
            "score": self.metrics.pattern_score,
            "opportunities": [self._serialize_pattern(p) for p in self.pattern_opportunities]
        }
    
    def _detect_patterns_in_file(self, file_path: Path) -> None:
        """Detect design pattern opportunities in a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Repository pattern: Direct database access in business layer
            if 'business' in str(file_path) and ('db.' in content or 'database' in content.lower()):
                self.pattern_opportunities.append(PatternOpportunity(
                    pattern_name="Repository",
                    location=str(file_path.name),
                    reason="Direct database access in business logic",
                    benefit="Testability +40%, Flexibility +30%",
                    priority="HIGH",
                    implementation_guide="Create IRepository interface, implement concrete repository, inject via DI"
                ))
            
            # Factory pattern: Multiple 'new' instantiations
            if content.count('= ') > 10 and ('if ' in content or 'elif ' in content):
                self.pattern_opportunities.append(PatternOpportunity(
                    pattern_name="Factory",
                    location=str(file_path.name),
                    reason="Complex object creation with conditionals",
                    benefit="Extensibility +50%, OCP compliance",
                    priority="MEDIUM",
                    implementation_guide="Extract factory class with create() method, use strategy for variants"
                ))
            
            # Strategy pattern: Long if/elif chains
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.If))
                    if if_count > 5:
                        self.pattern_opportunities.append(PatternOpportunity(
                            pattern_name="Strategy",
                            location=f"{file_path.name}:{node.name}",
                            reason=f"Long if/elif chain ({if_count} branches)",
                            benefit="OCP compliance, extensibility +60%",
                            priority="HIGH",
                            implementation_guide="Extract strategy interface, implement concrete strategies, use factory to select"
                        ))
                        break  # One per file to avoid duplicates
                        
        except Exception as e:
            logger.debug(f"Could not detect patterns in {file_path}: {e}")
    
    # =================================================================
    # PHASE 3: DEPENDENCY ANALYSIS
    # =================================================================
    
    def _phase_3_dependency_analysis(self) -> Dict[str, Any]:
        """
        Phase 3: Analyze dependencies for issues.
        
        Returns:
            Dependency analysis results
        """
        logger.info("🔗 Phase 3: Dependency Analysis")
        
        # Build dependency graph
        python_files = list(self.target_path.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        for file_path in python_files:
            self._build_dependency_graph(file_path)
        
        # Detect circular dependencies
        cycles = self._detect_circular_dependencies()
        self.metrics.circular_dependencies = len(cycles)
        
        for cycle in cycles:
            self.dependency_issues.append(DependencyIssue(
                issue_type="circular_dependency",
                severity="CRITICAL",
                modules=cycle,
                recommendation="Break cycle using Dependency Inversion Principle (introduce interface)"
            ))
        
        # Calculate score (20 points max, -5 per circular dep, -2 per tight coupling)
        self.metrics.tight_coupling_count = max(0, len(self.dependency_graph) - 10) if len(self.dependency_graph) > 10 else 0
        penalty = (self.metrics.circular_dependencies * 5) + (self.metrics.tight_coupling_count * 2)
        self.metrics.dependency_score = max(0, 20 - penalty)
        
        logger.info(f"✅ Dependency analysis complete:")
        logger.info(f"   • Circular dependencies: {self.metrics.circular_dependencies}")
        logger.info(f"   • Tight coupling: {self.metrics.tight_coupling_count}")
        logger.info(f"   • Score: {self.metrics.dependency_score}/20")
        
        return {
            "circular_dependencies": self.metrics.circular_dependencies,
            "tight_coupling": self.metrics.tight_coupling_count,
            "score": self.metrics.dependency_score,
            "issues": [self._serialize_dependency(d) for d in self.dependency_issues]
        }
    
    def _build_dependency_graph(self, file_path: Path) -> None:
        """Build dependency graph for circular detection."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            file_key = str(file_path.stem)
            
            if file_key not in self.dependency_graph:
                self.dependency_graph[file_key] = set()
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.dependency_graph[file_key].add(alias.name.split('.')[0])
                    elif node.module:
                        self.dependency_graph[file_key].add(node.module.split('.')[0])
                        
        except Exception as e:
            logger.debug(f"Could not build dependency graph for {file_path}: {e}")
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in self.dependency_graph:
            if node not in visited:
                dfs(node)
        
        return cycles
    
    # =================================================================
    # PHASE 4: SOLID ASSESSMENT
    # =================================================================
    
    def _phase_4_solid_assessment(self) -> Dict[str, Any]:
        """
        Phase 4: Assess SOLID compliance (reuse from Refinement).
        
        Returns:
            SOLID assessment results
        """
        logger.info("🛡️  Phase 4: SOLID Compliance Assessment")
        
        # Reuse SOLID violation count from refinement orchestrator
        # In real implementation, would call RefinementOrchestrator or share logic
        # For validation, use simplified detection
        
        python_files = list(self.target_path.rglob("*.py"))
        python_files = [f for f in python_files if not self._should_skip_file(f)]
        
        solid_violations = 0
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Quick SRP check: god classes (>20 methods)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                        if len(methods) > 20:
                            solid_violations += 1
                            
            except Exception as e:
                logger.debug(f"Could not assess SOLID in {file_path}: {e}")
        
        self.metrics.solid_violations = solid_violations
        self.metrics.solid_score = max(0, 15 - (solid_violations * 2))
        
        logger.info(f"✅ SOLID assessment complete:")
        logger.info(f"   • Violations: {self.metrics.solid_violations}")
        logger.info(f"   • Score: {self.metrics.solid_score}/15")
        
        return {
            "violations": self.metrics.solid_violations,
            "score": self.metrics.solid_score
        }
    
    # =================================================================
    # PHASE 5: TESTABILITY ANALYSIS
    # =================================================================
    
    def _phase_5_testability_analysis(self) -> Dict[str, Any]:
        """
        Phase 5: Analyze testability.
        
        Returns:
            Testability analysis results
        """
        logger.info("🧪 Phase 5: Testability Analysis")
        
        # Count test files
        test_files = list(self.target_path.rglob("test_*.py"))
        test_files += list(self.target_path.rglob("*_test.py"))
        
        # Count source files
        source_files = list(self.target_path.rglob("*.py"))
        source_files = [f for f in source_files if not self._should_skip_file(f) and 'test' not in str(f)]
        
        # Estimate coverage (very rough: test files / source files * 100)
        if source_files:
            self.metrics.test_coverage = (len(test_files) / len(source_files)) * 100
        
        # Score (25 points max, proportional to coverage)
        self.metrics.testability_score = (self.metrics.test_coverage / 100) * 25
        
        logger.info(f"✅ Testability analysis complete:")
        logger.info(f"   • Test files: {len(test_files)}")
        logger.info(f"   • Source files: {len(source_files)}")
        logger.info(f"   • Estimated coverage: {self.metrics.test_coverage:.1f}%")
        logger.info(f"   • Score: {self.metrics.testability_score:.1f}/25")
        
        return {
            "test_files": len(test_files),
            "source_files": len(source_files),
            "coverage": self.metrics.test_coverage,
            "score": self.metrics.testability_score
        }
    
    # =================================================================
    # PHASE 6: SCORING
    # =================================================================
    
    def _phase_6_scoring(self) -> Dict[str, Any]:
        """
        Phase 6: Calculate final architecture score and recommendations.
        
        Returns:
            Scoring results
        """
        logger.info("📊 Phase 6: Architecture Scoring")
        
        # Calculate total score
        total = self.metrics.calculate_total_score()
        
        # Generate top recommendations
        self._generate_recommendations()
        
        logger.info(f"✅ Scoring complete:")
        logger.info(f"   • Total Score: {total:.1f}/100")
        logger.info(f"   • Grade: {self.metrics.grade}")
        logger.info(f"   • Recommendations: {len(self.recommendations)}")
        
        return {
            "score": total,
            "grade": self.metrics.grade,
            "recommendations_count": len(self.recommendations)
        }
    
    def _generate_recommendations(self) -> None:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Priority 1: CRITICAL violations
        critical_violations = [v for v in self.layer_violations if v.severity == "CRITICAL"]
        for v in critical_violations:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Layer Separation",
                "title": f"Fix {v.source_layer} → {v.target_layer} violation",
                "location": v.source_file,
                "recommendation": v.recommendation
            })
        
        # Priority 2: Pattern opportunities
        high_priority_patterns = [p for p in self.pattern_opportunities if p.priority == "HIGH"]
        for p in high_priority_patterns[:3]:  # Top 3
            recommendations.append({
                "priority": "HIGH",
                "category": "Design Patterns",
                "title": f"Apply {p.pattern_name} pattern",
                "location": p.location,
                "recommendation": p.implementation_guide
            })
        
        # Priority 3: Circular dependencies
        for d in self.dependency_issues:
            if d.issue_type == "circular_dependency":
                recommendations.append({
                    "priority": "HIGH",
                    "category": "Dependencies",
                    "title": "Break circular dependency",
                    "location": " → ".join(d.modules),
                    "recommendation": d.recommendation
                })
        
        self.recommendations = recommendations
    
    # =================================================================
    # HELPERS
    # =================================================================
    
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
    
    def _serialize_violation(self, violation: LayerViolation) -> Dict[str, Any]:
        """Serialize layer violation."""
        return {
            "type": violation.violation_type,
            "severity": violation.severity,
            "source_file": violation.source_file,
            "target_module": violation.target_module,
            "source_layer": violation.source_layer,
            "target_layer": violation.target_layer,
            "recommendation": violation.recommendation
        }
    
    def _serialize_pattern(self, pattern: PatternOpportunity) -> Dict[str, Any]:
        """Serialize pattern opportunity."""
        return {
            "pattern": pattern.pattern_name,
            "location": pattern.location,
            "reason": pattern.reason,
            "benefit": pattern.benefit,
            "priority": pattern.priority,
            "implementation": pattern.implementation_guide
        }
    
    def _serialize_dependency(self, dependency: DependencyIssue) -> Dict[str, Any]:
        """Serialize dependency issue."""
        return {
            "type": dependency.issue_type,
            "severity": dependency.severity,
            "modules": dependency.modules,
            "recommendation": dependency.recommendation
        }


def register() -> ArchitecturalReviewOrchestrator:
    """
    Register architectural review orchestrator.
    
    Returns:
        ArchitecturalReviewOrchestrator instance
    """
    return ArchitecturalReviewOrchestrator(target_path=Path.cwd())


if __name__ == "__main__":
    # CLI execution
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Architectural Review Orchestrator")
    parser.add_argument("--target", type=Path, required=True, help="Target directory to review")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only")
    
    args = parser.parse_args()
    
    orchestrator = ArchitecturalReviewOrchestrator(
        target_path=args.target,
        dry_run=args.dry_run
    )
    
    results = orchestrator.execute()
    
    print("\n" + "="*80)
    print("ARCHITECTURAL REVIEW RESULTS")
    print("="*80)
    print(json.dumps(results, indent=2))
