"""Quick test script for dashboard generation"""

from pathlib import Path
from src.cortex_lens.orchestrator import CortexLens

# Initialize CORTEX Lens
lens = CortexLens()

# Analyze current repository with console_app template
result = lens.analyze(
    repo_path='.',
    template='console_app'
)

print(f"\n✅ Analysis complete!")
print(f"📊 Dashboard: {result.get('dashboard_path')}")
print(f"📦 Package: {result.get('package_path')}")
print(f"🎯 Template: console_app")
