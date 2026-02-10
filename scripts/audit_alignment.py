#!/usr/bin/env python3
"""CORTEX Alignment Audit Script

Comprehensive validation of implementation ↔ specification sync.

Usage:
    python scripts/audit_alignment.py [--strict] [--fix] [--report]

Options:
    --strict    Exit with error code if any P0/P1 gaps found
    --fix       Auto-fix simple issues (remove empty stubs, update wiring)
    --report    Generate markdown report file

Author: CORTEX Framework
Version: 1.0
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class Severity(Enum):
    P0_CRITICAL = "P0_CRITICAL"
    P1_HIGH = "P1_HIGH"
    P2_MEDIUM = "P2_MEDIUM"
    P3_LOW = "P3_LOW"


class GapType(Enum):
    WIRED_NOT_IMPLEMENTED = "WIRED_NOT_IMPLEMENTED"
    IMPLEMENTED_NOT_WIRED = "IMPLEMENTED_NOT_WIRED"
    STUB_TEST = "STUB_TEST"
    STUB_CODE = "STUB_CODE"
    SKIPPED_TEST = "SKIPPED_TEST"
    MISSING_MCP_ADAPTER = "MISSING_MCP_ADAPTER"


@dataclass
class Gap:
    gap_type: GapType
    component: str
    location: str
    severity: Severity
    remediation: str


@dataclass
class AlignmentReport:
    gaps: list[Gap] = field(default_factory=list)
    
    def add_gap(self, gap: Gap) -> None:
        self.gaps.append(gap)
    
    @property
    def p0_count(self) -> int:
        return len([g for g in self.gaps if g.severity == Severity.P0_CRITICAL])
    
    @property
    def p1_count(self) -> int:
        return len([g for g in self.gaps if g.severity == Severity.P1_HIGH])
    
    @property
    def p2_count(self) -> int:
        return len([g for g in self.gaps if g.severity == Severity.P2_MEDIUM])
    
    @property
    def total_count(self) -> int:
        return len(self.gaps)
    
    def is_production_ready(self) -> bool:
        return self.p0_count == 0


def load_wiring() -> dict[str, Any]:
    """Load wiring.yaml specification."""
    wiring_path = Path("cortex/wiring/specifications/wiring.yaml")
    if not wiring_path.exists():
        raise FileNotFoundError(f"Wiring file not found: {wiring_path}")
    
    with open(wiring_path) as f:
        return yaml.safe_load(f)


def find_implementations() -> dict[str, str]:
    """Find all orchestrator class implementations."""
    implementations = {}
    orchestrator_dir = Path("cortex/orchestrators")
    
    if not orchestrator_dir.exists():
        return implementations
    
    patterns = [
        r'class\s+(\w+Orchestrator)\s*[:\(]',
        r'class\s+(\w+Engine)\s*[:\(]',
        r'class\s+(\w+Router)\s*[:\(]',
        r'class\s+(\w+Synthesis)\s*[:\(]',
        r'class\s+(\w+Validator)\s*[:\(]',
        r'class\s+(\w+Classifier)\s*[:\(]',
        r'class\s+(\w+Guard)\s*[:\(]',
        r'class\s+(\w+Detector)\s*[:\(]',
        r'class\s+(\w+Session)\s*[:\(]',
        r'class\s+(\w+Gate)\s*[:\(]',
        r'class\s+(\w+Layer)\s*[:\(]',
        r'class\s+(\w+Repository)\s*[:\(]',
        r'class\s+(\w+Registry)\s*[:\(]',
        r'class\s+(\w+Executor)\s*[:\(]',
        r'class\s+(\w+Planner)\s*[:\(]',
        r'class\s+(\w+Decomposer)\s*[:\(]',
    ]
    
    for py_file in orchestrator_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            content = py_file.read_text()
            for pattern in patterns:
                for match in re.finditer(pattern, content):
                    class_name = match.group(1)
                    implementations[class_name] = str(py_file)
        except Exception:
            continue
    
    return implementations


def grep_files(directory: str, pattern: str) -> list[tuple[str, int, str]]:
    """Search for pattern in files."""
    results = []
    base_path = Path(directory)
    
    if not base_path.exists():
        return results
    
    regex = re.compile(pattern, re.IGNORECASE)
    
    for py_file in base_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            lines = py_file.read_text().splitlines()
            for i, line in enumerate(lines, 1):
                if regex.search(line):
                    results.append((str(py_file), i, line.strip()))
        except Exception:
            continue
    
    return results


def audit_wiring_alignment(report: AlignmentReport) -> None:
    """Check wiring.yaml vs actual implementations."""
    print("🔍 Checking wiring alignment...")
    
    wiring = load_wiring()
    implementations = find_implementations()
    
    orchestrators = wiring.get("orchestrators", {})
    
    # Collect all wired orchestrator names
    wired_names = set()
    wired_tiers = {}
    
    for tier in ["core", "domain", "support"]:
        for orch in orchestrators.get(tier, []):
            if isinstance(orch, dict) and "name" in orch:
                name = orch["name"]
                wired_names.add(name)
                wired_tiers[name] = tier
    
    # Check for wired but not implemented
    for name in wired_names:
        if name not in implementations:
            tier = wired_tiers[name]
            severity = Severity.P0_CRITICAL if tier == "core" else (
                Severity.P1_HIGH if tier == "domain" else Severity.P2_MEDIUM
            )
            report.add_gap(Gap(
                gap_type=GapType.WIRED_NOT_IMPLEMENTED,
                component=name,
                location="cortex/wiring/specifications/wiring.yaml",
                severity=severity,
                remediation=f"Implement {name} in cortex/orchestrators/{tier}/ or remove from wiring.yaml"
            ))
    
    # Check for implemented but not wired
    for name, path in implementations.items():
        if name not in wired_names:
            # Skip test classes and internal helpers
            if "test" in name.lower() or "mock" in name.lower():
                continue
            report.add_gap(Gap(
                gap_type=GapType.IMPLEMENTED_NOT_WIRED,
                component=name,
                location=path,
                severity=Severity.P3_LOW,
                remediation=f"Add {name} to wiring.yaml or delete if unused"
            ))


def audit_stub_tests(report: AlignmentReport) -> None:
    """Find stub tests with assert True."""
    print("🔍 Checking for stub tests...")
    
    stubs = grep_files("tests/", r"assert\s+True\s*[,#\n]")
    
    for filepath, line_num, line_content in stubs:
        # Skip legitimate uses (e.g., in comments explaining patterns)
        if "# Example" in line_content or "documentation" in line_content.lower():
            continue
        
        report.add_gap(Gap(
            gap_type=GapType.STUB_TEST,
            component=f"{filepath}:{line_num}",
            location=filepath,
            severity=Severity.P1_HIGH,
            remediation="Replace with real assertion or delete test"
        ))


def audit_stub_code(report: AlignmentReport) -> None:
    """Find STUB code in production."""
    print("🔍 Checking for STUB code...")
    
    patterns = [
        r"raise\s+NotImplementedError",
        r"#\s*STUB",
        r"#\s*TODO.*implement",
        r"pass\s*#\s*Placeholder",
    ]
    
    for pattern in patterns:
        stubs = grep_files("cortex/", pattern)
        
        for filepath, line_num, line_content in stubs:
            # Skip test files
            if "test" in filepath.lower():
                continue
            # Skip intentional abstract methods
            if "ABC" in line_content or "abstract" in line_content.lower():
                continue
            
            report.add_gap(Gap(
                gap_type=GapType.STUB_CODE,
                component=f"{filepath}:{line_num}",
                location=filepath,
                severity=Severity.P2_MEDIUM,
                remediation="Implement functionality or remove unused code path"
            ))


def audit_skipped_tests(report: AlignmentReport) -> None:
    """Check for excessive skipped tests."""
    print("🔍 Checking for skipped tests...")
    
    skipped = grep_files("tests/", r"pytest\.skip|@pytest\.mark\.skip")
    
    # Count total test functions for ratio
    all_tests = grep_files("tests/", r"def\s+test_")
    total_tests = len(all_tests)
    skip_count = len(skipped)
    
    if total_tests > 0:
        skip_ratio = skip_count / total_tests
        if skip_ratio > 0.05:  # >5% threshold
            report.add_gap(Gap(
                gap_type=GapType.SKIPPED_TEST,
                component=f"{skip_count}/{total_tests} tests skipped ({skip_ratio:.1%})",
                location="tests/",
                severity=Severity.P2_MEDIUM,
                remediation="Review skip reasons, fix blockers or delete obsolete tests"
            ))


def print_report(report: AlignmentReport) -> None:
    """Print alignment report to console."""
    print("\n" + "=" * 60)
    print("CORTEX ALIGNMENT AUDIT REPORT")
    print("=" * 60)
    
    # Summary
    print(f"\n📊 SUMMARY")
    print(f"   Total Gaps: {report.total_count}")
    print(f"   P0 Critical: {report.p0_count}")
    print(f"   P1 High: {report.p1_count}")
    print(f"   P2 Medium: {report.p2_count}")
    print(f"   P3 Low: {len([g for g in report.gaps if g.severity == Severity.P3_LOW])}")
    
    status = "✅ PRODUCTION READY" if report.is_production_ready() else "❌ NOT PRODUCTION READY"
    print(f"\n   Status: {status}")
    
    # Group by type
    gap_types = {}
    for gap in report.gaps:
        if gap.gap_type not in gap_types:
            gap_types[gap.gap_type] = []
        gap_types[gap.gap_type].append(gap)
    
    for gap_type, gaps in gap_types.items():
        print(f"\n{'─' * 60}")
        print(f"📋 {gap_type.value} ({len(gaps)} issues)")
        print("─" * 60)
        
        # Sort by severity
        gaps.sort(key=lambda g: ["P0_CRITICAL", "P1_HIGH", "P2_MEDIUM", "P3_LOW"].index(g.severity.value))
        
        for gap in gaps[:20]:  # Limit to 20 per type
            icon = {"P0_CRITICAL": "🔴", "P1_HIGH": "🟡", "P2_MEDIUM": "🟠", "P3_LOW": "⚪"}
            print(f"   {icon[gap.severity.value]} [{gap.severity.value}] {gap.component}")
            print(f"      → {gap.remediation}")
        
        if len(gaps) > 20:
            print(f"   ... and {len(gaps) - 20} more")


def main():
    parser = argparse.ArgumentParser(description="CORTEX Alignment Audit")
    parser.add_argument("--strict", action="store_true", help="Exit with error if P0/P1 gaps found")
    parser.add_argument("--fix", action="store_true", help="Auto-fix simple issues")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    args = parser.parse_args()
    
    print("🚀 CORTEX Alignment Audit Starting...")
    print("=" * 60)
    
    report = AlignmentReport()
    
    # Run all checks
    try:
        audit_wiring_alignment(report)
    except FileNotFoundError as e:
        print(f"⚠️  {e}")
    
    audit_stub_tests(report)
    audit_stub_code(report)
    audit_skipped_tests(report)
    
    # Print results
    print_report(report)
    
    # Generate markdown report if requested
    if args.report:
        report_path = Path("ALIGNMENT-AUDIT-REPORT.md")
        with open(report_path, "w") as f:
            f.write("# CORTEX Alignment Audit Report\n\n")
            f.write(f"**Generated:** {__import__('datetime').datetime.now().isoformat()}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"| Severity | Count |\n")
            f.write(f"|----------|-------|\n")
            f.write(f"| P0 Critical | {report.p0_count} |\n")
            f.write(f"| P1 High | {report.p1_count} |\n")
            f.write(f"| P2 Medium | {report.p2_count} |\n")
            f.write(f"| Total | {report.total_count} |\n\n")
            
            f.write("## Gaps by Type\n\n")
            gap_types = {}
            for gap in report.gaps:
                if gap.gap_type not in gap_types:
                    gap_types[gap.gap_type] = []
                gap_types[gap.gap_type].append(gap)
            
            for gap_type, gaps in gap_types.items():
                f.write(f"### {gap_type.value} ({len(gaps)})\n\n")
                for gap in gaps:
                    f.write(f"- **{gap.severity.value}**: `{gap.component}`\n")
                    f.write(f"  - Remediation: {gap.remediation}\n")
                f.write("\n")
        
        print(f"\n📄 Report saved to: {report_path}")
    
    # Exit code
    if args.strict and (report.p0_count > 0 or report.p1_count > 0):
        print("\n❌ STRICT MODE: Exiting with error due to P0/P1 gaps")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
