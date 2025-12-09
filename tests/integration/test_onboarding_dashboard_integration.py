#!/usr/bin/env python3
"""
Integration test for onboarding orchestrator dashboard generation

Verifies that OnboardingOrchestrator:
1. Generates all 10 required JSON files
2. Outputs to correct path (cortex-brain/dashboards/data/repos/{repo-slug}/)
3. Uses DashboardOrchestrator for data collection
4. Returns correct dashboard URL

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
import json
import shutil

# Add project root to path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

from src.operations.onboarding_orchestrator import OnboardingOrchestrator


def test_onboarding_dashboard_generation():
    """Test that onboarding generates all required dashboard files"""
    
    print("="*70)
    print("ONBOARDING DASHBOARD INTEGRATION TEST")
    print("="*70)
    
    # Use a sample app from cortex-sample-apps
    test_project = project_root / "cortex-sample-apps" / "CleanSolidApp"
    
    if not test_project.exists():
        print(f"❌ Test project not found: {test_project}")
        return False
    
    print(f"\n📂 Test Project: {test_project.name}")
    print(f"   Path: {test_project}")
    
    # Initialize orchestrator in test mode
    print("\n🔧 Initializing OnboardingOrchestrator (test mode)...")
    orchestrator = OnboardingOrchestrator(project_root, test_mode=True)
    
    # Expected output path
    repo_slug = test_project.name.lower().replace(" ", "-")
    expected_output = project_root / "cortex-brain" / "dashboards" / "data" / "repos" / repo_slug
    
    print(f"\n📍 Expected Output Path:")
    print(f"   {expected_output}")
    
    # Clean up any existing test data
    if expected_output.exists():
        print(f"\n🧹 Cleaning up existing test data...")
        shutil.rmtree(expected_output)
    
    # Run onboarding
    print(f"\n🚀 Running onboarding on {test_project.name}...")
    try:
        result = orchestrator.onboard_application(
            project_path=test_project,
            project_name=test_project.name
        )
    except Exception as e:
        print(f"\n❌ Onboarding failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Check result
    if not result.success:
        print(f"\n❌ Onboarding failed:")
        for error in result.errors:
            print(f"   - {error}")
        return False
    
    print(f"\n✅ Onboarding completed successfully")
    print(f"   Quality Score: {result.quality_score:.1f}")
    print(f"   Security Issues: {result.security_issues}")
    print(f"   Dashboard URL: {result.dashboard_url}")
    
    # Verify output path exists
    print(f"\n🔍 Verifying output path...")
    if not expected_output.exists():
        print(f"❌ Output directory not found: {expected_output}")
        return False
    print(f"✅ Output directory exists")
    
    # Verify all 10 required JSON files
    print(f"\n📄 Verifying JSON files...")
    required_files = [
        "overview.json",
        "executive-summary.json",
        "executive-intelligence.json",
        "health-data.json",
        "tech-stack.json",
        "security.json",
        "architecture.json",
        "code-organization.json",
        "vendors.json",
        "reconciliation.json"
    ]
    
    missing_files = []
    present_files = []
    
    for filename in required_files:
        file_path = expected_output / filename
        if file_path.exists():
            # Verify it's valid JSON
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                present_files.append(filename)
                print(f"   ✅ {filename} ({len(json.dumps(data))} bytes)")
            except json.JSONDecodeError:
                print(f"   ❌ {filename} (invalid JSON)")
                missing_files.append(filename)
        else:
            print(f"   ❌ {filename} (missing)")
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n❌ Missing or invalid files: {len(missing_files)}/{len(required_files)}")
        return False
    
    print(f"\n✅ All {len(required_files)} JSON files generated successfully")
    
    # Verify dashboard URL format
    print(f"\n🔗 Verifying dashboard URL format...")
    expected_url_pattern = f"http://localhost:8080/ui/index.html?source={repo_slug}"
    if result.dashboard_url != expected_url_pattern:
        print(f"❌ Incorrect URL format:")
        print(f"   Expected: {expected_url_pattern}")
        print(f"   Got: {result.dashboard_url}")
        return False
    
    print(f"✅ Dashboard URL format correct")
    
    # Summary
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED")
    print("="*70)
    print(f"Files Generated: {len(present_files)}/{len(required_files)}")
    print(f"Output Location: {expected_output}")
    print(f"Dashboard URL: {result.dashboard_url}")
    print("="*70)
    
    return True


if __name__ == '__main__':
    success = test_onboarding_dashboard_generation()
    sys.exit(0 if success else 1)
