"""Quick alignment check after scoring fix"""
import sys
sys.path.insert(0, 'src')

from pathlib import Path
from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

print("Running system alignment validation...\n")
orch = SystemAlignmentOrchestrator()  # No context parameter - it auto-detects project root
result = orch.execute({'mode': 'validate', 'auto_prompt_fix': False})  # Skip interactive prompt

print(f"\nDEBUG: result type = {type(result)}")
print(f"DEBUG: result.success = {result.success}")
print(f"DEBUG: result.status = {result.status}")
print(f"DEBUG: result.data keys = {list(result.data.keys()) if result.data else 'None'}")

print(f"\n{'='*60}")
print(f"SYSTEM ALIGNMENT RESULTS")
print(f"{'='*60}")
print(f"Overall Health: {result.data.get('overall_health', 0)}%")
print(f"Critical Issues: {result.data.get('critical_issues', 0)}")
print(f"Warnings: {result.data.get('warnings', 0)}")
print(f"\nTop 5 Healthy Features:")
for feat in result.data.get('summary', {}).get('top_performers', [])[:5]:
    print(f"  ✅ {feat['name']}: {feat['health']}%")

print(f"\nPriority 1 Orchestrators (Previously 60%, Target 90%):")
priority_features = ['CommitOrchestrator', 'DiagramRegenerationOrchestrator', 'OnboardingOrchestrator']
for feat_name in priority_features:
    for feat in result.data.get('orchestrators', []):
        if feat['name'] == feat_name:
            print(f"  {'✅' if feat['health'] >= 70 else '⚠️'} {feat_name}: {feat['health']}%")
            break
