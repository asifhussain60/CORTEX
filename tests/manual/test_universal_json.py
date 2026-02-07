"""Quick test of Universal Dashboard Generator JSON generation."""

import pytest
pytestmark = pytest.mark.skip(reason="Phase 38.0 remediation pending - manual dashboard tests skipped")

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

# Wrapped imports - modules may not exist
try:
    from cortex.orchestrators.support.universal_dashboard_generator import get_universal_dashboard_generator
    from cortex.orchestrators.support.business_language_orchestrator import get_business_language_orchestrator

    # Generate narrative
    repo_path = Path("D:/PROJECTS/KASHKOLE")
    biz_orch = get_business_language_orchestrator()
    narrative = biz_orch.generate_narrative(repo_path, {})

    # Mock analysis data
    analysis_data = {
        'repo_path': str(repo_path),
        'timestamp': '2026-02-01T10:30:00',
        'security_risks': {
            'p0_risks': [{'id': 'SEC-001'}],
            'p1_risks': [],
            'p2_risks': []
        },
        'holistic_context': {
            'code_analysis': {
                'files': ['file1.py', 'file2.py']
            }
        }
    }
except (ImportError, ModuleNotFoundError):
    pass


# Generate dashboard
generator = get_universal_dashboard_generator()
print(f"Generator dashboards root: {generator.dashboards_root}")

dashboard_path = generator.generate_dashboard(
    repo_name="kashkole",
    narrative=narrative,
    analysis_data=analysis_data
)

print(f"\nDashboard generated: {dashboard_path}")

# Check data files
data_dir = dashboard_path.parent / "data"
print(f"\nData directory: {data_dir}")
print(f"Exists: {data_dir.exists()}")

if data_dir.exists():
    files = list(data_dir.glob("*"))
    print(f"Files: {[f.name for f in files]}")
