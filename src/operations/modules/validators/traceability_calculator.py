"""
Traceability Coverage Calculator for RA API Specifications

Calculates bidirectional traceability between legacy code, specifications,
and modern implementation.

Author: CORTEX
Version: 1.0
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse


class TraceabilityCalculator:
    """Calculates specification traceability coverage."""
    
    def __init__(self, legacy_file: Path, spec_file: Path, matrix_file: Path = None):
        self.legacy_file = legacy_file
        self.spec_file = spec_file
        self.matrix_file = matrix_file
        
        self.legacy_content = legacy_file.read_text(encoding='utf-8')
        self.spec_content = spec_file.read_text(encoding='utf-8')
        self.matrix_content = matrix_file.read_text(encoding='utf-8') if matrix_file and matrix_file.exists() else None
        
    def count_logic_lines(self) -> int:
        """Count lines of actual logic in legacy code (excluding comments, braces)."""
        lines = self.legacy_content.split('\n')
        logic_lines = 0
        
        in_comment_block = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
            
            # Handle multi-line comments
            if '/*' in stripped:
                in_comment_block = True
            if '*/' in stripped:
                in_comment_block = False
                continue
            if in_comment_block:
                continue
            
            # Skip single-line comments
            if stripped.startswith('//'):
                continue
            
            # Skip braces-only lines
            if stripped in ['{', '}']:
                continue
            
            # Skip using statements, namespace declarations
            if stripped.startswith('using ') or stripped.startswith('namespace '):
                continue
            
            # Count as logic line
            logic_lines += 1
        
        return logic_lines
    
    def extract_spec_line_references(self) -> Set[int]:
        """Extract all legacy line numbers referenced in specification."""
        patterns = [
            r'\[Line (\d+)\]',
            r'\(line (\d+)\)',
            r'Line (\d+):',
            r'L(\d+)',
            r'Lines? (\d+)-(\d+)'  # Line ranges
        ]
        
        line_refs = set()
        for pattern in patterns:
            matches = re.finditer(pattern, self.spec_content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2:  # Line range
                    start = int(match.group(1))
                    end = int(match.group(2))
                    line_refs.update(range(start, end + 1))
                else:
                    line_refs.add(int(match.group(1)))
        
        return line_refs
    
    def extract_matrix_mappings(self) -> List[Dict[str, str]]:
        """Extract mappings from traceability matrix."""
        if not self.matrix_content:
            return []
        
        # Parse markdown table
        # | Legacy Code | Line | Business Rule | Spec Section | Modern Layer |
        pattern = r'\|\s*(.+?)\s*\|\s*(\d+(?:-\d+)?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|'
        matches = re.finditer(pattern, self.matrix_content, re.MULTILINE)
        
        mappings = []
        for match in matches:
            # Skip table header
            if 'Legacy Code' in match.group(1):
                continue
            if '---' in match.group(1):
                continue
            
            mappings.append({
                'legacy_file': match.group(1).strip(),
                'line': match.group(2).strip(),
                'business_rule': match.group(3).strip(),
                'spec_section': match.group(4).strip(),
                'modern_layer': match.group(5).strip()
            })
        
        return mappings
    
    def calculate_spec_coverage(self) -> Tuple[float, Dict[str, any]]:
        """Calculate what % of legacy code is referenced in specification."""
        logic_lines = self.count_logic_lines()
        referenced_lines = self.extract_spec_line_references()
        
        coverage = (len(referenced_lines) / logic_lines * 100) if logic_lines > 0 else 0.0
        
        return coverage, {
            'total_logic_lines': logic_lines,
            'referenced_lines': len(referenced_lines),
            'coverage_percent': coverage
        }
    
    def calculate_matrix_coverage(self) -> Tuple[float, Dict[str, any]]:
        """Calculate traceability matrix completeness."""
        if not self.matrix_content:
            return 0.0, {'error': 'No matrix file provided'}
        
        mappings = self.extract_matrix_mappings()
        logic_lines = self.count_logic_lines()
        
        # Count unique line ranges covered by matrix
        covered_lines = set()
        for mapping in mappings:
            line_str = mapping['line']
            if '-' in line_str:
                start, end = map(int, line_str.split('-'))
                covered_lines.update(range(start, end + 1))
            else:
                covered_lines.add(int(line_str))
        
        coverage = (len(covered_lines) / logic_lines * 100) if logic_lines > 0 else 0.0
        
        return coverage, {
            'total_logic_lines': logic_lines,
            'mapped_lines': len(covered_lines),
            'total_mappings': len(mappings),
            'coverage_percent': coverage
        }
    
    def validate_bidirectional_traceability(self) -> Tuple[bool, List[str]]:
        """Check if spec references match matrix mappings."""
        if not self.matrix_content:
            return True, ["Matrix file not provided - skipping bidirectional check"]
        
        spec_refs = self.extract_spec_line_references()
        mappings = self.extract_matrix_mappings()
        
        # Extract all lines from matrix
        matrix_lines = set()
        for mapping in mappings:
            line_str = mapping['line']
            if '-' in line_str:
                start, end = map(int, line_str.split('-'))
                matrix_lines.update(range(start, end + 1))
            else:
                matrix_lines.add(int(line_str))
        
        # Check for spec references not in matrix
        missing_from_matrix = spec_refs - matrix_lines
        
        # Check for matrix mappings not referenced in spec
        missing_from_spec = matrix_lines - spec_refs
        
        issues = []
        if missing_from_matrix:
            issues.append(f"{len(missing_from_matrix)} spec references not in matrix")
        if missing_from_spec:
            issues.append(f"{len(missing_from_spec)} matrix mappings not referenced in spec")
        
        return len(issues) == 0, issues
    
    def extract_spec_sections(self) -> Set[str]:
        """Extract all specification section numbers."""
        # Pattern: § 3.2, Section 3.2, etc.
        patterns = [
            r'§\s*(\d+\.\d+)',
            r'Section\s+(\d+\.\d+)',
            r'###\s+(\d+\.\d+)'
        ]
        
        sections = set()
        for pattern in patterns:
            matches = re.finditer(pattern, self.spec_content, re.MULTILINE)
            sections.update(match.group(1) for match in matches)
        
        return sections
    
    def validate_spec_section_coverage(self) -> Tuple[bool, List[str]]:
        """Check if all spec sections are referenced in matrix."""
        if not self.matrix_content:
            return True, ["Matrix file not provided - skipping section coverage"]
        
        spec_sections = self.extract_spec_sections()
        mappings = self.extract_matrix_mappings()
        
        # Extract sections from matrix
        matrix_sections = {mapping['spec_section'].strip('§ ') for mapping in mappings}
        
        missing_sections = spec_sections - matrix_sections
        
        issues = []
        if missing_sections:
            issues.append(f"Spec sections not in matrix: {', '.join(sorted(missing_sections))}")
        
        return len(missing_sections) == 0, issues
    
    def calculate_overall_score(self) -> float:
        """Calculate overall traceability quality score (0-100)."""
        score = 0.0
        
        # Weight: 40% spec coverage
        spec_coverage, _ = self.calculate_spec_coverage()
        score += (spec_coverage / 100) * 40
        
        # Weight: 40% matrix coverage
        matrix_coverage, _ = self.calculate_matrix_coverage()
        score += (matrix_coverage / 100) * 40
        
        # Weight: 20% bidirectional consistency
        bidirectional_ok, _ = self.validate_bidirectional_traceability()
        if bidirectional_ok:
            score += 20
        
        return min(100.0, score)
    
    def run_all_checks(self) -> Dict[str, any]:
        """Run complete traceability validation."""
        results = {
            'overall_pass': True,
            'score': 0.0,
            'checks': {}
        }
        
        # Check 1: Spec Coverage
        coverage, details = self.calculate_spec_coverage()
        results['checks']['spec_coverage'] = {
            'passed': coverage >= 95.0,
            'coverage': coverage,
            'details': details
        }
        if coverage < 95.0:
            results['overall_pass'] = False
        
        # Check 2: Matrix Coverage
        if self.matrix_content:
            coverage, details = self.calculate_matrix_coverage()
            results['checks']['matrix_coverage'] = {
                'passed': coverage >= 95.0,
                'coverage': coverage,
                'details': details
            }
            if coverage < 95.0:
                results['overall_pass'] = False
        else:
            results['checks']['matrix_coverage'] = {
                'passed': False,
                'coverage': 0.0,
                'details': {'error': 'No matrix file provided'}
            }
            results['overall_pass'] = False
        
        # Check 3: Bidirectional Traceability
        passed, issues = self.validate_bidirectional_traceability()
        results['checks']['bidirectional'] = {
            'passed': passed,
            'issues': issues
        }
        if not passed and self.matrix_content:
            results['overall_pass'] = False
        
        # Check 4: Section Coverage
        passed, issues = self.validate_spec_section_coverage()
        results['checks']['section_coverage'] = {
            'passed': passed,
            'issues': issues
        }
        if not passed and self.matrix_content:
            results['overall_pass'] = False
        
        # Calculate overall score
        results['score'] = self.calculate_overall_score()
        
        return results
    
    def print_report(self, results: Dict[str, any]):
        """Print traceability report."""
        print("=" * 70)
        print("TRACEABILITY COVERAGE REPORT")
        print("=" * 70)
        print(f"Legacy File: {self.legacy_file.name}")
        print(f"Specification: {self.spec_file.name}")
        if self.matrix_file:
            print(f"Matrix File: {self.matrix_file.name}")
        print(f"Overall Score: {results['score']:.1f}/100")
        print("=" * 70)
        
        for check_name, check_results in results['checks'].items():
            status = "✅ PASS" if check_results['passed'] else "❌ FAIL"
            print(f"\n{status} - {check_name.replace('_', ' ').title()}")
            
            if 'coverage' in check_results:
                print(f"  Coverage: {check_results['coverage']:.1f}%")
            
            if 'details' in check_results:
                details = check_results['details']
                if 'total_logic_lines' in details:
                    print(f"  Total Logic Lines: {details['total_logic_lines']}")
                    print(f"  Referenced/Mapped: {details.get('referenced_lines', details.get('mapped_lines', 0))}")
                if 'total_mappings' in details:
                    print(f"  Total Mappings: {details['total_mappings']}")
            
            if 'issues' in check_results and check_results['issues']:
                print("  Issues:")
                for issue in check_results['issues']:
                    print(f"    - {issue}")
        
        print("\n" + "=" * 70)
        if results['overall_pass']:
            print("✅ OVERALL STATUS: PASS - Traceability is complete")
        else:
            print("❌ OVERALL STATUS: FAIL - Traceability needs improvement")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Calculate traceability coverage')
    parser.add_argument('--legacy', required=True, help='Path to legacy C# file')
    parser.add_argument('--spec', required=True, help='Path to business specification')
    parser.add_argument('--matrix', help='Path to traceability matrix (optional)')
    
    args = parser.parse_args()
    
    legacy_path = Path(args.legacy)
    spec_path = Path(args.spec)
    matrix_path = Path(args.matrix) if args.matrix else None
    
    if not legacy_path.exists():
        print(f"❌ Error: Legacy file not found: {legacy_path}")
        return 1
    
    if not spec_path.exists():
        print(f"❌ Error: Specification file not found: {spec_path}")
        return 1
    
    calculator = TraceabilityCalculator(legacy_path, spec_path, matrix_path)
    results = calculator.run_all_checks()
    calculator.print_report(results)
    
    return 0 if results['overall_pass'] else 1


if __name__ == '__main__':
    exit(main())
