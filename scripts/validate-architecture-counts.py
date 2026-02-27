#!/usr/bin/env python3
"""
validate-architecture-counts.py
================================
CORTEX Architecture Count Validator — CORE-035 / CORE-064

Reads canonical counts from cortex-registry/config/architecture-constants.yaml
and verifies all .md prompt/agent files contain matching values.

Exits 0 if clean, non-zero on any mismatch.

Usage:
    python3 scripts/validate-architecture-counts.py           # validate only
    python3 scripts/validate-architecture-counts.py --fix     # auto-fix mismatches
    python3 scripts/validate-architecture-counts.py --report  # summary table only

Pre-commit hook:
    Configured in .pre-commit-config.yaml as a local hook.
    Runs automatically on every `git commit`.

AC_START: AC-VALIDATE-COUNTS-{timestamp}
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
CONSTANTS_FILE = REPO_ROOT / "cortex-registry" / "config" / "architecture-constants.yaml"

# Files that are CANONICAL (authoritative sources — allowed to define counts)
# All other files referencing counts must match these.
CANONICAL_FILES = {
    ".github/prompts/cortex-architect.prompt.md",   # header counts
    ".github/agents/core/cortex-meta-auditor.md",   # check table counts
}

# Lines containing these substrings are intentional examples / design prose —
# the validator skips count extraction on them to avoid false positives.
FALSE_POSITIVE_SUBSTRINGS = [
    "orchestrator ≠",          # design principle: "1 orchestrator ≠ 1 MCP tool"
    "1 MCP tool",              # same design principle sentence
    "28 MCP tools",            # intentional stale example in meta-auditor code fence
    "25 MCP tools",            # intentional stale example in meta-auditor code fence
    "24 MCP tools",            # intentional stale example in meta-auditor code fence
    "24 orchestrators",        # intentional stale example in meta-auditor code fence
    "120 orchestrators",       # intentional stale example in meta-auditor code fence
    "(28 registered)",         # canonical format: "39 MCP Tools (28 registered)" — 39 is target, 28 is active
    "28 registered",           # canonical: registered count clarification present on same line
    "39 target",               # canonical: "28 registered (39 target)" variant
    "28 Registered",           # case variant of canonical format
    "39 MCP tools (28",        # canonical compound pattern
    "canonical is 28",         # meta-auditor stale-detection prose
    "canonical is 39",         # meta-auditor stale-detection prose
    "35 CORE rules\" (must",   # meta-auditor stale-detection checklist (quoted examples)
    "Claimed '35 CORE'",       # drift-detection script searching for stale values
    "Claimed '27 wired'",      # drift-detection script searching for stale orchestrator counts
    "Claimed '26 MCP'",        # drift-detection script searching for stale MCP counts
    "grep -rn",                # drift-detection grep commands (searching for stale values)
]

# Directories to scan for count references
SCAN_DIRS = [
    ".github/prompts",
    ".github/agents",
]

# Stale count patterns that indicate a P0 violation (wrong number → right number)
# Format: (stale_pattern, correct_value, check_name)
STALE_PATTERNS: list[tuple[str, str, str]] = [
    # Orchestrator count — the most common drift
    (r"\b17\s+[Ww]ired\b", "51 wired", "orchestrator_count"),
    (r"[Oo]rchestrators\s*\(17\s+wired\)", "Orchestrators (51 wired)", "orchestrator_count_parens"),
    (r"\*\*Orchestrators:\*\*\s*17\s+wired", "**Orchestrators:** 51 wired", "orchestrator_bold"),
    (r"\b17\s+[Ww]ired\s+[Oo]rchestrators\b", "51 Wired Orchestrators", "orchestrator_count_full"),
    (r"\b27\s+[Ww]ired\b", "51 wired", "orchestrator_count_27"),
    # Stale MCP tool counts (24, 26 were pre-refactor)
    (r"\b24\s+[Pp]roduction\b", "28 registered", "mcp_tool_count_24"),
    (r"\b26\s+MCP\b", "28 registered MCP", "mcp_tool_count_26"),
    # Stale lower rule counts
    (r"\b30\s+CORE\b", "38 CORE", "core_rule_count_30"),
    (r"\b32\s+CORE\b", "38 CORE", "core_rule_count_32"),
    (r"\b35\s+CORE\b", "38 CORE", "core_rule_count_35"),
]

# Grep patterns to find count-bearing lines in any scanned file
COUNT_GREP_PATTERNS = [
    (r"\d+\s+[Ww]ired\s+[Oo]rchestrators?", "orchestrators_wired", 51),
    (r"[Oo]rchestrators?\s*\(\d+\s+wired\)", "orchestrators_wired_parens", 51),
    (r"[Oo]rchestrators?:\s*\*\*\d+\s+wired\*\*", "orchestrators_wired_bold", 51),
    (r"\d+\s+MCP\s+[Tt]ools?\b", "mcp_tools_active", 28),
    (r"MCP\s+[Tt]ools?\s*\(\d+", "mcp_tools_parens", 28),
    (r"\d+\s+CORE\s+[Rr]ules?\b", "core_rules_active", 38),
    (r"\bMCP\s+[Tt]ools?\s+\(\d+\s+active\)", "mcp_tools_active_parens", 28),
]


# ── Loader ────────────────────────────────────────────────────────────────────

def load_constants() -> dict:
    """Load architecture constants from YAML truth source."""
    if not CONSTANTS_FILE.exists():
        print(f"ERROR: Constants file not found: {CONSTANTS_FILE}", file=sys.stderr)
        sys.exit(1)
    with open(CONSTANTS_FILE) as f:
        data = yaml.safe_load(f)
    return data.get("architecture", {})


# ── Scanner ───────────────────────────────────────────────────────────────────

def scan_files() -> list[Path]:
    """Return all .md files in SCAN_DIRS."""
    files: list[Path] = []
    for scan_dir in SCAN_DIRS:
        scan_path = REPO_ROOT / scan_dir
        if scan_path.exists():
            files.extend(scan_path.rglob("*.md"))
    return sorted(files)


def relative(path: Path) -> str:
    """Return path relative to REPO_ROOT."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


