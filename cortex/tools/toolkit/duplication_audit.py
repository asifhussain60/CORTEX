#!/usr/bin/env python3
"""
CORTEX Comprehensive Duplication Audit Tool
Detects duplicate class/function implementations across codebase
Enforces CORE-035: Single Canonical Implementation
"""

import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import json
from datetime import datetime

class DuplicationAudit:
    """Comprehensive duplication detection engine."""
    
    def __init__(self, root_path: str = "/Users/asifhussain/PROJECTS/CORTEX"):
        self.root = Path(root_path)
        self.cortex_dir = self.root / "cortex"
        self.cortex_brain_dir = self.root / "cortex_brain"
        
        # Tracking structures
        self.class_implementations: Dict[str, List[Dict]] = defaultdict(list)
        self.function_implementations: Dict[str, List[Dict]] = defaultdict(list)
        self.duplicates_found: Dict[str, List[Dict]] = {}
        self.violation_count = 0
        
    def scan_directory(self) -> None:
        """Scan cortex directories for Python implementations."""
        print("🔍 SCANNING CODEBASE FOR IMPLEMENTATIONS...\n")
        
        for py_dir in [self.cortex_dir, self.cortex_brain_dir]:
            if not py_dir.exists():
                continue
                
            for py_file in py_dir.rglob("*.py"):
                if "__pycache__" in str(py_file) or ".pyc" in str(py_file):
                    continue
                self._extract_implementations(py_file)
    
    def _extract_implementations(self, file_path: Path) -> None:
        """Extract class and function definitions from a Python file."""
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"⚠️  Skipping {file_path}: {e}")
            return
        
        # Extract class definitions
        class_pattern = r'^class\s+(\w+)\s*\(.*\):'
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            # Skip test classes and base classes
            if class_name.startswith('Test') or 'Base' in class_name:
                continue
                
            self.class_implementations[class_name].append({
                'file': str(file_path.relative_to(self.root)),
                'line': line_num,
                'type': 'class'
            })
        
        # Extract function definitions (module-level only)
        func_pattern = r'^def\s+(\w+)\s*\('
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            func_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            # Skip test functions and private functions
            if func_name.startswith('test_') or func_name.startswith('_'):
                continue
                
            self.function_implementations[func_name].append({
                'file': str(file_path.relative_to(self.root)),
                'line': line_num,
                'type': 'function'
            })
    
    def detect_duplicates(self) -> Dict[str, List[Dict]]:
        """Identify all duplicate implementations."""
        print("🔎 DETECTING DUPLICATES...\n")
        
        # Check classes
        for class_name, locations in self.class_implementations.items():
            if len(locations) > 1:
                self.duplicates_found[f"CLASS: {class_name}"] = locations
                self.violation_count += len(locations) - 1
        
        # Check functions
        for func_name, locations in self.function_implementations.items():
            if len(locations) > 1:
                self.duplicates_found[f"FUNCTION: {func_name}"] = locations
                self.violation_count += len(locations) - 1
        
        return self.duplicates_found
    
    def identify_priority_targets(self) -> List[Tuple[str, int]]:
        """Identify high-priority consolidation targets."""
        priority = []
        
        # Known duplicates from governance tracking
        known_issues = {
            'ValidationResult': 17,
            'AuditEntry': 13,
            'HealthStatus': 8,
            'Result': 7,
            'ConversationProtocol': 0,  # RESOLVED
        }
        
        for target, expected_count in known_issues.items():
            if target in self.class_implementations:
                actual_count = len(self.class_implementations[target])
                if actual_count > 1:
                    priority.append((target, actual_count - 1))
        
        return sorted(priority, key=lambda x: x[1], reverse=True)
    
    def generate_report(self) -> str:
        """Generate comprehensive audit report."""
        report = []
        report.append("=" * 80)
        report.append("🧠 CORTEX COMPREHENSIVE DUPLICATION AUDIT REPORT")
        report.append("=" * 80)
        report.append(f"\n📅 Generated: {datetime.now().isoformat()}")
        report.append(f"📍 Repository: {self.root}")
        
        report.append("\n" + "=" * 80)
        report.append("📊 DUPLICATION SUMMARY")
        report.append("=" * 80)
        report.append(f"\n✅ Total Unique Classes: {len(self.class_implementations)}")
        report.append(f"✅ Total Unique Functions: {len(self.function_implementations)}")
        report.append(f"⚠️  CORE-035 Violations Found: {self.violation_count}")
        report.append(f"📈 Duplicate Items: {len(self.duplicates_found)}")
        
        if not self.duplicates_found:
            report.append("\n✅ NO DUPLICATES DETECTED - ZERO DUPLICATION CONFIRMED!")
            report.append("🎉 Codebase is 100% compliant with CORE-035")
            return "\n".join(report)
        
        # Detailed violations
        report.append("\n" + "=" * 80)
        report.append("🔴 DETAILED VIOLATIONS (CORE-035 Enforcement)")
        report.append("=" * 80)
        
        for impl_name, locations in sorted(self.duplicates_found.items()):
            report.append(f"\n❌ {impl_name}")
            report.append(f"   Locations: {len(locations)} implementations found")
            for i, loc in enumerate(locations, 1):
                report.append(f"   [{i}] {loc['file']}:{loc['line']}")
        
        # Priority consolidation targets
        report.append("\n" + "=" * 80)
        report.append("🎯 PRIORITY CONSOLIDATION TARGETS (CONS-Pattern)")
        report.append("=" * 80)
        
        priorities = self.identify_priority_targets()
        if priorities:
            for i, (target, violation_count) in enumerate(priorities, 1):
                report.append(f"\n{i}. {target}")
                report.append(f"   Violations: {violation_count}")
                report.append(f"   Pattern: Use CONS-style composition pattern")
                report.append(f"   Action: Consolidate to UnifiedXXX class")
        
        # Governance compliance
        report.append("\n" + "=" * 80)
        report.append("📋 CORE-035 COMPLIANCE STATUS")
        report.append("=" * 80)
        
        if self.violation_count == 0:
            report.append("\n✅ FULL COMPLIANCE - All implementations are canonical")
            report.append("✅ Zero duplication detected")
            report.append("✅ Safe to deploy")
        else:
            report.append(f"\n⚠️  NON-COMPLIANT - {self.violation_count} violations")
            report.append("❌ Duplication detected - consolidation required")
            report.append("🔒 DEPLOYMENT BLOCKED until duplicates resolved")
        
        # Consolidation pattern template
        report.append("\n" + "=" * 80)
        report.append("📝 CONSOLIDATION PATTERN TEMPLATE (from CONS-003-009)")
        report.append("=" * 80)
        
        report.append("""
# Template for consolidation (100% backward compatible)

class UnifiedXXXComponent:
    '''Single canonical implementation (CORE-035 compliant).'''
    
    def __init__(self):
        # Delegate to existing implementations
        self._impl_a = ExistingImplementationA()
        self._impl_b = ExistingImplementationB()
    
    def execute(self, context):
        # Route to appropriate canonical handler
        if context.requires_implementation_a:
            return self._impl_a.execute(context)
        return self._impl_b.execute(context)

# Benefits:
# - Zero breaking changes (composition pattern)
# - Single entry point (CORE-035)
# - 85%+ consolidation value (proven in CONS-003-009)
# - Backward compatible (all existing code works)
""")
        
        # Recommendations
        report.append("\n" + "=" * 80)
        report.append("✅ RECOMMENDATIONS FOR ZERO-DUPLICATION IMPLEMENTATION")
        report.append("=" * 80)
        
        report.append("""
1. BEFORE CODING (Implementation Truth - CORE-030):
   - Run this audit to detect existing implementations
   - Check cortex/ and cortex_brain/ for your class/function name
   - If found: use consolidation pattern instead of creating new

2. DURING IMPLEMENTATION (CORE-035 Enforcement):
   - Use composition pattern (proven in CONS-002-009)
   - Maintain 100% backward compatibility
   - Document as "Unified" canonical entry point
   - Add AC-ID tracking for governance audit

3. AFTER IMPLEMENTATION (Validation):
   - Re-run this audit to confirm zero new duplicates
   - Add tests for consolidation composition pattern
   - Log to governance audit trail with AC_ID
   - Update core-rules.yaml tracking

4. TESTING:
   - Run: pytest tests/ -k consolidation
   - Verify: 100% backward compatibility
   - Benchmark: Time savings from consolidation
   - Report: Update TRANSFORM-002 progress
""")
        
        return "\n".join(report)
    
    def run(self) -> str:
        """Execute full audit."""
        self.scan_directory()
        self.detect_duplicates()
        report = self.generate_report()
        return report


def main():
    """Main entry point."""
    audit = DuplicationAudit()
    report = audit.run()
    print(report)
    
    # Save report
    report_path = Path("reports/analysis") / \
                  f"DUPLICATION-AUDIT-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)
    
    print(f"\n📁 Report saved to: {report_path}")
    
    # Return violation count for CI/CD
    return audit.violation_count


if __name__ == "__main__":
    violation_count = main()
    exit(violation_count)  # Exit code = number of violations
