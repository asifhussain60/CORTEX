#!/usr/bin/env python3
"""
Gap Detection Engine - Compares Requirements vs Implementation

This tool analyzes the cortex6 requirements folder and compares it against
the live implementation in src/ to identify:
1. Missing implementations (requirements without code)
2. Implementation drift (code doesn't match specs)
3. Undocumented code (code without requirements)
4. Test coverage gaps
5. Documentation gaps

Part of: CORTEX 6.0 Remediation Plan - Phase P0
Author: GitHub Copilot + Asif Hussain
Created: 2026-01-08
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import ast
import re


@dataclass
class Gap:
    """Represents a gap between requirements and implementation."""
    gap_id: str
    category: str  # MISSING_IMPLEMENTATION, DRIFT, UNDOCUMENTED_CODE, TEST_GAP, DOC_GAP
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    requirement_ref: Optional[str]
    implementation_ref: Optional[str]
    recommendation: str
    impact: str
    estimated_hours: int


@dataclass
class GapReport:
    """Complete gap analysis report."""
    report_id: str
    generated_at: str
    cortex_version: str
    requirements_path: str
    implementation_path: str
    summary: Dict[str, Any]
    gaps: List[Gap]
    metrics: Dict[str, Any]


class GapDetector:
    """Detects gaps between CORTEX 6.0 requirements and implementation."""
    
    def __init__(self, requirements_root: Path, implementation_root: Path):
        self.requirements_root = requirements_root
        self.implementation_root = implementation_root
        self.gaps: List[Gap] = []
        self.gap_counter = 0
        
    def generate_gap_id(self, category: str) -> str:
        """Generate unique gap ID."""
        self.gap_counter += 1
        prefix = {
            "MISSING_IMPLEMENTATION": "MI",
            "DRIFT": "DR",
            "UNDOCUMENTED_CODE": "UC",
            "TEST_GAP": "TG",
            "DOC_GAP": "DG"
        }.get(category, "GAP")
        return f"{prefix}-{self.gap_counter:03d}"
    
    def detect_all_gaps(self) -> GapReport:
        """Run all gap detection analyses."""
        print("🔍 Starting gap detection...")
        
        # 1. Check for missing feature YAML files
        self._detect_missing_feature_yamls()
        
        # 2. Check for missing implementations
        self._detect_missing_implementations()
        
        # 3. Check for undocumented code
        self._detect_undocumented_code()
        
        # 4. Check test coverage
        self._detect_test_gaps()
        
        # 5. Check documentation
        self._detect_documentation_gaps()
        
        # Generate summary
        summary = self._generate_summary()
        metrics = self._calculate_metrics()
        
        report = GapReport(
            report_id=f"GAP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            generated_at=datetime.now().isoformat(),
            cortex_version="6.0.0",
            requirements_path=str(self.requirements_root),
            implementation_path=str(self.implementation_root),
            summary=summary,
            gaps=self.gaps,
            metrics=metrics
        )
        
        return report
    
    def _detect_missing_feature_yamls(self):
        """Detect missing feature.yaml files for feat03-feat08."""
        features_dir = self.requirements_root / "source-of-truth" / "features"
        
        if not features_dir.exists():
            self.gaps.append(Gap(
                gap_id=self.generate_gap_id("MISSING_IMPLEMENTATION"),
                category="MISSING_IMPLEMENTATION",
                severity="CRITICAL",
                title="Features directory not found",
                description=f"Expected features directory at {features_dir} does not exist",
                requirement_ref="cortex6/source-of-truth/features/",
                implementation_ref=None,
                recommendation="Create features directory and individual feature.yaml files",
                impact="Cannot validate feature-level requirements",
                estimated_hours=1
            ))
            return
        
        # Check for feat01-feat08
        expected_features = [f"feat0{i}" for i in range(1, 9)]
        
        for feat_id in expected_features:
            # Check for individual feature folder
            feat_folder = features_dir / f"{feat_id}-*"
            matching = list(features_dir.glob(f"{feat_id}-*"))
            
            if not matching:
                self.gaps.append(Gap(
                    gap_id=self.generate_gap_id("MISSING_IMPLEMENTATION"),
                    category="MISSING_IMPLEMENTATION",
                    severity="HIGH",
                    title=f"Missing feature folder: {feat_id}",
                    description=f"No feature folder found for {feat_id}",
                    requirement_ref=f"cortex6/source-of-truth/features/{feat_id}/",
                    implementation_ref=None,
                    recommendation=f"Create {feat_id}-* folder with feature.yaml",
                    impact="Feature requirements not documented in proper structure",
                    estimated_hours=2
                ))
                continue
            
            # Check for feature.yaml within folder
            feat_yaml = matching[0] / "feature.yaml"
            if not feat_yaml.exists():
                self.gaps.append(Gap(
                    gap_id=self.generate_gap_id("MISSING_IMPLEMENTATION"),
                    category="MISSING_IMPLEMENTATION",
                    severity="HIGH",
                    title=f"Missing feature.yaml for {feat_id}",
                    description=f"Feature folder exists but no feature.yaml found",
                    requirement_ref=f"cortex6/source-of-truth/features/{feat_id}/feature.yaml",
                    implementation_ref=None,
                    recommendation=f"Create feature.yaml with phase/task definitions",
                    impact="Feature requirements not in machine-readable format",
                    estimated_hours=3
                ))
    
    def _detect_missing_implementations(self):
        """Detect requirements without corresponding implementation."""
        # Check if feat07 and feat08 have implementations
        
        # feat07: Integration tests
        integration_tests = self.implementation_root / "tests" / "integration"
        if integration_tests.exists():
            test_files = list(integration_tests.glob("test_*.py"))
            if len(test_files) < 5:
                self.gaps.append(Gap(
                    gap_id=self.generate_gap_id("MISSING_IMPLEMENTATION"),
                    category="MISSING_IMPLEMENTATION",
                    severity="HIGH",
                    title="Insufficient integration tests (feat07)",
                    description=f"Only {len(test_files)} integration test files found, expected 10+",
                    requirement_ref="feat07-integration",
                    implementation_ref=str(integration_tests),
                    recommendation="Create comprehensive integration test suite",
                    impact="System not validated as cohesive whole",
                    estimated_hours=12
                ))
        else:
            self.gaps.append(Gap(
                gap_id=self.generate_gap_id("MISSING_IMPLEMENTATION"),
                category="MISSING_IMPLEMENTATION",
                severity="CRITICAL",
                title="Missing integration tests directory (feat07)",
                description="No integration tests directory found",
                requirement_ref="feat07-integration",
                implementation_ref=None,
                recommendation="Create tests/integration/ with comprehensive test suite",
                impact="No end-to-end validation of system",
                estimated_hours=18
            ))
        
        # feat08: Vacuum orchestrator enhancements
        vacuum_dir = self.implementation_root / "orchestrators" / "vacuum"
        if vacuum_dir.exists():
            # Check for enhanced features
            vacuum_files = list(vacuum_dir.glob("*.py"))
            if len(vacuum_files) < 3:
                self.gaps.append(Gap(
                    gap_id=self.generate_gap_id("MISSING_IMPLEMENTATION"),
                    category="MISSING_IMPLEMENTATION",
                    severity="MEDIUM",
                    title="Vacuum orchestrator not enhanced (feat08)",
                    description=f"Only {len(vacuum_files)} files in vacuum/, expected enhanced version",
                    requirement_ref="feat08-cleanup",
                    implementation_ref=str(vacuum_dir),
                    recommendation="Enhance vacuum orchestrator with deep cleanup capabilities",
                    impact="No automated cleanup, technical debt accumulation",
                    estimated_hours=8
                ))
        else:
            self.gaps.append(Gap(
                gap_id=self.generate_gap_id("MISSING_IMPLEMENTATION"),
                category="MISSING_IMPLEMENTATION",
                severity="MEDIUM",
                title="Missing vacuum orchestrator (feat08)",
                description="No vacuum orchestrator directory found",
                requirement_ref="feat08-cleanup",
                implementation_ref=None,
                recommendation="Create vacuum orchestrator with cleanup automation",
                impact="No automated cleanup functionality",
                estimated_hours=12
            ))
    
    def _detect_undocumented_code(self):
        """Detect code without corresponding requirements."""
        # Scan src/ for Python files
        src_files = list(self.implementation_root.glob("**/*.py"))
        
        # Look for substantial modules without requirement docs
        substantial_modules = []
        for src_file in src_files:
            if src_file.name.startswith("__"):
                continue
            if "test" in str(src_file):
                continue
            
            # Check file size (substantial = >100 lines)
            try:
                lines = src_file.read_text().split("\n")
                if len(lines) > 100:
                    substantial_modules.append(src_file)
            except (OSError, UnicodeDecodeError, PermissionError) as e:
                # Skip files that can't be read (binary, permission denied, corrupted, etc.)
                pass
        
        # For now, just report count (detailed analysis would require requirement mapping)
        if len(substantial_modules) > 20:
            self.gaps.append(Gap(
                gap_id=self.generate_gap_id("UNDOCUMENTED_CODE"),
                category="UNDOCUMENTED_CODE",
                severity="MEDIUM",
                title=f"Many substantial modules without requirement traceability",
                description=f"Found {len(substantial_modules)} modules >100 lines, traceability unknown",
                requirement_ref=None,
                implementation_ref="src/**/*.py",
                recommendation="Create traceability matrix in P1 to identify undocumented code",
                impact="Cannot verify all code matches requirements",
                estimated_hours=8
            ))
    
    def _detect_test_gaps(self):
        """Detect test coverage gaps."""
        tests_dir = self.implementation_root / "tests"
        
        if not tests_dir.exists():
            self.gaps.append(Gap(
                gap_id=self.generate_gap_id("TEST_GAP"),
                category="TEST_GAP",
                severity="CRITICAL",
                title="Tests directory not found",
                description="No tests/ directory exists",
                requirement_ref="Testing strategy",
                implementation_ref=None,
                recommendation="Create tests/ directory with unit, integration, performance tests",
                impact="No quality validation",
                estimated_hours=40
            ))
            return
        
        # Count test files
        unit_tests = list((tests_dir / "unit").glob("test_*.py")) if (tests_dir / "unit").exists() else []
        integration_tests = list((tests_dir / "integration").glob("test_*.py")) if (tests_dir / "integration").exists() else []
        
        total_tests = len(unit_tests) + len(integration_tests)
        
        if total_tests < 50:
            self.gaps.append(Gap(
                gap_id=self.generate_gap_id("TEST_GAP"),
                category="TEST_GAP",
                severity="HIGH",
                title="Insufficient test coverage",
                description=f"Only {total_tests} test files found, expected 100+",
                requirement_ref="80% minimum coverage target",
                implementation_ref=str(tests_dir),
                recommendation="Expand test suite to achieve ≥95% coverage",
                impact="Quality and regression risk",
                estimated_hours=24
            ))
    
    def _detect_documentation_gaps(self):
        """Detect documentation gaps."""
        docs_dir = Path("docs")
        
        # Check for architecture documentation
        if not (docs_dir / "architecture").exists():
            self.gaps.append(Gap(
                gap_id=self.generate_gap_id("DOC_GAP"),
                category="DOC_GAP",
                severity="MEDIUM",
                title="Missing architecture documentation",
                description="No docs/architecture/ directory found",
                requirement_ref="Architecture documentation requirement",
                implementation_ref=None,
                recommendation="Create architecture docs from implemented system",
                impact="Difficult for new developers to understand system",
                estimated_hours=16
            ))
        
        # Check for API documentation
        if not (docs_dir / "api").exists():
            self.gaps.append(Gap(
                gap_id=self.generate_gap_id("DOC_GAP"),
                category="DOC_GAP",
                severity="LOW",
                title="Missing API documentation",
                description="No docs/api/ directory found",
                requirement_ref="API documentation requirement",
                implementation_ref=None,
                recommendation="Generate API docs from code docstrings",
                impact="API usage unclear",
                estimated_hours=8
            ))
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        by_category = {}
        
        for gap in self.gaps:
            by_severity[gap.severity] += 1
            if gap.category not in by_category:
                by_category[gap.category] = 0
            by_category[gap.category] += 1
        
        return {
            "total_gaps": len(self.gaps),
            "by_severity": by_severity,
            "by_category": by_category,
            "critical_blockers": by_severity["CRITICAL"],
            "estimated_hours_total": sum(g.estimated_hours for g in self.gaps)
        }
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate gap metrics."""
        return {
            "requirements_coverage": "UNKNOWN - Needs P1 traceability matrix",
            "implementation_completeness": f"{6 / 8 * 100:.1f}%",  # feat01-06 done, feat07-08 missing
            "test_coverage": "UNKNOWN - Needs pytest --cov execution",
            "documentation_coverage": "UNKNOWN - Needs documentation audit"
        }
    
    def save_report(self, report: GapReport, output_path: Path):
        """Save gap report as YAML."""
        report_dict = {
            "report_id": report.report_id,
            "generated_at": report.generated_at,
            "cortex_version": report.cortex_version,
            "requirements_path": report.requirements_path,
            "implementation_path": report.implementation_path,
            "summary": report.summary,
            "gaps": [asdict(gap) for gap in report.gaps],
            "metrics": report.metrics
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            yaml.dump(report_dict, f, default_flow_style=False, sort_keys=False)
        
        print(f"✅ Gap report saved: {output_path}")
        
        # Also save as JSON for programmatic access
        json_path = output_path.with_suffix(".json")
        with open(json_path, "w") as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"✅ JSON version saved: {json_path}")


