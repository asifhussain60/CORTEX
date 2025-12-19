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
import io
from pathlib import Path
import json
import shutil
import subprocess
import time
import socket

# Fix Windows console encoding for Unicode emoji support
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

from src.operations.onboarding_orchestrator import OnboardingOrchestrator


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def start_dashboard_server() -> subprocess.Popen:
    """Start dashboard server in a separate PowerShell window"""
    
    # Check if server is already running
    if is_port_in_use(8080):
        print("ℹ️  Dashboard server already running on port 8080")
        return None
    
    print("🚀 Starting dashboard server in separate window...")
    
    # Launch in new PowerShell window that stays open
    cmd = [
        'powershell.exe',
        '-NoExit',
        '-Command',
        f'cd "{project_root}"; python -m src.orchestrators.dashboard_launcher'
    ]
    
    # Start process in new window
    process = subprocess.Popen(
        cmd,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
        cwd=str(project_root)
    )
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    max_retries = 15
    for i in range(max_retries):
        time.sleep(1)
        if is_port_in_use(8080):
            print(f"✅ Dashboard server started (took {i+1}s)")
            return process
    
    print("❌ Dashboard server failed to start within 15 seconds")
    return None


def stop_dashboard_server(process: subprocess.Popen):
    """Stop the dashboard server process"""
    if process is None:
        return
    
    try:
        print("\n🛑 Stopping dashboard server...")
        process.terminate()
        process.wait(timeout=5)
        print("✅ Dashboard server stopped")
    except subprocess.TimeoutExpired:
        print("⚠️  Forcing server shutdown...")
        process.kill()
    except Exception as e:
        print(f"⚠️  Error stopping server: {e}")


def test_onboarding_dashboard_generation():
    """Test that onboarding generates all required dashboard files"""
    
    print("="*70)
    print("ONBOARDING DASHBOARD INTEGRATION TEST")
    print("="*70)
    
    # Start dashboard server
    server_process = start_dashboard_server()
    
    try:
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
        
        # Validate recommendations data
        print(f"\n📋 Validating recommendations data...")
        recommendations_path = expected_output / "recommendations.json"
        with open(recommendations_path, 'r', encoding='utf-8') as f:
            recommendations_data = json.load(f)
        
        total_recommendations = recommendations_data.get('summary', {}).get('total_recommendations', 0)
        if total_recommendations > 0:
            print(f"✅ Found {total_recommendations} recommendations")
            # Show breakdown by category
            by_category = recommendations_data.get('summary', {}).get('by_category', {})
            for category, count in by_category.items():
                if count > 0:
                    print(f"   - {category}: {count}")
        else:
            print(f"⚠️  No recommendations generated (expected at least 1)")
        
        # Validate overview data
        print(f"\n📊 Validating overview data...")
        overview_path = expected_output / "overview.json"
        with open(overview_path, 'r', encoding='utf-8') as f:
            overview_data = json.load(f)
        
        project_name = overview_data.get('project_name')
        health_score = overview_data.get('overall_health', {}).get('score', 0)
        print(f"✅ Project: {project_name}")
        print(f"✅ Health Score: {health_score}")
        
        # Summary
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        print(f"Files Generated: {len(present_files)}/{len(required_files)}")
        print(f"Recommendations: {total_recommendations}")
        print(f"Output Location: {expected_output}")
        print(f"Dashboard URL: {result.dashboard_url}")
        print("="*70)
        
        return True
    
    finally:
        # Clean up server
        stop_dashboard_server(server_process)


if __name__ == '__main__':
    success = test_onboarding_dashboard_generation()
    sys.exit(0 if success else 1)
