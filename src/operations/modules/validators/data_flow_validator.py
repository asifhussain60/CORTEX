"""
Data Flow Validator for RA API Specifications

Compares documented data flow diagrams against actual execution traces
to ensure accuracy of sequence diagrams.

Author: CORTEX
Version: 1.0
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Tuple
import argparse


class DataFlowValidator:
    """Validates data flow diagrams against execution traces."""
    
    def __init__(self, mermaid_file: Path, trace_file: Path = None):
        self.mermaid_file = mermaid_file
        self.trace_file = trace_file
        self.mermaid_content = mermaid_file.read_text(encoding='utf-8')
        self.trace_content = trace_file.read_text(encoding='utf-8') if trace_file else None
        
    def parse_mermaid_sequence(self) -> List[Dict[str, str]]:
        """Extract sequence diagram steps from Mermaid."""
        # Pattern: Actor->>Component: Message
        pattern = r'(\w+)->>(\w+):\s*(.+)'
        matches = re.finditer(pattern, self.mermaid_content, re.MULTILINE)
        
        steps = []
        for match in matches:
            steps.append({
                'from': match.group(1),
                'to': match.group(2),
                'message': match.group(3).strip(),
                'type': 'call'
            })
        
        # Pattern: Component-->>Actor: Response
        pattern = r'(\w+)-->>(\w+):\s*(.+)'
        matches = re.finditer(pattern, self.mermaid_content, re.MULTILINE)
        
        for match in matches:
            steps.append({
                'from': match.group(1),
                'to': match.group(2),
                'message': match.group(3).strip(),
                'type': 'response'
            })
        
        return steps
    
    def extract_documented_paths(self) -> Set[str]:
        """Extract all execution paths from diagram."""
        steps = self.parse_mermaid_sequence()
        paths = set()
        
        for step in steps:
            path = f"{step['from']} -> {step['to']}: {step['message']}"
            paths.add(path)
        
        return paths
    
    def parse_trace_log(self) -> List[Dict[str, str]]:
        """Parse execution trace log (if available)."""
        if not self.trace_content:
            return []
        
        # Expected format: [TRACE] Component.Method(params) -> Result
        pattern = r'\[TRACE\]\s+(\w+)\.(\w+)\((.*?)\)\s*->\s*(.+)'
        matches = re.finditer(pattern, self.trace_content, re.MULTILINE)
        
        trace_steps = []
        for match in matches:
            trace_steps.append({
                'component': match.group(1),
                'method': match.group(2),
                'params': match.group(3),
                'result': match.group(4).strip()
            })
        
        return trace_steps
    
    def extract_components(self) -> Set[str]:
        """Extract all components mentioned in diagram."""
        # Pattern: participant ComponentName
        pattern = r'participant\s+(\w+)'
        matches = re.finditer(pattern, self.mermaid_content, re.MULTILINE)
        
        components = {match.group(1) for match in matches}
        
        # Also extract from arrows
        steps = self.parse_mermaid_sequence()
        for step in steps:
            components.add(step['from'])
            components.add(step['to'])
        
        return components
    
    def extract_alt_paths(self) -> List[Dict[str, any]]:
        """Extract alternative paths (error handling, conditionals)."""
        # Pattern: alt ConditionName
        pattern = r'alt\s+(.+?)(?:\n|\r)'
        matches = re.finditer(pattern, self.mermaid_content, re.MULTILINE)
        
        alt_paths = []
        for match in matches:
            condition = match.group(1).strip()
            alt_paths.append({
                'type': 'alternative',
                'condition': condition
            })
        
        # Pattern: else AnotherCondition
        pattern = r'else\s+(.+?)(?:\n|\r)'
        matches = re.finditer(pattern, self.mermaid_content, re.MULTILINE)
        
        for match in matches:
            condition = match.group(1).strip()
            alt_paths.append({
                'type': 'else',
                'condition': condition
            })
        
        return alt_paths
    
    def validate_diagram_syntax(self) -> Tuple[bool, List[str]]:
        """Validate Mermaid syntax is correct."""
        issues = []
        
        # Check for sequenceDiagram declaration
        if 'sequenceDiagram' not in self.mermaid_content:
            issues.append("Missing 'sequenceDiagram' declaration")
        
        # Check for balanced alt/end blocks
        alt_count = len(re.findall(r'\balt\b', self.mermaid_content))
        end_count = len(re.findall(r'\bend\b', self.mermaid_content))
        
        if alt_count != end_count:
            issues.append(f"Unbalanced alt/end blocks: {alt_count} alt, {end_count} end")
        
        # Check for valid arrow syntax
        steps = self.parse_mermaid_sequence()
        if len(steps) == 0:
            issues.append("No sequence steps found (check arrow syntax)")
        
        return len(issues) == 0, issues
    
    def validate_completeness(self) -> Tuple[bool, List[str]]:
        """Check if diagram includes all necessary components."""
        issues = []
        
        components = self.extract_components()
        steps = self.parse_mermaid_sequence()
        
        # Check if there are participants
        if len(components) == 0:
            issues.append("No components/participants defined")
        
        # Check if there are interactions
        if len(steps) == 0:
            issues.append("No interactions documented")
        
        # Check for common components in RA APIs
        expected_components = {'Controller', 'UseCase', 'Repository', 'Database'}
        missing_expected = expected_components - components
        
        if missing_expected and len(components) > 0:  # Only warn if there are some components
            issues.append(f"Consider adding: {', '.join(missing_expected)}")
        
        # Check for error paths
        alt_paths = self.extract_alt_paths()
        if len(alt_paths) == 0:
            issues.append("No error/alternative paths documented (consider adding 'alt' blocks)")
        
        return len(issues) == 0, issues
    
    def validate_against_trace(self) -> Tuple[bool, List[str]]:
        """Validate diagram against execution trace (if available)."""
        if not self.trace_content:
            return True, ["Trace file not provided - skipping trace validation"]
        
        issues = []
        
        documented_paths = self.extract_documented_paths()
        trace_steps = self.parse_trace_log()
        
        # Build paths from trace
        trace_paths = set()
        for step in trace_steps:
            path = f"{step['component']}.{step['method']}"
            trace_paths.add(path)
        
        # Check if major trace paths are documented
        for trace_path in trace_paths:
            found = any(trace_path in doc_path for doc_path in documented_paths)
            if not found:
                issues.append(f"Trace path not documented: {trace_path}")
        
        return len(issues) == 0, issues
    
    def calculate_coverage_score(self) -> float:
        """Calculate overall diagram quality score (0-100)."""
        score = 100.0
        
        # Deduct points for issues
        syntax_ok, syntax_issues = self.validate_diagram_syntax()
        if not syntax_ok:
            score -= 30.0  # Critical issue
        
        completeness_ok, completeness_issues = self.validate_completeness()
        if not completeness_ok:
            score -= min(20.0, len(completeness_issues) * 5)
        
        trace_ok, trace_issues = self.validate_against_trace()
        if not trace_ok and self.trace_content:  # Only penalize if trace was provided
            score -= min(30.0, len(trace_issues) * 10)
        
        return max(0.0, score)
    
    def run_all_checks(self) -> Dict[str, any]:
        """Run complete validation suite."""
        results = {
            'overall_pass': True,
            'score': 0.0,
            'checks': {}
        }
        
        # Check 1: Syntax
        passed, issues = self.validate_diagram_syntax()
        results['checks']['syntax'] = {
            'passed': passed,
            'issues': issues
        }
        if not passed:
            results['overall_pass'] = False
        
        # Check 2: Completeness
        passed, issues = self.validate_completeness()
        results['checks']['completeness'] = {
            'passed': passed,
            'issues': issues
        }
        if not passed:
            results['overall_pass'] = False
        
        # Check 3: Trace Validation
        passed, issues = self.validate_against_trace()
        results['checks']['trace_validation'] = {
            'passed': passed,
            'issues': issues
        }
        if not passed and self.trace_content:
            results['overall_pass'] = False
        
        # Calculate score
        results['score'] = self.calculate_coverage_score()
        
        return results
    
    def print_report(self, results: Dict[str, any]):
        """Print validation report."""
        print("=" * 70)
        print("DATA FLOW VALIDATION REPORT")
        print("=" * 70)
        print(f"Mermaid File: {self.mermaid_file.name}")
        if self.trace_file:
            print(f"Trace File: {self.trace_file.name}")
        print(f"Quality Score: {results['score']:.1f}/100")
        print("=" * 70)
        
        for check_name, check_results in results['checks'].items():
            status = "✅ PASS" if check_results['passed'] else "❌ FAIL"
            print(f"\n{status} - {check_name.replace('_', ' ').title()}")
            
            if check_results['issues']:
                print("  Issues:")
                for issue in check_results['issues']:
                    print(f"    - {issue}")
        
        print("\n" + "=" * 70)
        if results['overall_pass']:
            print("✅ OVERALL STATUS: PASS - Data flow diagram is valid")
        else:
            print("❌ OVERALL STATUS: FAIL - Data flow diagram needs updates")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description='Validate data flow diagrams')
    parser.add_argument('--mermaid', required=True, help='Path to Mermaid diagram file')
    parser.add_argument('--trace', help='Path to execution trace log (optional)')
    
    args = parser.parse_args()
    
    mermaid_path = Path(args.mermaid)
    trace_path = Path(args.trace) if args.trace else None
    
    if not mermaid_path.exists():
        print(f"❌ Error: Mermaid file not found: {mermaid_path}")
        return 1
    
    if trace_path and not trace_path.exists():
        print(f"⚠️  Warning: Trace file not found: {trace_path}")
        trace_path = None
    
    validator = DataFlowValidator(mermaid_path, trace_path)
    results = validator.run_all_checks()
    validator.print_report(results)
    
    return 0 if results['overall_pass'] else 1


if __name__ == '__main__':
    exit(main())
