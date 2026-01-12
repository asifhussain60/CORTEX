#!/usr/bin/env python3
"""
Demonstration: CORTEX Response Header Injection System

Shows how the response template system injects the brain icon header,
copyright info, and Next Steps section into all user responses.

Run: python3 demo_header_injection.py

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrators.response_renderer import ResponseRenderer
from src.orchestrators.response_middleware import ResponseMiddleware


def demo_basic_response():
    """Demonstrate basic response with header and sections."""
    print("=" * 80)
    print("DEMO 1: Basic Response with Header and Sections")
    print("=" * 80)
    
    renderer = ResponseRenderer(templates_path="cortex-brain/response-templates-v4.yaml")
    
    result = {"message": "Operation completed"}
    context = {
        "version": "6.0.0",
        "operation_type": "TDD-Master",
        "summary": "Test-driven implementation of governance module completed successfully.",
        "outcomes": [
            "Governance merger implementation (AC-GOV-001) - 5/5 tests passing",
            "SKULL rule validation (AC-GOV-002) - all 23 rules enforced",
            "Phase 1 foundation at 60% completion (16/27 AC-IDs)"
        ],
        "in_progress": [
            "Audit infrastructure implementation",
            "State manager persistence layer"
        ],
        "next_steps": [
            "Run Phase 1 integration tests to validate governance pipeline",
            "Update progress-tracker.json with test evidence",
            "Proceed to Phase 2 when Phase 1 reaches 100%"
        ]
    }
    
    markdown = renderer.render(result, context=context)
    print(markdown)
    print()


def demo_with_warnings():
    """Demonstrate response with system message injection."""
    print("=" * 80)
    print("DEMO 2: Response with System Message Injection (Warnings)")
    print("=" * 80)
    
    renderer = ResponseRenderer(templates_path="cortex-brain/response-templates-v4.yaml")
    middleware = ResponseMiddleware()
    
    result = {"message": "Query completed"}
    context = {
        "version": "6.0.0",
        "operation_type": "Analysis",
        "summary": "Brittleness review identified 8 critical and 12 high-priority risks.",
        "outcomes": [
            "Identified YAML encoding corruption vulnerability (AC-BRITTLE-001)",
            "Found state persistence race condition (AC-RISK-003)",
            "Detected missing evidence validation (AC-DEBT-002)"
        ],
        "risks": [
            "YAML file corruption can silently corrupt governance rules",
            "No database backup before write operations",
            "Single-writer planning.db contention under load"
        ],
        "next_steps": [
            "Implement YAML repair mechanism (AC-BRITTLE-001)",
            "Add database backup before critical writes (AC-RISK-003)",
            "Implement evidence validation (AC-DEBT-002)"
        ],
        "token_usage_percentage": 82,
        "security_warnings": [
            "Audit logs may expose sensitive data in context fields",
            "Planning database readable by all processes (no encryption)"
        ],
        "session_id": "session-2026-01-12-demo"
    }
    
    # Render markdown
    rendered = renderer.render(result, context=context)
    
    # Inject system messages
    final = middleware.inject_system_messages(rendered, context)
    print(final)
    print()


def demo_minimal_response():
    """Demonstrate minimal response (instant tier)."""
    print("=" * 80)
    print("DEMO 3: Minimal Response (Instant Tier)")
    print("=" * 80)
    
    renderer = ResponseRenderer(templates_path="cortex-brain/response-templates-v4.yaml")
    
    result = {"message": "Status query"}
    context = {
        "version": "6.0.0",
        "operation_type": "Status",
        "summary": "CORTEX 6.0 Phase 1 at 60% completion.",
        "outcomes": [
            "Phase 1: 16 of 27 AC-IDs complete"
        ],
        "next_steps": [
            "Continue Phase 1 implementation"
        ]
    }
    
    markdown = renderer.render(result, context=context)
    print(markdown)
    print()


def demo_validation():
    """Show that all quality gates pass."""
    print("=" * 80)
    print("VALIDATION: Quality Gate Checks")
    print("=" * 80)
    
    renderer = ResponseRenderer(templates_path="cortex-brain/response-templates-v4.yaml")
    
    result = {"message": "Test"}
    context = {
        "version": "6.0.0",
        "operation_type": "Test",
        "summary": "Test response.",
        "outcomes": ["Test outcome"],
        "next_steps": ["Next step"]
    }
    
    markdown = renderer.render(result, context=context)
    
    # Check quality gates
    checks = {
        "🧠 Brain icon present": "🧠 CORTEX" in markdown,
        "Copyright present": "Copyright © 2025-2026" in markdown,
        "Author present": "**Author:** Asif Hussain" in markdown,
        "Version present": "**Version:**" in markdown,
        "Outcomes section": "✅ OUTCOMES" in markdown,
        "Next Steps section": "📋 NEXT STEPS" in markdown,
        "Proper order (header first)": markdown.startswith("# 🧠"),
        "Proper order (Next Steps last)": markdown.rstrip().endswith("Next step"),
    }
    
    print("\n✅ QUALITY GATE VALIDATION:\n")
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {check_name}")
    
    all_passed = all(checks.values())
    print(f"\n  Overall: {'✅ ALL GATES PASSED' if all_passed else '❌ SOME GATES FAILED'}\n")


if __name__ == "__main__":
    try:
        print("\n" + "=" * 80)
        print("CORTEX RESPONSE HEADER INJECTION SYSTEM - DEMONSTRATION")
        print("=" * 80 + "\n")
        
        demo_basic_response()
        demo_with_warnings()
        demo_minimal_response()
        demo_validation()
        
        print("=" * 80)
        print("DEMONSTRATION COMPLETE - All responses include:")
        print("  ✅ 🧠 Brain icon with CORTEX title")
        print("  ✅ Version, date, author, copyright")
        print("  ✅ Executive summary format (bullets, no prose)")
        print("  ✅ Mandatory Next Steps section")
        print("  ✅ System message injection (warnings, deprecations)")
        print("=" * 80)
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
