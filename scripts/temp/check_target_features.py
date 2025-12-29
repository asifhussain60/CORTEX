#!/usr/bin/env python3
"""Check status of target features that were remediated."""

from pathlib import Path
from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

# Initialize orchestrator
context = {"project_root": Path.cwd()}
orch = SystemAlignmentOrchestrator(context)

# Execute alignment
result = orch.execute({})
report = result.data.get('report') or result.data
scores = report.feature_scores if hasattr(report, 'feature_scores') else report.get('feature_scores', {})

# Target features from remediation work
target_features = [
    'HolisticCleanupOrchestrator',
    'SetupEPMOrchestrator', 
    'ADOWorkItemOrchestrator',
    'DemoOrchestrator',
    'UnifiedEntryPointOrchestrator'
]

print("\n" + "="*60)
print("TARGET FEATURES STATUS (Remediated in Session)")
print("="*60)

for name in target_features:
    if name in scores:
        score_obj = scores[name]
        print(f"\n{name}:")
        print(f"  Score: {score_obj.score}%")
        print(f"  Status: {score_obj.status}")
        print(f"  Discovered: {'✓' if score_obj.discovered else '✗'}")
        print(f"  Imported: {'✓' if score_obj.imported else '✗'}")
        print(f"  Instantiated: {'✓' if score_obj.instantiated else '✗'}")
        print(f"  Documented: {'✓' if score_obj.documented else '✗'}")
        print(f"  Tested: {'✓' if score_obj.tested else '✗'}")
        print(f"  Wired: {'✓' if score_obj.wired else '✗'}")
        print(f"  Optimized: {'✓' if score_obj.optimized else '✗'}")
        if score_obj.issues:
            print(f"  Issues: {', '.join(score_obj.issues)}")
    else:
        print(f"\n{name}: NOT FOUND")

# Summary
target_scores = [scores[name].score for name in target_features if name in scores]
if target_scores:
    avg_score = sum(target_scores) / len(target_scores)
    print(f"\n{'='*60}")
    print(f"AVERAGE SCORE: {avg_score:.1f}%")
    print(f"ALL ABOVE 80%: {'YES ✓' if all(s >= 80 for s in target_scores) else 'NO ✗'}")
    print(f"{'='*60}\n")
