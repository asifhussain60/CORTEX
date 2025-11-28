#!/usr/bin/env python3
"""
Test Protection Event Notifications (Sprint 2 - Task 7)

Demonstrates the new notification system that displays educational
governance alerts in Copilot Chat when rules are violated.

Purpose:
- Verify notification formatting with severity indicators
- Test educational explanations and suggested fixes
- Confirm dashboard links are included
- Validate both BLOCKED and WARNING notifications

Author: Asif Hussain
Date: November 28, 2025
Sprint: 2 (Active Compliance Dashboard)
Task: 7 (Protection Event Notifications)
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.tier0.brain_protector import BrainProtector, ModificationRequest, Severity


def test_blocked_notification():
    """Test notification for BLOCKED severity (Instinct Immutability)."""
    print("=" * 80)
    print("TEST 1: BLOCKED Notification (Disable TDD)")
    print("=" * 80)
    
    protector = BrainProtector()
    
    # Create request that violates Instinct Immutability
    request = ModificationRequest(
        intent="disable TDD workflow",
        description="Skip test-first development and remove RED-GREEN-REFACTOR cycle",
        files=["src/tdd/workflow.py"],
        justification="Want to move faster without writing tests first"
    )
    
    # Validate and get result
    result = protector.analyze_request(request)
    
    print(f"\n🔍 Validation Result:")
    print(f"   Severity: {result.severity.value.upper()}")
    print(f"   Decision: {result.decision}")
    print(f"   Violations: {len(result.violations)}")
    print(f"   Override Required: {result.override_required}")
    
    # Generate and display notification
    if result.severity != Severity.SAFE:
        notification = protector.format_user_notification(result)
        print("\n📢 USER-FACING NOTIFICATION:")
        print(notification)
    
    return result.severity == Severity.BLOCKED


def test_warning_notification():
    """Test notification for WARNING severity (SOLID Compliance)."""
    print("\n" + "=" * 80)
    print("TEST 2: WARNING Notification (God Object)")
    print("=" * 80)
    
    protector = BrainProtector()
    
    # Create request that violates SOLID Compliance
    request = ModificationRequest(
        intent="create centralized manager",
        description="Add all-in-one manager class with config, state, orchestration, and logging responsibilities",
        files=["src/managers/master_manager.py"],
        justification="Convenience and centralization"
    )
    
    # Validate and get result
    result = protector.analyze_request(request)
    
    print(f"\n🔍 Validation Result:")
    print(f"   Severity: {result.severity.value.upper()}")
    print(f"   Decision: {result.decision}")
    print(f"   Violations: {len(result.violations)}")
    print(f"   Override Required: {result.override_required}")
    
    # Generate and display notification
    if result.severity != Severity.SAFE:
        notification = protector.format_user_notification(result)
        print("\n📢 USER-FACING NOTIFICATION:")
        print(notification)
    
    return result.severity == Severity.WARNING


def test_safe_operation():
    """Test that safe operations produce no notification."""
    print("\n" + "=" * 80)
    print("TEST 3: SAFE Operation (No Notification)")
    print("=" * 80)
    
    protector = BrainProtector()
    
    # Create safe request
    request = ModificationRequest(
        intent="add utility function",
        description="Add helper function for string formatting in utils module",
        files=["src/utils/string_helpers.py"],
        justification="Code organization improvement"
    )
    
    # Validate and get result
    result = protector.analyze_request(request)
    
    print(f"\n🔍 Validation Result:")
    print(f"   Severity: {result.severity.value.upper()}")
    print(f"   Decision: {result.decision}")
    print(f"   Violations: {len(result.violations)}")
    
    # Generate notification (should be empty)
    notification = protector.format_user_notification(result)
    
    if notification:
        print("\n❌ UNEXPECTED: Notification generated for safe operation!")
        print(notification)
        return False
    else:
        print("\n✅ CORRECT: No notification for safe operation")
        return True


def test_notification_components():
    """Test that notification includes all required components."""
    print("\n" + "=" * 80)
    print("TEST 4: Notification Component Validation")
    print("=" * 80)
    
    protector = BrainProtector()
    
    # Create request with multiple violations
    request = ModificationRequest(
        intent="bypass DoR validation",
        description="Skip Definition of Ready checks and remove acceptance criteria requirements",
        files=["src/planning/dor_validator.py"],
        justification="Want to start coding faster"
    )
    
    result = protector.analyze_request(request)
    notification = protector.format_user_notification(result)
    
    # Check required components
    required_components = {
        "Severity Emoji": any(emoji in notification for emoji in ["🔴", "🟡", "🟢"]),
        "Governance Header": "Governance" in notification,
        "Rules Violated Section": "Rules Violated:" in notification,
        "Layer Information": "Layer:" in notification,
        "Issue Description": "Issue:" in notification,
        "Why This Matters": "Why This Matters:" in notification or "Rationale" in notification,
        "Suggested Fix": "Suggested Fix:" in notification or "remedy" in notification.lower(),
        "Dashboard Link": "show compliance" in notification,
        "Markdown Formatting": "##" in notification and "**" in notification
    }
    
    print("\n📋 Component Checklist:")
    all_present = True
    for component, present in required_components.items():
        status = "✅" if present else "❌"
        print(f"   {status} {component}")
        if not present:
            all_present = False
    
    if all_present:
        print("\n✅ All required components present")
    else:
        print("\n❌ Some components missing - review notification format")
    
    return all_present


def main():
    """Run all notification tests."""
    print("\n")
    print("🧪 CORTEX Sprint 2 - Task 7: Protection Event Notifications Test")
    print("=" * 80)
    print("Testing user-facing governance notifications with educational context\n")
    
    results = {
        "Blocked Notification": test_blocked_notification(),
        "Warning Notification": test_warning_notification(),
        "Safe Operation": test_safe_operation(),
        "Component Validation": test_notification_components()
    }
    
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Notification system working correctly.")
        print("\n📋 Next Steps:")
        print("   1. Mark Task 7 as complete")
        print("   2. Move to Task 8 (Unit Tests)")
        print("   3. Move to Task 9 (Integration Tests)")
        print("   4. Complete Task 10 (Manual Validation)")
        return 0
    else:
        print("\n❌ Some tests failed. Review notification implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
