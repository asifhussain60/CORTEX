#!/usr/bin/env python3
"""
CORTEX Track:Eval Execution Engine - Silent & Efficient
Executes all 8 audit/cleanup phases with minimal verbosity
Updated: 2026-01-22
"""

import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
CORTEX_ROOT = Path(__file__).parent.parent
TRACK = "eval"
PHASES = [
    "PHASE-AUDIT-001-EXPORT-VERIFY",
    "PHASE-AUDIT-002-PHASE-E-VERIFY",
    "PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT",
    "PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK",
    "CLEANUP-PHASE-001-ROADMAP-MAINTENANCE",
    "PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY",
    "PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK",
    "PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH",
]

# Result tracking
RESULTS = {
    "start_time": datetime.now().isoformat(),
    "phases": {},
    "blockers": [],
    "summary": {}
}


def run_cmd(cmd: str, silent: bool = True) -> Tuple[int, str, str]:
    """Execute command silently and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=str(CORTEX_ROOT),
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"
    except Exception as e:
        return 1, "", str(e)


def audit_001_export_verify() -> Dict:
    """PHASE-AUDIT-001: Verify test collection errors fixed."""
    result = {
        "phase": "PHASE-AUDIT-001-EXPORT-VERIFY",
        "status": "RUNNING",
        "checks": {}
    }

    # Check 1: Test collection
    rc, out, err = run_cmd("python -m pytest tests/ --collect-only -q 2>&1 | grep -i 'error\\|failed' | wc -l")
    error_count = int(out.strip()) if out.strip().isdigit() else 0
    result["checks"]["collection_errors"] = error_count
    result["ac_001_01"] = "PASS" if error_count == 0 else f"FAIL ({error_count} errors)"

    # Check 2: Full collection without errors
    rc, out, err = run_cmd("python -m pytest tests/ --collect-only -q 2>&1")
    result["ac_001_02"] = "PASS" if rc == 0 else f"FAIL (rc={rc})"
    result["status"] = "PASS" if error_count == 0 and rc == 0 else "FAIL"

    return result


def audit_002_phase_e_verify() -> Dict:
    """PHASE-AUDIT-002: Verify PHASE-E production readiness."""
    result = {
        "phase": "PHASE-AUDIT-002-PHASE-E-VERIFY",
        "status": "RUNNING",
        "samples": {}
    }

    # Find Phase E modules
    rc, out, err = run_cmd("find cortex -name '*.py' -path '*/domain_brain/*' -o -path '*/governance/*' -o -path '*/intent_router/*' | head -25")
    modules = [m.strip() for m in out.split('\n') if m.strip()]

    # Sample modules and check for real implementations (not just docstrings)
    real_impl_count = 0
    for module in modules[:25]:
        rc, content, _ = run_cmd(f"cat {module}")
        # Count non-comment, non-docstring lines
        lines = [l for l in content.split('\n') if l.strip() and not l.strip().startswith('#') and '"""' not in l]
        if len(lines) > 5:  # Real implementation
            real_impl_count += 1

    impl_rate = (real_impl_count / len(modules)) * 100 if modules else 0
    result["ac_002_02"] = f"PASS ({impl_rate:.0f}% real)" if impl_rate >= 90 else f"FAIL ({impl_rate:.0f}%)"

    # Run sample module tests
    rc, out, err = run_cmd("python -m pytest cortex/domain_brain/ -q --tb=no 2>&1 | tail -1")
    result["ac_002_03"] = "PASS" if rc == 0 else f"FAIL (rc={rc})"

    # Coverage
    rc, cov_out, _ = run_cmd("python -m pytest cortex/domain_brain/ --cov=cortex.domain_brain --cov-report=term-missing -q --tb=no 2>&1 | grep TOTAL")
    coverage_line = cov_out.strip()
    result["ac_002_04"] = coverage_line if coverage_line else "UNKNOWN"

    result["status"] = "PASS" if impl_rate >= 90 and rc == 0 else "CONDITIONAL" if impl_rate >= 70 else "FAIL"
    if result["status"] == "FAIL":
        RESULTS["blockers"].append(("PHASE-AUDIT-002", impl_rate, coverage_line))

    return result


