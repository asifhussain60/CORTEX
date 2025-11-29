"""Get critical features needing fixes"""
import sys
sys.path.insert(0, 'src')

from pathlib import Path
from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

print("Analyzing critical features...\n")
orch = SystemAlignmentOrchestrator()
report = orch.run_full_validation(monitor=None)

print(f"Critical Features (<70% health):")
critical = [(name, score) for name, score in report.feature_scores.items() if score.score < 70]
critical_sorted = sorted(critical, key=lambda x: x[1].score)

for name, score in critical_sorted[:15]:  # Top 15 critical
    layers = f"D{'+'  if score.discovered else '-'} I{'+' if score.imported else '-'} C{'+' if score.instantiated else '-'} Doc{'+' if score.documented else '-'} T{'+' if score.tested else '-'} W{'+' if score.wired else '-'}"
    print(f"  {name}: {score.score}% ({layers})")
    if not score.documented:
        print(f"    -> Missing: Documentation")
    if not score.tested:
        print(f"    -> Missing: Test coverage")
    if not score.wired:
        print(f"    -> Missing: Entry point wiring")