# ── Validator ─────────────────────────────────────────────────────────────────

def validate_file(
    path: Path,
    constants: dict,
    violations: list[dict],
    fixable: list[dict],
) -> None:
    """Scan one file for stale count patterns and count mismatches."""
    text = path.read_text(encoding="utf-8")
    rel = relative(path)

    # Check 1: Stale hardcoded wrong numbers
    for stale_pattern, correct, check_name in STALE_PATTERNS:
        for match in re.finditer(stale_pattern, text):
            # Skip lines that are intentional examples / design prose
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            line_text = text[line_start:line_end if line_end != -1 else len(text)]
            if any(fp in line_text for fp in FALSE_POSITIVE_SUBSTRINGS):
                continue
            line_num = text[: match.start()].count("\n") + 1
            violations.append({
                "file": rel,
                "line": line_num,
                "check": check_name,
                "severity": "P0",
                "found": match.group(0).strip(),
                "expected": correct,
                "fixable": True,
                "pattern": stale_pattern,
                "replacement": correct,
            })
            fixable.append({
                "path": path,
                "pattern": stale_pattern,
                "replacement": correct,
            })

    # Check 2: Count-bearing lines — verify number matches constants
    expected_map = {
        "orchestrators_wired": constants.get("orchestrators_wired", 27),
        "orchestrators_wired_parens": constants.get("orchestrators_wired", 27),
        "orchestrators_wired_bold": constants.get("orchestrators_wired", 27),
        "mcp_tools_active": constants.get("mcp_tools_active", 26),
        "mcp_tools_parens": constants.get("mcp_tools_active", 26),
        "mcp_tools_active_parens": constants.get("mcp_tools_active", 26),
        "core_rules_active": constants.get("core_rules_active", 35),
    }

    for grep_pattern, check_name, _ in COUNT_GREP_PATTERNS:
        for match in re.finditer(grep_pattern, text):
            # Skip false-positive lines (design prose / intentional examples)
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", match.end())
            line_text = text[line_start:line_end if line_end != -1 else len(text)]
            if any(fp in line_text for fp in FALSE_POSITIVE_SUBSTRINGS):
                continue
            # Extract the number from the matched string
            numbers = re.findall(r"\d+", match.group(0))
            if not numbers:
                continue
            found_num = int(numbers[0])
            expected_num = expected_map.get(check_name, None)
            if expected_num is None:
                continue
            if found_num != expected_num:
                line_num = text[: match.start()].count("\n") + 1
                # Avoid double-reporting (already caught by STALE_PATTERNS)
                already_reported = any(
                    v["file"] == rel and v["line"] == line_num
                    for v in violations
                )
                if not already_reported:
                    violations.append({
                        "file": rel,
                        "line": line_num,
                        "check": check_name,
                        "severity": "P0",
                        "found": f"{found_num} (in: {match.group(0).strip()!r})",
                        "expected": str(expected_num),
                        "fixable": False,
                        "pattern": grep_pattern,
                        "replacement": None,
                    })