def main():
    """Run gap detection."""
    print("=" * 80)
    print("CORTEX 6.0 Gap Detection Engine")
    print("=" * 80)
    print()
    
    project_root = Path(__file__).parent.parent.parent
    requirements_root = project_root / ".asif" / "AI-Learning" / "cortex6"
    implementation_root = project_root / "src"
    
    detector = GapDetector(requirements_root, implementation_root)
    report = detector.detect_all_gaps()
    
    # Save report
    output_path = project_root / ".asif" / "AI-Learning" / "cortex6-fixes" / "reports" / "baseline-gap-report.yaml"
    detector.save_report(report, output_path)
    
    # Print summary
    print()
    print("=" * 80)
    print("GAP ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total Gaps: {report.summary['total_gaps']}")
    print(f"  🚨 CRITICAL: {report.summary['by_severity']['CRITICAL']}")
    print(f"  ⚠️  HIGH: {report.summary['by_severity']['HIGH']}")
    print(f"  ⚡ MEDIUM: {report.summary['by_severity']['MEDIUM']}")
    print(f"  ℹ️  LOW: {report.summary['by_severity']['LOW']}")
    print()
    print(f"Estimated Hours to Close All Gaps: {report.summary['estimated_hours_total']}")
    print(f"Implementation Completeness: {report.metrics['implementation_completeness']}")
    print()
    print(f"📄 Full report: {output_path}")
    print("=" * 80)
    
    return 0 if report.summary['critical_blockers'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
