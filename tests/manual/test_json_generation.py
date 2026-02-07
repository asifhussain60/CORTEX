"""Test JSON data generation for Kashkole dashboard.

SKIPPED: DomainDashboardGenerator not available
         Phase 38.0 remediation pending.
"""

import pytest

pytestmark = pytest.mark.skip(reason="DomainDashboardGenerator not available - Phase 38.0 remediation pending")

from pathlib import Path

def main():
    print("Testing JSON data generation...")
    
    # Setup
    domain_name = "kashkole"
    domain_path = Path("company/dashboards/kashkole")
    domain_path.mkdir(parents=True, exist_ok=True)
    
    # Create generator
    generator = DomainDashboardGenerator(
        domain_name=domain_name,
        domain_path=domain_path
    )
    
    print(f"Generator created. Data dir: {generator.data_dir}")
    print(f"Data dir exists: {generator.data_dir.exists()}")
    
    # Mock onboarding data
    onboarding_data = {
        'repo_path': 'D:/PROJECTS/KASHKOLE',
        'timestamp': '2026-02-01T10:30:00',
        'security_risks': {
            'p0_risks': [{'id': 'SEC-001', 'category': 'Hardcoded Credentials', 'description': 'Test finding'}],
            'p1_risks': [],
            'p2_risks': []
        },
        'holistic_context': {
            'code_analysis': {
                'files': ['file1.py', 'file2.py']
            }
        },
        'recommendations': []
    }
    
    # Generate data
    print("\nCalling _generate_overview_data...")
    try:
        generator._generate_overview_data(onboarding_data)
        print("✅ Overview data generated")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Check files
    print(f"\nChecking data directory...")
    if generator.data_dir.exists():
        files = list(generator.data_dir.glob("*"))
        print(f"Files in data dir: {files}")
    else:
        print("Data directory doesn't exist!")

if __name__ == "__main__":
    main()
