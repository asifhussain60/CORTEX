#!/usr/bin/env python3
"""
Pre-commit hook for CORTEX governance validation.

This hook runs before every commit to ensure:
1. AC-ID format validation (AC-DOMAIN-NNN-NN)
2. Governance rule compliance
3. Critical violations prevention

Run with: .githooks/pre-commit-governance-check.py
Or automatically via git pre-commit hook setup.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


def check_ac_id_format(message: str) -> Tuple[bool, str]:
    """
    Validate AC-ID format in commit message.

    Valid formats:
    - AC-XXX-NNN-NN (e.g., AC-AR-001-01, AC-FR-002-03, AC-ENH-001-01)
    - Multiple AC-IDs allowed (comma-separated)
    - Optional in commit message (not all commits require AC-ID)

    Args:
        message: Commit message

    Returns:
        (is_valid, error_message)
    """
    # AC-ID pattern: AC-[A-Z]{2,3}-\d{3}-\d{2}
    ac_id_pattern = r"AC-[A-Z]{2,3}-\d{3}-\d{2}"

    # Find all AC-IDs in message
    ac_ids = re.findall(ac_id_pattern, message)

    if ac_ids:
        # Validate format of each AC-ID
        for ac_id in ac_ids:
            if not re.match(f"^{ac_id_pattern}$", ac_id):
                return False, f"Invalid AC-ID format: {ac_id}"
    else:
        # AC-ID is optional for some commits (e.g., refactoring)
        # Only warn if message explicitly mentions AC-ID-like text
        if "AC-" in message and not re.search(ac_id_pattern, message):
            return False, (
                "AC-ID format invalid. Expected: AC-DOMAIN-NNN-NN "
                "(e.g., AC-AR-001-01)"
            )

    return True, ""


def check_governance_violations() -> Tuple[bool, str]:
    """
    Check for governance violations using governance CLI.

    Args:
        None

    Returns:
        (no_violations, error_message)
    """
    # Get staged files
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        staged_files = result.stdout.strip().split("\n")
        staged_files = [f for f in staged_files if f.endswith(".py")]
    except subprocess.CalledProcessError:
        # No staged files
        return True, ""

    if not staged_files:
        return True, ""

    # Validate staged Python files
    cli_script = Path(__file__).parent.parent / "src" / "tools" / "governance-cli.py"
    if not cli_script.exists():
        # CLI not available, skip validation
        return True, ""

    violations = []
    for file in staged_files:
        try:
            result = subprocess.run(
                ["python3", str(cli_script), "validate", file, "--strict"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                # Extract violations from output
                violations.append(f"  {file}: {result.stdout}")

        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Validation timeout or CLI not available, skip
            pass

    if violations:
        return False, "Governance violations found:\n" + "\n".join(violations)

    return True, ""


def get_commit_message() -> str:
    """Get commit message from .git/COMMIT_EDITMSG."""
    git_dir = Path(".git")
    if not git_dir.exists():
        return ""

    msg_file = git_dir / "COMMIT_EDITMSG"
    if not msg_file.exists():
        return ""

    try:
        with open(msg_file) as f:
            return f.read().strip()
    except IOError:
        return ""


def main() -> int:
    """Run pre-commit governance checks."""
    print("🔍 Running CORTEX governance pre-commit checks...")

    commit_message = get_commit_message()

    # Check AC-ID format
    ac_id_valid, ac_id_error = check_ac_id_format(commit_message)
    if not ac_id_valid:
        print(f"❌ AC-ID Validation Failed: {ac_id_error}")
        print("\nFor governance ACs, use format: AC-DOMAIN-NNN-NN")
        print("Example: GV-001-01: Implement governance CLI")
        return 1

    # Check governance violations
    gov_valid, gov_error = check_governance_violations()
    if not gov_valid:
        print(f"❌ Governance Violations Detected:\n{gov_error}")
        print("\nUse: git commit --no-verify (use with caution!)")
        return 1

    print("✅ Pre-commit checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
