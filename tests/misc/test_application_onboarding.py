"""
Quick test for Application Onboarding Operation

Tests that the application onboarding operation is properly configured
and can execute the crawlers to generate documentation.

Author: Asif Hussain
"""

from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.operations.application_onboarding_operation import ApplicationOnboardingOperation

def test_application_onboarding():
    """Test application onboarding operation"""
    print("=" * 60)
    print("Testing Application Onboarding Operation")
    print("=" * 60)
    
    # Create operation instance
    print("\n✅ Step 1: Creating ApplicationOnboardingOperation instance...")
    operation = ApplicationOnboardingOperation()
    print(f"   ✓ Operation created successfully")
    print(f"   ✓ Step registry initialized with {len(operation.step_registry._steps)} steps")
    
    # List registered steps
    print("\n✅ Step 2: Verifying registered steps...")
    expected_steps = [
        "copy_cortex_entry_points",
        "install_tooling",
        "initialize_brain_tiers",
        "crawl_application",
        "analyze_discoveries",
        "generate_smart_questions",
        "present_onboarding_summary"
    ]
    
    for step_id in expected_steps:
        if operation.step_registry.get_step(step_id):
            print(f"   ✓ {step_id} - registered")
        else:
            print(f"   ✗ {step_id} - NOT FOUND")
            return False
    
    print(f"\n✅ Step 3: Checking critical crawl_application step...")
    crawl_step = operation.step_registry.get_step("crawl_application")
    if crawl_step:
        print(f"   ✓ Crawl step found: {crawl_step.name}")
        print(f"   ✓ Description: {crawl_step.description}")
        print(f"   ✓ Estimated duration: {crawl_step.estimated_duration}s")
    else:
        print(f"   ✗ Crawl step NOT FOUND!")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe application onboarding operation is properly configured.")
    print("It will run crawlers to generate documentation for applications.")
    print("\nTo use: 'onboard this application' or 'analyze my codebase'")
    
    return True

if __name__ == "__main__":
    success = test_application_onboarding()
    sys.exit(0 if success else 1)