# ── Auto-Fix ──────────────────────────────────────────────────────────────────

def apply_fixes(fixable: list[dict]) -> int:
    """Apply regex replacements for all fixable violations. Returns fix count."""
    # Group by file path
    by_file: dict[Path, list[dict]] = {}
    for item in fixable:
        by_file.setdefault(item["path"], []).append(item)

    total_fixed = 0
    for path, fixes in by_file.items():
        text = path.read_text(encoding="utf-8")
        original = text
        for fix in fixes:
            text = re.sub(fix["pattern"], fix["replacement"], text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            fixed_count = len(fixes)
            total_fixed += fixed_count
            print(f"  ✅ Fixed {fixed_count} violation(s) in {relative(path)}")

    return total_fixed


# ── Reporter ──────────────────────────────────────────────────────────────────

def print_report(violations: list[dict], constants: dict) -> None:
    """Print violation table."""
    if not violations:
        print("\n✅ Architecture count validation: CLEAN")
        print(f"   Canonical values: {constants.get('orchestrators_wired')} orchestrators · "
              f"{constants.get('mcp_tools_active')} MCP tools · "
              f"{constants.get('core_rules_active')} CORE rules · "
              f"{constants.get('audit_production_checks')}-Point audit · "
              f"{constants.get('meta_audit_checks')} meta-checks")
        return

    p0 = [v for v in violations if v["severity"] == "P0"]
    print(f"\n⛔ Architecture count validation: {len(violations)} violation(s) — {len(p0)} P0")
    print(f"   Truth source: {relative(CONSTANTS_FILE)}\n")

    # Table header
    col_w = [5, 55, 30, 30, 6]
    header = f"{'Sev':<{col_w[0]}} {'File:Line':<{col_w[1]}} {'Found':<{col_w[2]}} {'Expected':<{col_w[3]}} {'Fix?':<{col_w[4]}}"
    print(header)
    print("-" * sum(col_w))

    for v in violations:
        file_line = f"{v['file']}:{v['line']}"
        fix_flag = "✅ auto" if v["fixable"] else "🟡 manual"
        print(
            f"{v['severity']:<{col_w[0]}} "
            f"{file_line:<{col_w[1]}} "
            f"{v['found']:<{col_w[2]}} "
            f"{v['expected']:<{col_w[3]}} "
            f"{fix_flag:<{col_w[4]}}"
        )

    fixable_count = sum(1 for v in violations if v["fixable"])
    print(f"\n  Fixable automatically: {fixable_count}/{len(violations)}")
    print("  Run with --fix to apply auto-fixes.")


# ── Entry Point ───────────────────────────────────────────────────────────────

def main() -> int:
    """Main entry point. Returns exit code."""
    parser = argparse.ArgumentParser(
        description="CORTEX Architecture Count Validator (CORE-035)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix all fixable violations (regex replacement)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Print summary table only, always exit 0",
    )
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Validate a single file instead of full scan",
    )
    args = parser.parse_args()

    constants = load_constants()
    violations: list[dict] = []
    fixable: list[dict] = []

    if args.file:
        target = Path(args.file)
        if not target.exists():
            print(f"ERROR: File not found: {target}", file=sys.stderr)
            return 1
        files = [target]
    else:
        files = scan_files()

    print(f"🔎 Scanning {len(files)} file(s) against {relative(CONSTANTS_FILE)} ...")

    for f in files:
        validate_file(f, constants, violations, fixable)

    if args.fix and fixable:
        print(f"\n🔧 Applying {len(fixable)} auto-fix(es) ...")
        fixed = apply_fixes(fixable)
        print(f"   Total fixed: {fixed}")
        # Re-scan after fix to confirm clean
        violations.clear()
        fixable.clear()
        for f in files:
            validate_file(f, constants, violations, fixable)

    print_report(violations, constants)

    if args.report:
        return 0

    p0_count = sum(1 for v in violations if v["severity"] == "P0")
    return 1 if p0_count > 0 else 0


if __name__ == "__main__":
    # AC_COMPLETE: AC-VALIDATE-COUNTS-{timestamp} ✅
    sys.exit(main())