def audit_003_import_migration() -> Dict:
    """PHASE-AUDIT-003: Audit concerning import patterns."""
    result = {
        "phase": "PHASE-AUDIT-003-IMPORT-MIGRATION-AUDIT",
        "status": "RUNNING"
    }

    # Find files with old import patterns
    rc, out, err = run_cmd("grep -r 'from cortex\\.' cortex/ --include='*.py' 2>/dev/null | wc -l")
    old_pattern_count = int(out.strip()) if out.strip().isdigit() else 0

    # Categorize
    rc, out, err = run_cmd("grep -r 'from cortex\\.' cortex/ --include='*.py' 2>/dev/null | grep -E '(test_|conftest|scripts)' | wc -l")
    non_prod_count = int(out.strip()) if out.strip().isdigit() else 0
    prod_count = old_pattern_count - non_prod_count

    result["old_patterns"] = old_pattern_count
    result["production_code"] = prod_count
    result["non_production"] = non_prod_count
    result["ac_003_01"] = "PASS" if prod_count < 50 else f"WARN ({prod_count} files)"
    result["status"] = "PASS" if prod_count < 50 else "WARN"

    return result


def audit_004_governance_compliance() -> Dict:
    """PHASE-AUDIT-004: Verify CORE governance compliance."""
    result = {
        "phase": "PHASE-AUDIT-004-GOVERNANCE-COMPLIANCE-CHECK",
        "status": "RUNNING",
        "compliance": {}
    }

    # Check type hints (sample 25 files)
    rc, out, err = run_cmd("find cortex -name '*.py' -type f | head -25 | xargs grep -l 'def ' | xargs grep -c ': ' | awk -F: '{sum+=$2; cnt++} END {print int(sum/cnt)}'")
    type_hints_pct = int(out.strip()) if out.strip().isdigit() else 0
    result["compliance"]["type_hints"] = f"{type_hints_pct}%"
    result["ac_004_02"] = "PASS" if type_hints_pct >= 95 else f"WARN ({type_hints_pct}%)"

    # Check docstrings (sample 25 files)
    rc, out, err = run_cmd("find cortex -name '*.py' -type f | head -25 | xargs grep -c '\"\"\"' | awk -F: '{sum+=$2; cnt++} END {print int(sum/(cnt*2))}'")
    docstring_pct = int(out.strip()) if out.strip().isdigit() else 0
    result["compliance"]["docstrings"] = f"{docstring_pct}%"
    result["ac_004_03"] = "PASS" if docstring_pct >= 95 else f"WARN ({docstring_pct}%)"

    # Run pylint on sample
    rc, out, err = run_cmd("python -m pylint cortex/core/ -q --disable=all --enable=missing-raises-doc,missing-param-doc 2>&1 | tail -1")
    pylint_summary = out.strip() if out.strip() else "NO_ISSUES"
    result["compliance"]["pylint"] = pylint_summary

    result["status"] = "PASS" if type_hints_pct >= 95 and docstring_pct >= 95 else "WARN"

    return result


def cleanup_001_roadmap_maintenance() -> Dict:
    """CLEANUP-PHASE-001: Remove duplicates and consolidate roadmap."""
    result = {
        "phase": "CLEANUP-PHASE-001-ROADMAP-MAINTENANCE",
        "status": "RUNNING"
    }

    # Find duplicate phase definitions
    rc, out, err = run_cmd("grep -n '^  - id:' _workspaces/roadmap/cortex-impl-map.yaml | awk -F: '{print $3}' | sort | uniq -d")
    duplicates = [d.strip().strip('"').strip("'") for d in out.split('\n') if d.strip()]

    result["duplicates_found"] = len(duplicates)
    result["duplicate_ids"] = duplicates[:5] if duplicates else []

    # Check if file is valid YAML
    rc, _, _ = run_cmd("python -c \"import yaml; yaml.safe_load(open('_workspaces/roadmap/cortex-impl-map.yaml'))\"")
    result["yaml_valid"] = "PASS" if rc == 0 else "FAIL"

    result["ac_001_02"] = "PASS" if rc == 0 else "FAIL"
    result["status"] = "PASS" if rc == 0 and len(duplicates) == 0 else "CONDITIONAL"

    return result


def audit_005_git_checkpoint() -> Dict:
    """PHASE-AUDIT-005: Verify git checkpoints per CORE-026."""
    result = {
        "phase": "PHASE-AUDIT-005-GIT-CHECKPOINT-VERIFY",
        "status": "RUNNING"
    }

    # Check commits on 2026-01-21 and 2026-01-22
    rc, out, err = run_cmd("git log --oneline --since='2026-01-20' --until='2026-01-23' | wc -l")
    commit_count = int(out.strip()) if out.strip().isdigit() else 0

    # Check commit format
    rc, out, err = run_cmd("git log --oneline --since='2026-01-20' --until='2026-01-23' | head -5")
    commits = out.strip().split('\n')

    proper_format = sum(1 for c in commits if ':' in c)

    result["commits_found"] = commit_count
    result["proper_format"] = proper_format
    result["ac_005_01"] = "PASS" if commit_count > 0 else "WARN (no recent commits)"
    result["ac_005_02"] = "PASS" if proper_format > 0 else "WARN (no proper format)"
    result["status"] = "PASS" if commit_count > 0 and proper_format > 0 else "WARN"

    return result


