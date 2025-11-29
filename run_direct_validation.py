"""Direct validation check bypassing progress monitor emojis"""
import sys
sys.path.insert(0, 'src')

from pathlib import Path
from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

print("Running direct validation (no progress monitor)...\n")
orch = SystemAlignmentOrchestrator()

# Call run_full_validation directly (bypasses emoji issues)
report = orch.run_full_validation(monitor=None)

print(f"\n{'='*60}")
print(f"SYSTEM ALIGNMENT RESULTS")
print(f"{'='*60}")
print(f"Overall Health: {report.overall_health}%")
print(f"Total Features: {len(report.feature_scores)}")
print(f"Critical Issues: {report.critical_issues} | Warnings: {report.warnings}")

print(f"\nTop 10 Features by Health:")
sorted_features = sorted(
    report.feature_scores.items(),
    key=lambda x: x[1].score,
    reverse=True
)[:10]
for name, score in sorted_features:
    status = "OK" if score.score >= 70 else ("WARN" if score.score >= 40 else "CRIT")
    print(f"  [{status}] {name}: {score.score}% - {score.status}")

print(f"\nPriority 1 Orchestrators (Previously 50-60%, Target: 90%):")
priority_features = ['CommitOrchestrator', 'DiagramRegenerationOrchestrator', 'OnboardingOrchestrator']
for feat_name in priority_features:
    if feat_name in report.feature_scores:
        score = report.feature_scores[feat_name]
        status = "PASS" if score.score >= 70 else "FAIL"
        layers = f"Disc:{'+' if score.discovered else '-'} Imp:{'+' if score.imported else '-'} Inst:{'+' if score.instantiated else '-'} Doc:{'+' if score.documented else '-'} Test:{'+' if score.tested else '-'} Wire:{'+' if score.wired else '-'}"
        print(f"  [{status}] {feat_name}: {score.score}% ({layers})")
    else:
        print(f"  [NOTFOUND] {feat_name}")
