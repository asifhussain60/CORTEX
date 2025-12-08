#!/usr/bin/env python3
"""
TDD Mastery Validation Test - Cortex-Clean Sample Application

Tests the new TDD_TEST_FILE_VALIDATION and TDD_EMPTY_TEST_DETECTION rules
against the Cortex-Clean application to verify they catch all gaps identified
in CODE-QUALITY-REVIEW.md.

Expected Results:
- TDD_TEST_FILE_VALIDATION: BLOCKED (missing 15+ test files)
- TDD_EMPTY_TEST_DETECTION: WARNING (UnitTest1.cs is empty placeholder)
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class TestGap:
    production_file: str
    expected_test_file: str
    layer: str
    exists: bool


@dataclass
class TestQualityIssue:
    test_file: str
    issue_type: str
    details: str
    line_number: int = 0


class CortexCleanValidator:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.backend_path = self.base_path / "backend"
        self.test_gaps: List[TestGap] = []
        self.quality_issues: List[TestQualityIssue] = []
        
        # Layer-specific thresholds from TDD_TEST_FILE_VALIDATION
        self.coverage_thresholds = {
            "Domain": 90,
            "Application": 85,
            "Infrastructure": 70,
            "API": 80
        }
        
        # File patterns to scan
        self.production_patterns = {
            "Domain": ["*Entity.cs", "*Service.cs", "*Exception.cs"],
            "Application": ["*Handlers.cs", "*Validators.cs", "*Commands.cs", "*Queries.cs"],
            "Infrastructure": ["*Repository.cs", "*DbContext.cs"],
            "API": ["*Controller.cs", "*Middleware.cs"]
        }
    
    def validate_test_file_existence(self) -> Dict[str, any]:
        """
        Rule: TDD_TEST_FILE_VALIDATION
        Validates all production code has corresponding test files.
        """
        print("\n" + "="*80)
        print("🔍 RULE: TDD_TEST_FILE_VALIDATION")
        print("="*80)
        
        results = {}
        
        for layer, patterns in self.production_patterns.items():
            layer_path = self.backend_path / f"Cortex.Clean.{layer}"
            if not layer_path.exists():
                continue
            
            production_files = []
            for pattern in patterns:
                production_files.extend(layer_path.rglob(pattern))
            
            # Exclude obj/ directories and Class1.cs
            production_files = [
                f for f in production_files 
                if "obj" not in str(f) and "Class1.cs" not in str(f)
            ]
            
            layer_gaps = []
            for prod_file in production_files:
                test_file = self._get_expected_test_path(prod_file, layer)
                exists = test_file.exists()
                
                gap = TestGap(
                    production_file=str(prod_file.relative_to(self.backend_path)),
                    expected_test_file=str(test_file.relative_to(self.backend_path)),
                    layer=layer,
                    exists=exists
                )
                
                if not exists:
                    layer_gaps.append(gap)
                    self.test_gaps.append(gap)
            
            results[layer] = {
                "total_files": len(production_files),
                "missing_tests": len(layer_gaps),
                "coverage": 0 if len(production_files) == 0 else 
                           int(((len(production_files) - len(layer_gaps)) / len(production_files)) * 100)
            }
        
        return results
    
    def _get_expected_test_path(self, prod_file: Path, layer: str) -> Path:
        """
        Generates expected test file path based on production file.
        Pattern: Tests/{Layer}/{FileName}Tests.cs
        """
        file_name = prod_file.stem
        test_name = f"{file_name}Tests.cs"
        
        # Determine test subdirectory
        if "Handler" in file_name:
            subdir = "Handlers"
        elif "Validator" in file_name:
            subdir = "Validators"
        elif "Repository" in file_name:
            subdir = "Repositories"
        elif "Controller" in file_name:
            subdir = "Controllers"
        elif layer == "Domain":
            subdir = ""
        else:
            subdir = ""
        
        test_path = self.backend_path / "Cortex.Clean.Tests" / layer
        if subdir:
            test_path = test_path / subdir
        
        return test_path / test_name
    
    def detect_empty_placeholder_tests(self) -> List[TestQualityIssue]:
        """
        Rule: TDD_EMPTY_TEST_DETECTION
        Detects low-quality placeholder tests.
        """
        print("\n" + "="*80)
        print("🔍 RULE: TDD_EMPTY_TEST_DETECTION")
        print("="*80)
        
        test_dir = self.backend_path / "Cortex.Clean.Tests"
        test_files = list(test_dir.rglob("*.cs"))
        
        # Exclude obj/ directories
        test_files = [f for f in test_files if "obj" not in str(f)]
        
        for test_file in test_files:
            self._scan_test_file(test_file)
        
        return self.quality_issues
    
    def _scan_test_file(self, test_file: Path):
        """Scan a single test file for quality issues."""
        try:
            content = test_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Pattern 1: Empty test methods
            empty_test_pattern = r'\[Fact\]\s*public\s+void\s+(\w+)\(\s*\)\s*\{\s*\}'
            for match in re.finditer(empty_test_pattern, content, re.MULTILINE | re.DOTALL):
                self.quality_issues.append(TestQualityIssue(
                    test_file=str(test_file.relative_to(self.backend_path)),
                    issue_type="Empty Test Method",
                    details=f"Method '{match.group(1)}' has no implementation"
                ))
            
            # Pattern 2: Placeholder test names
            placeholder_pattern = r'public\s+void\s+(Test\d+|UnitTest\d+|TestMethod\d+)\('
            for i, line in enumerate(lines, 1):
                if re.search(placeholder_pattern, line):
                    self.quality_issues.append(TestQualityIssue(
                        test_file=str(test_file.relative_to(self.backend_path)),
                        issue_type="Placeholder Test Name",
                        details=f"Generic test name detected on line {i}",
                        line_number=i
                    ))
            
            # Pattern 3: Meaningless assertions
            meaningless_pattern = r'Assert\.True\(true\)'
            for i, line in enumerate(lines, 1):
                if re.search(meaningless_pattern, line):
                    self.quality_issues.append(TestQualityIssue(
                        test_file=str(test_file.relative_to(self.backend_path)),
                        issue_type="Meaningless Assertion",
                        details=f"Assert.True(true) always passes on line {i}",
                        line_number=i
                    ))
            
            # Pattern 4: Placeholder class names
            if "UnitTest1.cs" in str(test_file) or "TestClass1.cs" in str(test_file):
                self.quality_issues.append(TestQualityIssue(
                    test_file=str(test_file.relative_to(self.backend_path)),
                    issue_type="Placeholder File Name",
                    details="Generic test file name (UnitTest1.cs or TestClass1.cs)"
                ))
        
        except Exception as e:
            print(f"Error scanning {test_file}: {e}")
    
    def generate_report(self, coverage_results: Dict, quality_issues: List[TestQualityIssue]):
        """Generate validation report showing all detected issues."""
        print("\n" + "="*80)
        print("📊 VALIDATION REPORT - CORTEX-CLEAN")
        print("="*80)
        
        # Part 1: Test File Validation Results
        print("\n┌─ TDD_TEST_FILE_VALIDATION Results ─────────────────────────────────────┐")
        print("│ Severity: BLOCKED                                                      │")
        print("└────────────────────────────────────────────────────────────────────────┘\n")
        
        total_prod_files = sum(r["total_files"] for r in coverage_results.values())
        total_missing = sum(r["missing_tests"] for r in coverage_results.values())
        overall_coverage = int(((total_prod_files - total_missing) / total_prod_files * 100) 
                               if total_prod_files > 0 else 0)
        
        print("Layer Coverage Summary:")
        print("─" * 80)
        
        blocked = False
        for layer, results in coverage_results.items():
            threshold = self.coverage_thresholds[layer]
            coverage = results["coverage"]
            status = "✅" if coverage >= threshold else "❌"
            
            print(f"{status} {layer:20s} {coverage:3d}% (threshold: {threshold}%) - "
                  f"{results['missing_tests']:2d}/{results['total_files']:2d} tests missing")
            
            if coverage < threshold:
                blocked = True
        
        print("─" * 80)
        print(f"\nOverall Test Coverage: {overall_coverage}%")
        print(f"Production Files: {total_prod_files}")
        print(f"Missing Test Files: {total_missing}")
        
        if blocked:
            print("\n❌ BLOCKED: Cannot proceed - coverage below thresholds")
        else:
            print("\n✅ PASSED: All layers meet coverage thresholds")
        
        # Show missing test files
        if self.test_gaps:
            print("\n\nMissing Test Files (detailed):")
            print("─" * 80)
            
            by_layer = {}
            for gap in self.test_gaps:
                if gap.layer not in by_layer:
                    by_layer[gap.layer] = []
                by_layer[gap.layer].append(gap)
            
            for layer, gaps in sorted(by_layer.items()):
                print(f"\n{layer} Layer ({len(gaps)} missing):")
                for gap in gaps:
                    print(f"  Production: {gap.production_file}")
                    print(f"  Expected:   {gap.expected_test_file}")
                    print()
        
        # Part 2: Empty Test Detection Results
        print("\n┌─ TDD_EMPTY_TEST_DETECTION Results ─────────────────────────────────────┐")
        print("│ Severity: WARNING                                                      │")
        print("└────────────────────────────────────────────────────────────────────────┘\n")
        
        if quality_issues:
            print(f"Quality Issues Found: {len(quality_issues)}\n")
            
            by_type = {}
            for issue in quality_issues:
                if issue.issue_type not in by_type:
                    by_type[issue.issue_type] = []
                by_type[issue.issue_type].append(issue)
            
            for issue_type, issues in sorted(by_type.items()):
                print(f"⚠️  {issue_type} ({len(issues)} found):")
                for issue in issues:
                    print(f"   File: {issue.test_file}")
                    print(f"   Details: {issue.details}")
                    print()
            
            print("⚠️  WARNING: Test quality issues must be addressed")
        else:
            print("✅ No quality issues detected")
        
        # Part 3: Comparison with CODE-QUALITY-REVIEW.md findings
        print("\n" + "="*80)
        print("📋 VERIFICATION: Matches CODE-QUALITY-REVIEW.md Findings")
        print("="*80 + "\n")
        
        expected_gaps = {
            "Application Layer": [
                "CreateTaskCommandHandler.cs",
                "UpdateTaskCommandHandler.cs",
                "DeleteTaskCommandHandler.cs",
                "ToggleTaskCompletionCommandHandler.cs",
                "CreateTaskCommandValidator.cs",
                "UpdateTaskCommandValidator.cs"
            ],
            "Infrastructure Layer": [
                "TaskRepository.cs",
                "ApplicationDbContext.cs"
            ],
            "API Layer": [
                "TasksController.cs",
                "GlobalExceptionMiddleware.cs"
            ]
        }
        
        for layer, expected_files in expected_gaps.items():
            actual_gaps = [g for g in self.test_gaps if g.layer == layer.split()[0]]
            print(f"{layer}:")
            for expected in expected_files:
                found = any(expected in g.production_file for g in actual_gaps)
                status = "✅ DETECTED" if found else "❌ MISSED"
                print(f"  {status}: {expected}")
        
        print("\nEmpty Test Detection:")
        unittest1_found = any("UnitTest1.cs" in i.test_file for i in quality_issues)
        status = "✅ DETECTED" if unittest1_found else "❌ MISSED"
        print(f"  {status}: UnitTest1.cs (empty placeholder)")
        
        # Final Summary
        print("\n" + "="*80)
        print("✨ VALIDATION COMPLETE")
        print("="*80)
        
        print(f"\nRule TDD_TEST_FILE_VALIDATION: {'❌ BLOCKED' if blocked else '✅ PASSED'}")
        print(f"Rule TDD_EMPTY_TEST_DETECTION: {'⚠️  WARNING' if quality_issues else '✅ PASSED'}")
        
        print(f"\nTest Coverage Gap: Claimed 90%+ → Actual {overall_coverage}% "
              f"(Gap: {90 - overall_coverage}%)")
        
        if blocked or quality_issues:
            print("\n🎯 These rules would have PREVENTED the Cortex-Clean coverage gap!")
        
        return blocked, len(quality_issues) > 0


def main():
    # Path to Cortex-Clean
    cortex_clean_path = Path(__file__).parent / "cortex-sample-apps" / "Cortex-Clean"
    
    if not cortex_clean_path.exists():
        print(f"❌ Error: Cortex-Clean not found at {cortex_clean_path}")
        return
    
    print("🧪 TDD Mastery Validation - Testing New Rules on Cortex-Clean")
    print("="*80)
    print(f"Target: {cortex_clean_path}")
    print(f"Testing: TDD_TEST_FILE_VALIDATION + TDD_EMPTY_TEST_DETECTION")
    
    validator = CortexCleanValidator(str(cortex_clean_path))
    
    # Run validations
    coverage_results = validator.validate_test_file_existence()
    quality_issues = validator.detect_empty_placeholder_tests()
    
    # Generate report
    blocked, has_warnings = validator.generate_report(coverage_results, quality_issues)
    
    # Exit code
    if blocked:
        exit(1)  # BLOCKED
    elif has_warnings:
        exit(2)  # WARNING
    else:
        exit(0)  # PASSED


if __name__ == "__main__":
    main()
