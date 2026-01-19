#!/usr/bin/env python3
"""Verification script for CORTEX adoption (AC-UNIFIED-DEPLOY-002-02)."""

import os
import sys
import json
from pathlib import Path
from typing import Tuple, List


class CORTEXVerifier:
    """Verifies CORTEX installation and configuration."""

    CORTEX_PROMPT_PATH = ".github/prompts/CORTEX.prompt"
    REQUIRED_SECTIONS = [
        "SYSTEM IDENTITY",
        "ORCHESTRATORS",
        "MCP TOOLS REGISTRY",
        "GOVERNANCE RULES",
    ]

    def __init__(self, repo_root: str = "."):
        """Initialize verifier."""
        self.repo_root = Path(repo_root)
        self.results: List[Tuple[str, bool, str]] = []

    def run_all_checks(self) -> Tuple[bool, List[str]]:
        """Run all verification checks."""
        all_passed = True

        # Check 1: File placement
        file_ok, file_msg = self.check_file_placement()
        self.results.append(("File Placement", file_ok, file_msg))
        all_passed = all_passed and file_ok

        if not file_ok:
            # Can't proceed without file
            return False, self.format_results()

        # Check 2: Syntax validation
        syntax_ok, syntax_msg = self.check_syntax_validity()
        self.results.append(("Syntax Valid", syntax_ok, syntax_msg))
        all_passed = all_passed and syntax_ok

        # Check 3: Required sections
        sections_ok, sections_msg = self.check_required_sections()
        self.results.append(("Required Sections", sections_ok, sections_msg))
        all_passed = all_passed and sections_ok

        # Check 4: Version detection
        version_ok, version_msg = self.check_version_detection()
        self.results.append(("Version Detected", version_ok, version_msg))

        # Check 5: Orchestrator definitions
        orch_ok, orch_msg = self.check_orchestrator_definitions()
        self.results.append(("Orchestrators", orch_ok, orch_msg))
        all_passed = all_passed and orch_ok

        # Check 6: MCP tool registry
        tools_ok, tools_msg = self.check_mcp_tools()
        self.results.append(("MCP Tools", tools_ok, tools_msg))
        all_passed = all_passed and tools_ok

        return all_passed, self.format_results()

    def check_file_placement(self) -> Tuple[bool, str]:
        """Check if CORTEX.prompt is in correct location."""
        cortex_path = self.repo_root / self.CORTEX_PROMPT_PATH
        if cortex_path.exists():
            return True, f"✓ Found at {self.CORTEX_PROMPT_PATH}"
        else:
            return False, f"✗ Not found at {self.CORTEX_PROMPT_PATH} (required)"

    def check_syntax_validity(self) -> Tuple[bool, str]:
        """Check if CORTEX.prompt loads without syntax errors."""
        cortex_path = self.repo_root / self.CORTEX_PROMPT_PATH
        try:
            with open(cortex_path, "r") as f:
                content = f.read()
            # Basic syntax check (not full parse, just structure)
            if "SYSTEM IDENTITY" in content and "---" in content:
                return True, "✓ Syntax valid"
            else:
                return False, "✗ Invalid format or missing markers"
        except Exception as e:
            return False, f"✗ Error reading file: {str(e)}"

    def check_required_sections(self) -> Tuple[bool, str]:
        """Check for required sections in CORTEX.prompt."""
        cortex_path = self.repo_root / self.CORTEX_PROMPT_PATH
        try:
            with open(cortex_path, "r") as f:
                content = f.read()
            missing = [s for s in self.REQUIRED_SECTIONS if s not in content]
            if not missing:
                return True, f"✓ All {len(self.REQUIRED_SECTIONS)} required sections present"
            else:
                return False, f"✗ Missing sections: {', '.join(missing)}"
        except Exception as e:
            return False, f"✗ Error: {str(e)}"

    def check_version_detection(self) -> Tuple[bool, str]:
        """Detect and report CORTEX version."""
        cortex_path = self.repo_root / self.CORTEX_PROMPT_PATH
        try:
            with open(cortex_path, "r") as f:
                content = f.read()
            # Extract version
            for line in content.split("\n"):
                if "Version:" in line:
                    version = line.split("Version:")[-1].strip().split()[0]
                    return True, f"✓ CORTEX v{version} detected"
            return False, "✗ Version not found in prompt"
        except Exception as e:
            return False, f"✗ Error: {str(e)}"

    def check_orchestrator_definitions(self) -> Tuple[bool, str]:
        """Verify orchestrator definitions are present."""
        cortex_path = self.repo_root / self.CORTEX_PROMPT_PATH
        try:
            with open(cortex_path, "r") as f:
                content = f.read()
            orchestrators = [
                "Master Orchestrator",
                "LENS Pipeline",
                "ResponseComposer",
                "ContextSwitcher",
            ]
            found = [o for o in orchestrators if o in content]
            if len(found) >= 3:
                return True, f"✓ {len(found)}/{len(orchestrators)} orchestrators defined"
            else:
                return False, f"✗ Only {len(found)}/{len(orchestrators)} orchestrators found"
        except Exception as e:
            return False, f"✗ Error: {str(e)}"

    def check_mcp_tools(self) -> Tuple[bool, str]:
        """Verify MCP tools registry is present."""
        cortex_path = self.repo_root / self.CORTEX_PROMPT_PATH
        try:
            with open(cortex_path, "r") as f:
                content = f.read()
            tools = [
                "file_search",
                "grep_search",
                "read_file",
                "replace_string_in_file",
            ]
            found = sum(1 for t in tools if t in content)
            if found >= 3:
                return True, f"✓ {found}/{len(tools)} core tools registered"
            else:
                return False, f"✗ Only {found}/{len(tools)} core tools registered"
        except Exception as e:
            return False, f"✗ Error: {str(e)}"

    def format_results(self) -> List[str]:
        """Format results for display."""
        lines = [
            "\n╔════════════════════════════════════════════════════════╗",
            "║           CORTEX Verification Report                   ║",
            "╚════════════════════════════════════════════════════════╝\n",
        ]

        all_passed = True
        for check_name, passed, message in self.results:
            status = "✓" if passed else "✗"
            lines.append(f"{status} {check_name:.<40} {message}")
            all_passed = all_passed and passed

        lines.append("\n" + "=" * 58)
        if all_passed:
            lines.append("✓ CORTEX installation verified and working correctly!")
        else:
            lines.append("✗ Some checks failed. See above for details.")
        lines.append("=" * 58 + "\n")

        return lines


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify CORTEX installation in current repo"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository root path (default: current directory)",
    )

    args = parser.parse_args()

    verifier = CORTEXVerifier(args.repo)
    all_passed, results = verifier.run_all_checks()

    for line in results:
        print(line)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
