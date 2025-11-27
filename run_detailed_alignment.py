import sys
sys.path.insert(0, 'src')

from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator
from pathlib import Path
import json

orchestrator = SystemAlignmentOrchestrator({'project_root': Path.cwd()})
result = orchestrator.execute({})

report = result.data["report"]

print('\n' + '='*80)
print('CORTEX SYSTEM ALIGNMENT REPORT')
print('='*80)
print(f'\nOverall Health: {report.overall_health}% ({report.critical_issues} critical, {report.warnings} warnings)')
print(f'Status: {result.status}')
print(f'Discovered Features: {len(report.feature_scores)}')

# Critical Issues
print('\n' + '='*80)
print('CRITICAL ISSUES (10)')
print('='*80)

critical_count = 0
for name, score in report.feature_scores.items():
    if score.score < 70:  # Critical threshold
        critical_count += 1
        print(f'\n{critical_count}. {name} ({score.feature_type}) - Score: {score.score}%')
        print(f'   Issues: {", ".join(score.issues)}')

# File Organization Violations
if report.organization_violations:
    print(f'\n{critical_count + 1}. File Organization - Score: {report.organization_score}%')
    print(f'   Violations: {len(report.organization_violations)} issues')
    for i, v in enumerate(report.organization_violations[:3], 1):
        msg = v.message if hasattr(v, 'message') else str(v)
        print(f'   - {msg}')
    if len(report.organization_violations) > 3:
        print(f'   ... and {len(report.organization_violations) - 3} more')

# Header Violations
if report.header_violations:
    print(f'\nHeader Compliance - Score: {report.header_compliance_score}%')
    print(f'   Violations: {len(report.header_violations)} issues')
    for i, v in enumerate(report.header_violations[:3], 1):
        msg = v.message if hasattr(v, 'message') else str(v)
        print(f'   - {msg}')
    if len(report.header_violations) > 3:
        print(f'   ... and {len(report.header_violations) - 3} more')

# Documentation Governance
if report.doc_governance_violations:
    print(f'\nDocumentation Governance - Score: {report.doc_governance_score}%')
    print(f'   Violations: {len(report.doc_governance_violations)} issues')
    for i, v in enumerate(report.doc_governance_violations[:3], 1):
        msg = v.message if hasattr(v, 'message') else str(v)
        print(f'   - {msg}')
    if len(report.doc_governance_violations) > 3:
        print(f'   ... and {len(report.doc_governance_violations) - 3} more')

# Warnings
print('\n' + '='*80)
print('WARNINGS (18)')
print('='*80)

warning_count = 0
for name, score in report.feature_scores.items():
    if 70 <= score.score < 90:  # Warning threshold
        warning_count += 1
        print(f'\n{warning_count}. {name} ({score.feature_type}) - Score: {score.score}%')
        print(f'   Issues: {", ".join(score.issues)}')

# Ghost Features
if report.ghost_features:
    print(f'\nGhost Features (no entry point): {len(report.ghost_features)}')
    for gf in report.ghost_features[:5]:
        print(f'   - {gf}')

# Orphaned Triggers
if report.orphaned_triggers:
    print(f'\nOrphaned Triggers (no implementation): {len(report.orphaned_triggers)}')
    for ot in report.orphaned_triggers[:5]:
        print(f'   - {ot}')

print('\n' + '='*80)
print('SUMMARY')
print('='*80)
print(f'Total Issues: {report.critical_issues + report.warnings}')
print(f'Path to 90% Health: Fix {report.critical_issues} critical + reduce {report.warnings} warnings')
print('='*80 + '\n')
