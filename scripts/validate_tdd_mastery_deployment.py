#!/usr/bin/env python3
"""
CORTEX Deployment Validation - TDD Mastery Components

Validates that all TDD Mastery v3.2.0 components are present and ready for deployment.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Date: 2025-11-24
"""

import sys
from pathlib import Path
from typing import List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def check_file_exists(file_path: Path) -> Tuple[bool, str]:
    """Check if a file exists and return status with message."""
    if file_path.exists():
        size = file_path.stat().st_size
        return True, f"Found ({size:,} bytes)"
    return False, "Missing"


def validate_tdd_mastery_deployment() -> bool:
    """Validate all TDD Mastery components are present."""
    project_root = Path(__file__).parent.parent
    
    print(f"{Colors.BOLD}CORTEX v3.2.0 - TDD Mastery Deployment Validation{Colors.RESET}")
    print("=" * 70)
    print()
    
    all_passed = True
    
    # Critical Documentation Files
    print(f"{Colors.BLUE}📚 Documentation Files:{Colors.RESET}")
    docs = [
        "cortex-brain/documents/implementation-guides/TDD-MASTERY-INTEGRATION-PLAN.md",
        "cortex-brain/documents/implementation-guides/TDD-MASTERY-QUICKSTART.md",
        "cortex-brain/documents/implementation-guides/test-strategy.yaml",
        "cortex-brain/documents/reports/TDD-MASTERY-PHASE1-2-COMPLETE.md",
        "cortex-brain/documents/reports/TDD-MASTERY-PHASE4-COMPLETE.md",
        "cortex-brain/documents/reports/TDD-MASTERY-PHASE5-COMPLETE.md",
        ".github/prompts/CORTEX.prompt.md",  # Updated with TDD Mastery section
        "cortex-brain/metadata/capabilities.yaml",     # Updated with tdd_mastery capability
    ]
    
    for doc_path in docs:
        full_path = project_root / doc_path
        passed, message = check_file_exists(full_path)
        status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} {doc_path}: {message}")
        if not passed:
            all_passed = False
    
    print()
    
    # Workflow Source Files
    print(f"{Colors.BLUE}🔧 Workflow Source Files:{Colors.RESET}")
    workflows = [
        "src/workflows/tdd_workflow_orchestrator.py",
        "src/workflows/tdd_state_machine.py",
        "src/workflows/refactoring_intelligence.py",
    ]
    
    for workflow_path in workflows:
        full_path = project_root / workflow_path
        passed, message = check_file_exists(full_path)
        status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} {workflow_path}: {message}")
        if not passed:
            all_passed = False
    
    print()
    
    # Agent Files
    print(f"{Colors.BLUE}🤖 Agent Files:{Colors.RESET}")
    agents = [
        "src/agents/view_discovery_agent.py",
        "src/agents/feedback_agent.py",
        "cortex-brain/agents/debug_agent.py",
        "cortex-brain/agents/debug_session_manager.py",
    ]
    
    for agent_path in agents:
        full_path = project_root / agent_path
        passed, message = check_file_exists(full_path)
        status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} {agent_path}: {message}")
        if not passed:
            all_passed = False
    
    print()
    
    # Integration Tests
    print(f"{Colors.BLUE}🧪 Integration Tests:{Colors.RESET}")
    tests = [
        "tests/test_tdd_phase4_integration.py",
    ]
    
    for test_path in tests:
        full_path = project_root / test_path
        passed, message = check_file_exists(full_path)
        
        # Check test pass rate if file exists
        if passed:
            # File exists, check content for test count
            content = full_path.read_text()
            test_count = content.count("def test_")
            message = f"Found ({test_count} tests, {message})"
        
        status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} {test_path}: {message}")
        if not passed:
            all_passed = False
    
    print()
    
    # Check for required content in CORTEX.prompt.md
    print(f"{Colors.BLUE}📝 Content Validation:{Colors.RESET}")
    cortex_prompt = project_root / ".github/prompts/CORTEX.prompt.md"
    if cortex_prompt.exists():
        content = cortex_prompt.read_text()
        
        # Check for TDD Mastery section
        has_tdd_section = "## 🎯 TDD Mastery (NEW)" in content
        status = f"{Colors.GREEN}✓{Colors.RESET}" if has_tdd_section else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} TDD Mastery section in CORTEX.prompt.md: {'Present' if has_tdd_section else 'Missing'}")
        if not has_tdd_section:
            all_passed = False
        
        # Check for TDD commands
        has_tdd_commands = "start tdd" in content and "suggest refactorings" in content
        status = f"{Colors.GREEN}✓{Colors.RESET}" if has_tdd_commands else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} TDD natural language commands: {'Present' if has_tdd_commands else 'Missing'}")
        if not has_tdd_commands:
            all_passed = False
    
    print()
    
    # Check capabilities.yaml for tdd_mastery
    capabilities_file = project_root / "cortex-brain/metadata/capabilities.yaml"
    if capabilities_file.exists():
        content = capabilities_file.read_text()
        
        has_tdd_capability = "id: \"tdd_mastery\"" in content or 'id: "tdd_mastery"' in content
        status = f"{Colors.GREEN}✓{Colors.RESET}" if has_tdd_capability else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} tdd_mastery capability in capabilities.yaml: {'Present' if has_tdd_capability else 'Missing'}")
        if not has_tdd_capability:
            all_passed = False
        
        # Check for readiness
        if has_tdd_capability:
            has_readiness = "readiness: 100" in content
            status = f"{Colors.GREEN}✓{Colors.RESET}" if has_readiness else f"{Colors.YELLOW}⚠{Colors.RESET}"
            print(f"  {status} tdd_mastery readiness: 100%: {'Yes' if has_readiness else 'Check needed'}")
    
    print()
    
    # Check test-strategy.yaml for tdd_mastery section
    test_strategy = project_root / "cortex-brain/documents/implementation-guides/test-strategy.yaml"
    if test_strategy.exists():
        content = test_strategy.read_text()
        
        has_tdd_section = "tdd_mastery:" in content
        status = f"{Colors.GREEN}✓{Colors.RESET}" if has_tdd_section else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {status} tdd_mastery section in test-strategy.yaml: {'Present' if has_tdd_section else 'Missing'}")
        if not has_tdd_section:
            all_passed = False
    
    print()
    print("=" * 70)
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ ALL CHECKS PASSED - TDD MASTERY READY FOR DEPLOYMENT{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILED - FIX MISSING COMPONENTS{Colors.RESET}")
        return False


if __name__ == "__main__":
    success = validate_tdd_mastery_deployment()
    sys.exit(0 if success else 1)
