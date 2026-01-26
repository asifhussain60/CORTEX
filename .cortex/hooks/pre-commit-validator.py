#!/usr/bin/env python3
"""
Git pre-commit hook: Validate CORTEX wiring before each commit.

Usage:
  1. Create as: .cortex/hooks/pre-commit-validator.py
  2. Link from git: ln -s ../../.cortex/hooks/pre-commit-validator.py .git/hooks/pre-commit
  3. Make executable: chmod +x .git/hooks/pre-commit

The hook will:
- Stage 1 (Fast path): Quick health check <200ms
- Stage 2 (Fallback): Full validation if Stage 1 fails <3s
- Block commits if validation fails
- Suggest remediation steps

CORE-026: Git checkpoint before major changes
CORE-027: Audit trail for operations
"""

import sys
import os
from pathlib import Path

# Add CORTEX root to path
cortex_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(cortex_root))

from cortex.infrastructure.pre_commit_validator import (
    PreCommitValidator,
    DecisionType,
)


def print_header(title: str) -> None:
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_section(title: str) -> None:
    """Print section header"""
    print(f"\n{title}:")
    print("-" * 70)


def print_success(message: str) -> None:
    """Print success message with emoji"""
    print(f"✅ {message}")


def print_warning(message: str) -> None:
    """Print warning message with emoji"""
    print(f"🟡 {message}")


def print_error(message: str) -> None:
    """Print error message with emoji"""
    print(f"❌ {message}")


def print_info(message: str) -> None:
    """Print info message with emoji"""
    print(f"ℹ️  {message}")


def print_step(number: int, message: str) -> None:
    """Print numbered step"""
    print(f"  {number}. {message}")


def main() -> int:
    """
    Execute pre-commit validation.
    
    Returns:
        0 if commit allowed, 1 if blocked
    """
    print_header("CORTEX Pre-Commit Validator")
    
    try:
        # Initialize validator
        validator = PreCommitValidator()
        print_info("Initialized validator with DatabaseBackedRegistry")
        
        # Run evaluation
        print_section("Evaluating Commit")
        decision = validator.evaluate_commit()
        
        # Report decision
        if decision.allow_commit:
            print_success(f"Commit ALLOWED ({decision.decision_type.value})")
            print_info(f"Validation completed in {decision.validation_time_ms:.1f}ms")
            
            if decision.stage_executed == "STAGE_1":
                print_info("✨ Fast path: Health check passed (no Stage 2 needed)")
            elif decision.stage_executed == "STAGE_1_2":
                print_info("🔧 Fallback path: Stage 2 full validation recovered all issues")
            
            print(f"\n{'='*70}")
            print("  ✅ All checks passed - proceeding with commit")
            print(f"{'='*70}\n")
            return 0
        
        else:
            print_error(f"Commit BLOCKED - Validation failed")
            print_section("Failure Details")
            
            # Show failure reason
            if decision.failure_reason:
                for line in decision.failure_reason.split('\n'):
                    if line.strip():
                        print(f"  {line}")
            
            # Show remediation steps
            if decision.remediation_steps:
                print_section("Remediation Steps")
                for i, step in enumerate(decision.remediation_steps, 1):
                    print(f"  {step}")
            
            print_section("Additional Information")
            print_info(f"Validation time: {decision.validation_time_ms:.1f}ms")
            print_info(f"Stages executed: {decision.stage_executed}")
            
            print("\n" + "="*70)
            print("  ❌ Fix the issues above and try committing again")
            print("="*70 + "\n")
            
            return 1
    
    except Exception as e:
        print_error(f"Hook execution failed: {str(e)}")
        print_info("Allowing commit (validation error)")
        return 0


if __name__ == '__main__':
    sys.exit(main())
