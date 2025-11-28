#!/usr/bin/env python3
"""
Manual Testing Script for Day 3-4: First-Time Acknowledgment
Sprint 1: Rulebook Visibility Enhancement - US-1.3

Tests the complete user onboarding acknowledgment flow:
- New user sees 3-step onboarding
- Acknowledgment persists in database
- Returning user skips onboarding automatically
- Flow is intuitive and non-intrusive

Usage:
    python scripts/manual_test_day3_4_onboarding.py
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tier1.user_profile_governance import UserProfileGovernance
from orchestrators.onboarding_acknowledgment_orchestrator import OnboardingAcknowledgmentOrchestrator


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_step(step: str, details: str = ""):
    """Print a test step."""
    print(f"✓ {step}")
    if details:
        print(f"  → {details}")


def print_result(success: bool, message: str):
    """Print a test result."""
    icon = "✅" if success else "❌"
    print(f"\n{icon} {message}\n")


def test_scenario_1_new_user():
    """Test Scenario 1: New user sees 3-step onboarding."""
    print_header("SCENARIO 1: New User - First-Time Onboarding")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_tier1.db")
    
    try:
        print_step("Creating new user profile (no acknowledgment)")
        orchestrator = OnboardingAcknowledgmentOrchestrator(db_path=db_path)
        
        # Check if onboarding is needed
        needs_onboarding = orchestrator.needs_onboarding()
        print_result(needs_onboarding, f"New user needs onboarding: {needs_onboarding}")
        
        if not needs_onboarding:
            print_result(False, "FAILED: New user should need onboarding")
            return False
        
        # Step 1: Welcome
        print_step("Executing Step 1: Welcome")
        step1 = orchestrator.execute_step_1_welcome()
        print(f"  Step: {step1['step']}/3")
        print(f"  Title: {step1['title']}")
        print(f"  Content Preview: {step1['content'][:100]}...")
        
        if step1['step'] != 1:
            print_result(False, f"FAILED: Expected step 1, got {step1['step']}")
            return False
        
        # Step 2: Rulebook
        print_step("Executing Step 2: Rulebook Overview")
        step2 = orchestrator.execute_step_2_rulebook()
        print(f"  Step: {step2['step']}/3")
        print(f"  Title: {step2['title']}")
        print(f"  Content Preview: {step2['content'][:100]}...")
        
        if step2['step'] != 2:
            print_result(False, f"FAILED: Expected step 2, got {step2['step']}")
            return False
        
        # Step 3: Acknowledgment
        print_step("Executing Step 3: Acknowledgment Prompt")
        step3 = orchestrator.execute_step_3_acknowledgment()
        print(f"  Step: {step3['step']}/3")
        print(f"  Title: {step3['title']}")
        print(f"  Content Preview: {step3['content'][:100]}...")
        
        if step3['step'] != 3:
            print_result(False, f"FAILED: Expected step 3, got {step3['step']}")
            return False
        
        # Record acknowledgment
        print_step("Recording user acknowledgment")
        result = orchestrator.record_acknowledgment()
        
        if not result['success']:
            print_result(False, f"FAILED: Could not record acknowledgment: {result.get('error')}")
            return False
        
        print_result(True, "All 3 steps completed successfully and acknowledgment recorded")
        
        # Verify acknowledgment persisted
        print_step("Verifying acknowledgment persists in database")
        governance = UserProfileGovernance(db_path=db_path)
        acknowledged = governance.has_acknowledged_rulebook()
        
        if not acknowledged:
            print_result(False, "FAILED: Acknowledgment did not persist")
            return False
        
        status = governance.get_acknowledgment_status()
        print(f"  Acknowledged: {status['acknowledged']}")
        print(f"  Timestamp: {status['acknowledged_at']}")
        print(f"  Onboarding Complete: {status['onboarding_completed']}")
        
        print_result(True, "Acknowledgment persisted successfully")
        
        return True
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_scenario_2_returning_user():
    """Test Scenario 2: Returning user skips onboarding."""
    print_header("SCENARIO 2: Returning User - Auto-Skip Onboarding")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_tier1.db")
    
    try:
        # Simulate a returning user (already acknowledged)
        print_step("Creating returning user profile (acknowledged=1)")
        governance = UserProfileGovernance(db_path=db_path)
        governance.mark_rulebook_acknowledged()
        
        print_step("Checking if returning user needs onboarding")
        orchestrator = OnboardingAcknowledgmentOrchestrator(db_path=db_path)
        
        needs_onboarding = orchestrator.needs_onboarding()
        print_result(not needs_onboarding, f"Returning user should skip onboarding: {not needs_onboarding}")
        
        if needs_onboarding:
            print_result(False, "FAILED: Returning user should not need onboarding")
            return False
        
        # Verify status
        status = orchestrator.get_onboarding_status()
        print(f"  Acknowledged: {status['acknowledged']}")
        print(f"  Needs Onboarding: {status['needs_onboarding']}")
        print(f"  Acknowledged At: {status['acknowledged_at']}")
        
        print_result(True, "Returning user correctly skips onboarding")
        
        return True
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_scenario_3_acknowledgment_persistence():
    """Test Scenario 3: Acknowledgment persists across instances."""
    print_header("SCENARIO 3: Acknowledgment Persistence Across Instances")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_tier1.db")
    
    try:
        # First instance: Record acknowledgment
        print_step("Instance 1: Recording acknowledgment")
        orchestrator1 = OnboardingAcknowledgmentOrchestrator(db_path=db_path)
        
        if not orchestrator1.needs_onboarding():
            print_result(False, "FAILED: Fresh user should need onboarding")
            return False
        
        result = orchestrator1.record_acknowledgment()
        if not result['success']:
            print_result(False, f"FAILED: Could not record acknowledgment: {result.get('error')}")
            return False
        
        print_result(True, "Instance 1 recorded acknowledgment")
        
        # Second instance: Verify persistence
        print_step("Instance 2: Verifying acknowledgment persists")
        orchestrator2 = OnboardingAcknowledgmentOrchestrator(db_path=db_path)
        
        needs_onboarding = orchestrator2.needs_onboarding()
        if needs_onboarding:
            print_result(False, "FAILED: Acknowledgment did not persist across instances")
            return False
        
        status = orchestrator2.get_onboarding_status()
        print(f"  Acknowledged: {status['acknowledged']}")
        print(f"  Needs Onboarding: {status['needs_onboarding']}")
        
        print_result(True, "Acknowledgment persists correctly across instances")
        
        return True
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_scenario_4_ux_validation():
    """Test Scenario 4: UX validation - flow is intuitive and non-intrusive."""
    print_header("SCENARIO 4: UX Validation - Content Quality")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_tier1.db")
    
    try:
        print_step("Creating orchestrator for UX validation")
        orchestrator = OnboardingAcknowledgmentOrchestrator(db_path=db_path)
        
        # Get all steps
        step1 = orchestrator.execute_step_1_welcome()
        step2 = orchestrator.execute_step_2_rulebook()
        step3 = orchestrator.execute_step_3_acknowledgment()
        
        print_step("Validating Step 1: Welcome")
        print(f"  Title: {step1['title']}")
        print(f"  Has content: {len(step1['content']) > 100}")
        print(f"  Has progress indicator: {step1.get('progress') == '1/3'}")
        
        print_step("Validating Step 2: Rulebook")
        print(f"  Title: {step2['title']}")
        print(f"  Has content: {len(step2['content']) > 200}")
        print(f"  Has progress indicator: {step2.get('progress') == '2/3'}")
        print(f"  Mentions protection layers: {'7 Core Protection Layers' in step2['content']}")
        
        print_step("Validating Step 3: Acknowledgment")
        print(f"  Title: {step3['title']}")
        print(f"  Has content: {len(step3['content']) > 100}")
        print(f"  Has progress indicator: {step3.get('progress') == '3/3'}")
        print(f"  Has acknowledgment prompt: {'acknowledge' in step3['content'].lower()}")
        
        # Content quality checks
        quality_checks = [
            len(step1['content']) > 100,
            len(step2['content']) > 200,
            len(step3['content']) > 100,
            step1.get('progress') == '1/3',
            step2.get('progress') == '2/3',
            step3.get('progress') == '3/3',
            '7 Core Protection Layers' in step2['content'],
            'acknowledge' in step3['content'].lower()
        ]
        
        all_passed = all(quality_checks)
        print_result(all_passed, f"UX Quality: {sum(quality_checks)}/{len(quality_checks)} checks passed")
        
        if not all_passed:
            print("Failed checks:")
            check_names = [
                "Step 1 content length > 100",
                "Step 2 content length > 200",
                "Step 3 content length > 100",
                "Step 1 has progress indicator (progress='1/3')",
                "Step 2 has progress indicator (progress='2/3')",
                "Step 3 has progress indicator (progress='3/3')",
                "Step 2 mentions 7 Core Protection Layers",
                "Step 3 has acknowledgment prompt"
            ]
            for i, passed in enumerate(quality_checks):
                if not passed:
                    print(f"  ❌ {check_names[i]}")
        
        return all_passed
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def main():
    """Run all manual test scenarios."""
    print_header("🧪 MANUAL TESTING: Day 3-4 First-Time Acknowledgment")
    print("Sprint 1: Rulebook Visibility Enhancement - US-1.3")
    print("Testing 3-step onboarding acknowledgment flow\n")
    
    results = []
    
    # Run all scenarios
    results.append(("Scenario 1: New User Flow", test_scenario_1_new_user()))
    results.append(("Scenario 2: Returning User Auto-Skip", test_scenario_2_returning_user()))
    results.append(("Scenario 3: Acknowledgment Persistence", test_scenario_3_acknowledgment_persistence()))
    results.append(("Scenario 4: UX Quality Validation", test_scenario_4_ux_validation()))
    
    # Summary
    print_header("📊 MANUAL TESTING SUMMARY")
    
    for scenario, passed in results:
        icon = "✅" if passed else "❌"
        print(f"{icon} {scenario}: {'PASSED' if passed else 'FAILED'}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\n{'=' * 70}")
    print(f"  TOTAL: {passed}/{total} scenarios passed ({passed/total*100:.0f}%)")
    print(f"{'=' * 70}\n")
    
    if passed == total:
        print("✅ ALL MANUAL TESTS PASSED - Ready to commit Day 3-4! ✅\n")
        return 0
    else:
        print(f"❌ {total - passed} SCENARIO(S) FAILED - Review before committing ❌\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
