"""
AST Completeness Checker for RA API Specifications

Validates that all public methods, business rules, and logic paths from legacy code
are documented in the generated business specification.

Author: CORTEX
Version: 1.0
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple, Set
import argparse


class ASTCompletenessChecker:
    """Validates specification completeness against legacy C# code."""
    
    def __init__(self, legacy_file: Path, spec_file: Path):
        self.legacy_file = legacy_file
        self.spec_file = spec_file
        self.legacy_content = legacy_file.read_text(encoding='utf-8')
        self.spec_content = spec_file.read_text(encoding='utf-8')
        
    def extract_public_methods(self) -> List[Dict[str, any]]:
        """Extract all public method signatures from legacy code."""
        # Pattern: public [static] [async] ReturnType MethodName(params)
        pattern = r'public\s+(?:static\s+)?(?:async\s+)?(\w+(?:<.*?>)?)\s+(\w+)\s*\((.*?)\)'
        matches = re.finditer(pattern, self.legacy_content, re.MULTILINE)
        
        methods = []
        for match in matches:
            return_type = match.group(1)
            method_name = match.group(2)
            parameters = match.group(3)
            
            # Get line number
            line_num = self.legacy_content[:match.start()].count('\n') + 1
            
            methods.append({
                'name': method_name,
                'return_type': return_type,
                'parameters': parameters.strip(),
                'line': line_num,
                'signature': match.group(0)
            })
        
        return methods
    
    def extract_if_statements(self) -> List[Dict[str, any]]:
        """Extract all if/else branches representing business rules."""
        pattern = r'if\s*\((.*?)\)'
        matches = re.finditer(pattern, self.legacy_content, re.MULTILINE)
        
        conditions = []
        for match in matches:
            condition = match.group(1).strip()
            line_num = self.legacy_content[:match.start()].count('\n') + 1
            
            conditions.append({
                'condition': condition,
                'line': line_num
            })
        
        return conditions
    
    def extract_validation_rules(self) -> List[Dict[str, any]]:
        """Extract validation logic (throw, return error, etc.)."""
        # Look for throw statements, ModelState errors, etc.
        patterns = [
            r'throw new (\w+)\("(.+?)"\)',
            r'ModelState\.AddModelError\("(.+?)", "(.+?)"\)',
            r'return.*Error.*"(.+?)"'
        ]
        
        validations = []
        for pattern in patterns:
            matches = re.finditer(pattern, self.legacy_content, re.MULTILINE | re.DOTALL)
            for match in matches:
                line_num = self.legacy_content[:match.start()].count('\n') + 1
                validations.append({
                    'type': 'validation',
                    'line': line_num,
                    'message': match.group(1) if len(match.groups()) == 1 else match.group(2)
                })
        
        return validations
    
    def extract_database_operations(self) -> List[Dict[str, any]]:
        """Extract database queries and operations."""
        patterns = [
            r'(SELECT|INSERT|UPDATE|DELETE)\s+.*FROM\s+(\w+)',
            r'\.(\w+Repository)\.',
            r'_context\.(\w+)\.(?:Add|Update|Remove|Find)'
        ]
        
        db_ops = []
        for pattern in patterns:
            matches = re.finditer(pattern, self.legacy_content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = self.legacy_content[:match.start()].count('\n') + 1
                db_ops.append({
                    'type': 'database',
                    'line': line_num,
                    'operation': match.group(0)[:50]  # Truncate long queries
                })
        
        return db_ops
    
    def extract_external_service_calls(self) -> List[Dict[str, any]]:
        """Extract calls to external services/APIs."""
        patterns = [
            r'_(\w+Client)\.',
            r'_(\w+Service)\.',
            r'await\s+(\w+)\.(?:GetAsync|PostAsync|PutAsync|DeleteAsync)'
        ]
        
        service_calls = []
        for pattern in patterns:
            matches = re.finditer(pattern, self.legacy_content, re.MULTILINE)
            for match in matches:
                line_num = self.legacy_content[:match.start()].count('\n') + 1
                service_calls.append({
                    'type': 'external_service',
                    'line': line_num,
                    'service': match.group(1)
                })
        
        return service_calls
    
    def extract_spec_operations(self) -> Set[str]:
        """Extract documented operations from specification."""
        # Look for operation sections: ### Operation: MethodName
        pattern = r'###\s+Operation:\s+(\w+)'
        matches = re.finditer(pattern, self.spec_content, re.MULTILINE)
        return {match.group(1) for match in matches}
    
    def extract_spec_business_rules(self) -> List[str]:
        """Extract documented business rules from specification."""
        # Look for numbered business rules: 1. **RuleName:**
        pattern = r'\d+\.\s+\*\*(.+?):\*\*'
        matches = re.finditer(pattern, self.spec_content, re.MULTILINE)
        return [match.group(1) for match in matches]
    
    def extract_spec_line_references(self) -> Set[int]:
        """Extract all legacy line numbers referenced in specification."""
        # Look for legacy code references: [Line 45], (line 67), etc.
        patterns = [
            r'\[Line (\d+)\]',
            r'\(line (\d+)\)',
            r'Line (\d+):',
            r'L(\d+)'
        ]
        
        line_refs = set()
        for pattern in patterns:
            matches = re.finditer(pattern, self.spec_content, re.MULTILINE)
            line_refs.update(int(match.group(1)) for match in matches)
        
        return line_refs
    
    def validate_method_coverage(self) -> Tuple[bool, List[str]]:
        """Check if all public methods are documented."""
        legacy_methods = self.extract_public_methods()
        spec_operations = self.extract_spec_operations()
        
        missing = []
        for method in legacy_methods:
            if method['name'] not in spec_operations:
                missing.append(f"Line {method['line']}: {method['name']}()")
        
        return len(missing) == 0, missing
    
    def validate_business_rule_coverage(self) -> Tuple[bool, List[str]]:
        """Check if all if/else branches are documented as rules."""
        legacy_conditions = self.extract_if_statements()
        spec_rules = self.extract_spec_business_rules()
        
        # This is a heuristic - we can't perfectly match conditions to rules
        # But we can check if the number of conditions is roughly covered
        coverage_ratio = len(spec_rules) / max(len(legacy_conditions), 1)
        
        if coverage_ratio < 0.8:  # 80% threshold
            return False, [
                f"Only {len(spec_rules)} rules documented for {len(legacy_conditions)} conditions",
                f"Coverage: {coverage_ratio:.1%} (target: 80%+)"
            ]
        
        return True, []
    
    def validate_validation_coverage(self) -> Tuple[bool, List[str]]:
        """Check if all validation rules are documented."""
        legacy_validations = self.extract_validation_rules()
        
        # Check if validation messages appear in spec
        missing = []
        for validation in legacy_validations:
            if validation['message'] not in self.spec_content:
                missing.append(f"Line {validation['line']}: {validation['message']}")
        
        return len(missing) == 0, missing
    
    def validate_database_operations_coverage(self) -> Tuple[bool, List[str]]:
        """Check if database operations are documented."""
        db_ops = self.extract_database_operations()
        
        # Check for database/data flow section in spec
        has_data_section = bool(re.search(r'###\s+Data Flow|###\s+Database Operations', self.spec_content))
        
        if not has_data_section and len(db_ops) > 0:
            return False, [f"Found {len(db_ops)} database operations but no Data Flow section"]
        
        return True, []
    
    def run_all_checks(self) -> Dict[str, any]:
        """Run complete validation suite."""
        results = {
            'overall_pass': True,
            'checks': {}
        }
        
        # Check 1: Method Coverage
        passed, missing = self.validate_method_coverage()
        results['checks']['method_coverage'] = {
            'passed': passed,
            'missing': missing,
            'count': len(missing)
        }
        if not passed:
            results['overall_pass'] = False
        
        # Check 2: Business Rule Coverage
        passed, issues = self.validate_business_rule_coverage()
        results['checks']['business_rule_coverage'] = {
            'passed': passed,
            'issues': issues
        }
        if not passed:
            results['overall_pass'] = False
        
        # Check 3: Validation Coverage
        passed, missing = self.validate_validation_coverage()
        results['checks']['validation_coverage'] = {
            'passed': passed,
            'missing': missing,
            'count': len(missing)
        }
        if not passed:
            results['overall_pass'] = False
        
        # Check 4: Database Operations
        passed, issues = self.validate_database_operations_coverage()
        results['checks']['database_operations'] = {
            'passed': passed,
            'issues': issues
        }
        if not passed:
            results['overall_pass'] = False
        
        return results
    
    def print_report(self, results: Dict[str, any]):
        """Print validation report."""
        print("=" * 70)
        print("AST COMPLETENESS VALIDATION REPORT")
        print("=" * 70)
        print(f"Legacy File: {self.legacy_file.name}")
        print(f"Specification: {self.spec_file.name}")
        print("=" * 70)
        
        for check_name, check_results in results['checks'].items():
            status = "✅ PASS" if check_results['passed'] else "❌ FAIL"
            print(f"\n{status} - {check_name.replace('_', ' ').title()}")
            
            if 'missing' in check_results and check_results['missing']:
                print(f"  Missing items ({check_results['count']}):")
                for item in check_results['missing'][:5]:  # Show first 5
                    print(f"    - {item}")
                if check_results['count'] > 5:
                    print(f"    ... and {check_results['count'] - 5} more")
            
            if 'issues' in check_results and check_results['issues']:
                print("  Issues:")
                for issue in check_results['issues']:
                    print(f"    - {issue}")
        
        print("\n" + "=" * 70)
        if results['overall_pass']:
            print("✅ OVERALL STATUS: PASS - Specification is complete")
        else:
            print("❌ OVERALL STATUS: FAIL - Specification needs updates")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Validate specification completeness')
    parser.add_argument('--legacy', required=True, help='Path to legacy C# file')
    parser.add_argument('--spec', required=True, help='Path to business specification')
    
    args = parser.parse_args()
    
    legacy_path = Path(args.legacy)
    spec_path = Path(args.spec)
    
    if not legacy_path.exists():
        print(f"❌ Error: Legacy file not found: {legacy_path}")
        return 1
    
    if not spec_path.exists():
        print(f"❌ Error: Specification file not found: {spec_path}")
        return 1
    
    checker = ASTCompletenessChecker(legacy_path, spec_path)
    results = checker.run_all_checks()
    checker.print_report(results)
    
    return 0 if results['overall_pass'] else 1


if __name__ == '__main__':
    exit(main())
