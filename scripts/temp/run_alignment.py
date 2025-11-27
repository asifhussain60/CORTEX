#!/usr/bin/env python3
"""Run system alignment validation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

def main():
    orchestrator = SystemAlignmentOrchestrator({'project_root': Path.cwd()})
    report = orchestrator.run_full_validation()
    
    print(f'\n[OK] Overall Health: {report.overall_health}%')
    print(f'Critical Issues: {report.critical_issues}')
    print(f'Warnings: {report.warnings}')
    print(f'\nFeatures Validated: {len(report.feature_scores)}')
    
    healthy = sum(1 for s in report.feature_scores.values() if s.score >= 90)
    warning = sum(1 for s in report.feature_scores.values() if 70 <= s.score < 90)
    critical = sum(1 for s in report.feature_scores.values() if s.score < 70)
    
    print(f'  [OK] Healthy (>=90%): {healthy}')
    print(f'  [WARN] Warning (70-89%): {warning}')
    print(f'  [CRIT] Critical (<70%): {critical}')
    
    print(f'\nTop Issues:')
    issues = [(n, s) for n, s in report.feature_scores.items() if s.score < 90]
    issues.sort(key=lambda x: x[1].score)
    
    for name, score in issues[:5]:
        issues_str = ", ".join(score.issues)
        print(f'  {score.status} {name}: {score.score}% - {issues_str}')
    
    if len(issues) > 5:
        print(f'  ... and {len(issues) - 5} more issues')
    
    # Show remediation suggestions
    if report.remediation_suggestions:
        print(f'\n[INFO] {len(report.remediation_suggestions)} auto-remediation suggestions available')
    
    # Show deployment gate results
    if report.deployment_gate_results:
        gate_results = report.deployment_gate_results
        print(f'\n[GATE] Deployment Gates: {"PASS" if gate_results.get("passed") else "FAIL"}')
    
    # Show package purity results
    if report.package_purity_results:
        purity_results = report.package_purity_results
        print(f'[PKG] Package Purity: {"PURE" if purity_results.get("is_pure") else "CONTAMINATED"}')

if __name__ == '__main__':
    main()