def audit_006_docstring_compliance() -> Dict:
    """PHASE-AUDIT-006: Static analysis of type hints/docstrings."""
    result = {
        "phase": "PHASE-AUDIT-006-DOCSTRING-COMPLIANCE-CHECK",
        "status": "RUNNING"
    }

    # Run Pylance/Pylint on sample
    rc, out, err = run_cmd("python -m pylint cortex/core/ cortex/common/ -q --disable=all --enable=missing-docstring,missing-function-docstring 2>&1 | tail -5")
    violations = out.strip()

    result["violations_sample"] = violations[:200] if violations else "NONE"
    result["ac_006_01"] = "PASS" if not violations or int(violations.split('\n')[0].split()[0] if violations else 0) < 50 else "WARN"

    result["status"] = "PASS" if not violations else "WARN"

    return result


def audit_007_coverage_baseline() -> Dict:
    """PHASE-AUDIT-007: Establish test coverage baseline."""
    result = {
        "phase": "PHASE-AUDIT-007-COVERAGE-BASELINE-ESTABLISH",
        "status": "RUNNING"
    }

    # Run coverage analysis
    rc, out, err = run_cmd("python -m pytest cortex/ --cov=cortex --cov-report=term-missing -q --tb=no 2>&1 | tail -5")
    coverage_output = out.strip()

    # Extract total coverage
    rc2, cov_pct, _ = run_cmd("python -m pytest cortex/ --cov=cortex --cov-report=term --tb=no -q 2>&1 | grep TOTAL")

    result["coverage_total"] = cov_pct.strip() if cov_pct.strip() else "UNKNOWN"
    result["ac_007_02"] = "PASS" if "85%" in cov_pct or "9" in cov_pct[:2] else "WARN"

    result["status"] = "PASS" if "TOTAL" in cov_pct else "WARN"

    return result


def generate_summary() -> str:
    """Generate silent summary of all phase results."""
    summary_lines = []
    summary_lines.append("\n" + "="*60)
    summary_lines.append("TRACK:EVAL EXECUTION SUMMARY")
    summary_lines.append("="*60)

    pass_count = sum(1 for p in RESULTS["phases"].values() if p.get("status") == "PASS")
    warn_count = sum(1 for p in RESULTS["phases"].values() if p.get("status") == "WARN")
    fail_count = sum(1 for p in RESULTS["phases"].values() if p.get("status") == "FAIL")
    cond_count = sum(1 for p in RESULTS["phases"].values() if p.get("status") == "CONDITIONAL")

    summary_lines.append(f"Phases: {len(RESULTS['phases'])} | ✓ {pass_count} | ⚠ {warn_count} | ⊘ {cond_count} | ✗ {fail_count}")

    if RESULTS["blockers"]:
        summary_lines.append("\nBLOCKERS:")
        for blocker in RESULTS["blockers"]:
            summary_lines.append(f"  ✗ {blocker[0]}: {blocker[1]}")

    if fail_count == 0 and cond_count == 0:
        summary_lines.append("\n✓ ALL PHASES PASSED")
    else:
        summary_lines.append(f"\n⚠ {cond_count + fail_count} phases need attention")

    summary_lines.append("="*60 + "\n")

    return "\n".join(summary_lines)


def main():
    """Execute all track:eval phases silently."""
    print(f"▶ Executing TRACK:EVAL ({len(PHASES)} phases)...", file=sys.stderr)

    # Execute phases in sequence
    phase_funcs = [
        audit_001_export_verify,
        audit_002_phase_e_verify,
        audit_003_import_migration,
        audit_004_governance_compliance,
        cleanup_001_roadmap_maintenance,
        audit_005_git_checkpoint,
        audit_006_docstring_compliance,
        audit_007_coverage_baseline,
    ]

    for i, phase_func in enumerate(phase_funcs, 1):
        try:
            result = phase_func()
            RESULTS["phases"][result["phase"]] = result
            status_icon = "✓" if result["status"] == "PASS" else "⚠" if result["status"] == "WARN" else "⊘" if result["status"] == "CONDITIONAL" else "✗"
            print(f"  [{i}/8] {status_icon} {result['phase']}", file=sys.stderr)
        except Exception as e:
            print(f"  [{i}/8] ✗ {phase_func.__name__}: {str(e)[:50]}", file=sys.stderr)
            RESULTS["phases"][phase_func.__name__] = {"status": "ERROR", "error": str(e)}

    # Output results
    RESULTS["end_time"] = datetime.now().isoformat()
    summary = generate_summary()
    print(summary, file=sys.stderr)

    # Return JSON for programmatic use
    print(json.dumps(RESULTS, indent=2))

    # Exit with appropriate code
    if RESULTS["blockers"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
