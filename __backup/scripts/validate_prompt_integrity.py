#!/usr/bin/env python3
"""
CORTEX Prompt Self-Review Validator
Checks CORTEX.prompt.md against its own declared rules.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

class PromptValidator:
    def __init__(self, prompt_path: Path):
        self.prompt_path = prompt_path
        self.content = prompt_path.read_text()
        self.line_count = len(self.content.splitlines())
        self.violations = []
        
    def check_core_001_violation(self) -> bool:
        """CORE-001: Operations <500 lines. Prompt itself is 3890 lines."""
        if self.line_count > 500:
            self.violations.append({
                'rule': 'CORE-001',
                'severity': 'HIGH',
                'issue': f'Prompt is {self.line_count} lines (target: <500)',
                'recommendation': 'Split into: routing-table.yaml, failure-modes.yaml, workflow.md'
            })
            return False
        return True
    
    def check_executive_summary_compliance(self) -> bool:
        """Check if prompt follows its own executive summary rules."""
        # Count code snippets (lines starting with 4+ spaces or ``` blocks)
        code_lines = len([l for l in self.content.splitlines() if l.startswith('    ') or l.startswith('```')])
        narrative_lines = self.line_count - code_lines
        
        if narrative_lines > self.line_count * 0.3:  # >30% narrative
            self.violations.append({
                'rule': 'EXECUTIVE_SUMMARY',
                'severity': 'MEDIUM',
                'issue': f'{narrative_lines} lines of narrative prose (target: minimal bullets)',
                'recommendation': 'Convert to declarative bullets, remove filler'
            })
            return False
        return True
    
    def check_referenced_scripts_exist(self) -> bool:
        """Verify all referenced scripts actually exist."""
        script_refs = re.findall(r'scripts/([a-z_]+\.py)', self.content)
        root = self.prompt_path.parent.parent
        missing = []
        stubs = []
        
        for script in set(script_refs):
            script_path = root / 'scripts' / script
            if not script_path.exists():
                missing.append(script)
            else:
                # Check if stub (< 100 lines or contains "PLANNED")
                content = script_path.read_text()
                if len(content.splitlines()) < 100 or 'STATUS: PLANNED' in content or 'raise NotImplementedError' in content:
                    stubs.append(script)
        
        if missing:
            self.violations.append({
                'rule': 'REFERENCE_INTEGRITY',
                'severity': 'HIGH',
                'issue': f'Referenced scripts missing: {", ".join(missing)}',
                'recommendation': 'Create scripts or remove references'
            })
            return False
        
        if stubs:
            self.violations.append({
                'rule': 'REFERENCE_INTEGRITY',
                'severity': 'MEDIUM',
                'issue': f'Referenced scripts are stubs/planned: {", ".join(stubs)}',
                'recommendation': 'Implement scripts or mark as PLANNED in prompt'
            })
            # Don't fail - stubs are acceptable if marked
        
        return len(missing) == 0
    
    def check_plan_viewer_paths(self) -> bool:
        """Check for stale plan-viewer paths."""
        stale_refs = re.findall(r'templates/plan-viewer/', self.content)
        correct_refs = re.findall(r'cx6-plan/viewer/', self.content)
        
        if stale_refs:
            self.violations.append({
                'rule': 'PATH_CONSISTENCY',
                'severity': 'MEDIUM',
                'issue': f'{len(stale_refs)} references to obsolete templates/plan-viewer/',
                'recommendation': 'Global replace: templates/plan-viewer → cx6-plan/viewer'
            })
            return False
        return True
    
    def check_phantom_implementations(self) -> bool:
        """Check for referenced classes/functions that may not exist."""
        phantom_candidates = [
            ('BrittlenessAmbiguityValidator', 'src/infrastructure/brittleness_ambiguity_validator.py'),
            ('run_synchronization_check', 'src/orchestrators/core/state_synchronizer.py'),
            ('phase_gate_validator', 'src/orchestrators/gates/phase_gate_validator.py'),
        ]
        
        root = self.prompt_path.parent.parent
        missing = []
        stubs = []
        
        for name, expected_path in phantom_candidates:
            if name in self.content:
                full_path = root / expected_path
                if not full_path.exists():
                    missing.append(f'{name} → {expected_path}')
                else:
                    # Check if stub/planned
                    content = full_path.read_text()
                    if 'STATUS: PLANNED' in content or 'raise NotImplementedError' in content:
                        stubs.append(f'{name} (PLANNED in {expected_path})')
        
        if missing:
            self.violations.append({
                'rule': 'IMPLEMENTATION_INTEGRITY',
                'severity': 'CRITICAL',
                'issue': f'Phantom implementations: {"; ".join(missing)}',
                'recommendation': 'Implement classes or mark as planned/future'
            })
            return False
        
        if stubs:
            self.violations.append({
                'rule': 'IMPLEMENTATION_INTEGRITY',
                'severity': 'MEDIUM',
                'issue': f'Implementations are PLANNED: {"; ".join(stubs)}',
                'recommendation': 'Document as PLANNED in prompt or defer to Phase 2'
            })
            # Don't fail - PLANNED is acceptable if documented
        
        return len(missing) == 0
    
    def check_self_contradictions(self) -> bool:
        """Detect contradictory statements."""
        contradictions = []
        
        # Example: Claims automatic execution but requires manual invocation
        if 'ON EVERY TURN' in self.content and 'python3 -m' in self.content:
            auto_claims = len(re.findall(r'(automatic|automatically|ON EVERY TURN)', self.content, re.I))
            manual_cmds = len(re.findall(r'python3 -m src\.', self.content))
            
            if manual_cmds > auto_claims * 2:  # More manual than auto claims
                contradictions.append('Claims automatic execution but provides manual commands')
        
        if contradictions:
            self.violations.append({
                'rule': 'LOGICAL_CONSISTENCY',
                'severity': 'HIGH',
                'issue': '; '.join(contradictions),
                'recommendation': 'Clarify automation vs manual execution contexts'
            })
            return False
        return True
    
    def generate_report(self) -> str:
        """Generate executive summary of violations."""
        if not self.violations:
            return "✅ All self-review checks passed. Prompt integrity validated."
        
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_violations = sorted(self.violations, key=lambda v: severity_order[v['severity']])
        
        report = [
            "# CORTEX.prompt.md Self-Review Report",
            f"**Prompt:** {self.prompt_path}",
            f"**Lines:** {self.line_count}",
            f"**Violations:** {len(self.violations)}",
            "",
            "## Violations by Severity",
            ""
        ]
        
        by_severity = {}
        for v in sorted_violations:
            sev = v['severity']
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append(v)
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if severity in by_severity:
                report.append(f"### {severity}")
                for v in by_severity[severity]:
                    report.append(f"- **{v['rule']}:** {v['issue']}")
                    report.append(f"  - *Fix:* {v['recommendation']}")
                report.append("")
        
        # Summary
        critical = len([v for v in self.violations if v['severity'] == 'CRITICAL'])
        high = len([v for v in self.violations if v['severity'] == 'HIGH'])
        
        if critical > 0:
            report.append(f"⛔ **BLOCKED:** {critical} critical violation(s) prevent operation.")
        elif high > 0:
            report.append(f"⚠️ **WARNING:** {high} high-priority issue(s) should be fixed soon.")
        else:
            report.append("✅ **ACCEPTABLE:** Only minor issues detected.")
        
        return '\n'.join(report)
    
    def run_all_checks(self) -> Dict[str, bool]:
        """Run all validation checks."""
        results = {
            'CORE-001': self.check_core_001_violation(),
            'EXECUTIVE_SUMMARY': self.check_executive_summary_compliance(),
            'REFERENCE_INTEGRITY': self.check_referenced_scripts_exist(),
            'PATH_CONSISTENCY': self.check_plan_viewer_paths(),
            'IMPLEMENTATION_INTEGRITY': self.check_phantom_implementations(),
            'LOGICAL_CONSISTENCY': self.check_self_contradictions(),
        }
        return results

def main():
    import sys
    
    if len(sys.argv) > 1:
        prompt_path = Path(sys.argv[1])
    else:
        # Default to CORTEX location
        prompt_path = Path(__file__).parent.parent / '.github/prompts/CORTEX.prompt.md'
    
    if not prompt_path.exists():
        print(f"❌ Prompt not found: {prompt_path}")
        sys.exit(1)
    
    validator = PromptValidator(prompt_path)
    results = validator.run_all_checks()
    
    print(validator.generate_report())
    print("\n" + "="*80)
    print("Check Results:")
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {check}")
    
    # Exit code: 0 if all pass, 1 if any fail
    sys.exit(0 if all(results.values()) else 1)

if __name__ == '__main__':
    main()
