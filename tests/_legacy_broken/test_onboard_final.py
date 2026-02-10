import sys
import os

# Force UTF-8 encoding
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from pathlib import Path
from cortex.orchestrators.support.repository_onboarding_orchestrator import RepositoryOnboardingOrchestrator

print("Starting KSESSIONS onboarding test...")

repo_path = Path("D:/PROJECTS/KSESSIONS")
orchestrator = RepositoryOnboardingOrchestrator()

result = orchestrator.onboard_repository(repo_path, include_dashboard=True)

print(f"\nSuccess: {result.success}")
print(f"Use cases: {len(result.dashboard_data.get('use_cases', []))}")

for i, uc in enumerate(result.dashboard_data['use_cases'][:10], 1):
    print(f"  {i}. {uc['title']}")
