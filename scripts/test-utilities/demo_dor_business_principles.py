#!/usr/bin/env python3
"""
Demo: Business Principles Display in DoR

Shows actual markdown output with business principles.
"""

from cortex.orchestrators.core.dor_approval_gate import IntentReflection


def demo_dor_display():
    """Demonstrate DoR display with business principles."""
    
    print("=" * 80)
    print("DEMO: DoR Intent Classification with Business Principles")
    print("=" * 80)
    print()
    
    # Create sample reflection
    reflection = IntentReflection(
        intent_type="IMPLEMENT",
        target_handler="TDDOrchestrator",
        dor_confidence=0.85,
        scope="MODULE",
        key_entities=["user_authentication.py", "AuthService", "login()"],
        governance_rules=["CORE-008", "CORE-011", "CORE-012", "CORE-030", "CORE-038"],
        requires_tests=True,
        estimated_impact="high"
    )
    
    # Generate markdown
    markdown = reflection.to_markdown()
    
    print(markdown)
    print()
    print("=" * 80)
    print("✅ Business Principles now display with separate rows!")
    print("Format: **Principle Name** → Technical Term (CORE-ID)")
    print("=" * 80)


if __name__ == "__main__":
    demo_dor_display()
