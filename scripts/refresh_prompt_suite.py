#!/usr/bin/env python3
"""
CORTEX Prompt Suite Refresh Playbook
=====================================
Repeatable script to regenerate copilot-instructions.md, prompts, and agents
based on live architecture introspection + SQLite audit logs.

Usage:
    python3 scripts/refresh_prompt_suite.py              # Full refresh
    python3 scripts/refresh_prompt_suite.py --dry-run     # Preview changes only
    python3 scripts/refresh_prompt_suite.py --db-cleanup   # SQLite cleanup only
    python3 scripts/refresh_prompt_suite.py --db-cleanup-loop --loop-interval-seconds 300
    python3 scripts/refresh_prompt_suite.py --counts-only  # Just show live counts

Governance: CORE-002 (inline output), CORE-049 (silent autonomous)
Author: Asif Hussain
"""

import argparse
import glob
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─── Constants ──────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
CORTEX_RUNTIME = ROOT / ".cortex-runtime"
GITHUB_DIR = ROOT / ".github"
COPILOT_INSTRUCTIONS = GITHUB_DIR / "copilot-instructions.md"
PROMPTS_DIR = GITHUB_DIR / "prompts"
AGENTS_DIR = GITHUB_DIR / "agents"
AGENT_INDEX = AGENTS_DIR / "AGENT-INDEX.md"
TEMPLATES_DIR = GITHUB_DIR / "templates"
REGISTRY_DIR = ROOT / "cortex-registry"
MASTER_YAML = REGISTRY_DIR / "cortex-master.yaml"

# SQLite databases managed by CORTEX
# Phase 104: Consolidated from 9 → 7 databases (deleted 2 empty ghost DBs:
#   traces/governance.db (0 rows) and state/cortex_brain/state/governance.db (0 rows))
SQLITE_DATABASES = {
    "orchestrator-traces": CORTEX_RUNTIME / "traces" / "orchestrator-traces.db",
    "rca-store": CORTEX_RUNTIME / "rca" / "rca_store.db",
    "audit": CORTEX_RUNTIME / "audit.db",
    "governance": CORTEX_RUNTIME / "governance.db",
    "conversations": CORTEX_RUNTIME / "state" / "conversations.db",
    "wiring-audit": CORTEX_RUNTIME / "wiring" / "contract_validation_audit.db",
    "intelligence-audit": CORTEX_RUNTIME / "intelligence" / "intelligence_audit.db",
}

# Retention policy (days)
RETENTION_DAYS = 30
RETENTION_DAYS_CONVERSATIONS = 90

# ─── Architecture Introspection ─────────────────────────────────────────────


def count_orchestrator_files() -> Dict[str, int]:
    """Count orchestrator .py files per tier (excluding __init__.py, __pycache__).

    Uses rglob to recursively count all .py files in each domain subdirectory,
    capturing nested modules (e.g., core/strategies/, support/debugging/).
    Also counts top-level .py files directly in cortex/orchestrators/.
    """
    tiers = {}
    orch_dir = ROOT / "cortex" / "orchestrators"
    # Count top-level .py files (not in any subdomain)
    top_level = [
        f for f in orch_dir.glob("*.py")
        if f.name != "__init__.py"
    ]
    if top_level:
        tiers["_top_level"] = len(top_level)
    # All known domains — use rglob for all to capture nested subdirectories
    all_domains = [
        "core", "domain", "support", "git", "health",
        "intelligence", "persona", "registry", "response",
        "strategies", "synthesis", "tools", "validation", "workflow",
    ]
    for domain_name in all_domains:
        domain_path = orch_dir / domain_name
        if domain_path.is_dir():
            py_files = [
                f for f in domain_path.rglob("*.py")
                if f.name != "__init__.py"
            ]
            tiers[domain_name] = len(py_files)
    return tiers


def count_mcp_tools_registered() -> int:
    """Count MCP tools registered in mcp_registry.py."""
    registry_path = ROOT / "cortex" / "mcp" / "mcp_registry.py"
    if not registry_path.exists():
        return 0
    content = registry_path.read_text()
    return len(re.findall(r'"cortex_\w+"', content))


def count_mcp_tool_files() -> int:
    """Count MCP tool files in cortex/mcp/tools/ (recursive, including toolkit/)."""
    tools_dir = ROOT / "cortex" / "mcp" / "tools"
    if not tools_dir.is_dir():
        return 0
    return len([
        f for f in tools_dir.rglob("*.py")
        if f.name not in ("__init__.py", "_shared.py", "tool_helpers.py")
    ])


def count_tests() -> Optional[int]:
    """Count collected tests via pytest --collect-only (fast)."""
    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/", "--collect-only", "-q",
             "--no-header", "-p", "no:xdist"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=60
        )
        match = re.search(r"(\d+)\s+tests?\s+collected", result.stdout)
        if match:
            return int(match.group(1))
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def count_core_rules() -> int:
    """Count governance YAML files in cortex-registry/core/."""
    core_dir = REGISTRY_DIR / "core"
    if not core_dir.is_dir():
        return 0
    return len(list(core_dir.rglob("*.yaml"))) + len(list(core_dir.rglob("*.yml")))


def count_intent_types() -> List[str]:
    """Extract IntentType enum values from canonical_enums.py."""
    enums_file = ROOT / "cortex" / "models" / "canonical_enums.py"
    if not enums_file.exists():
        return []
    content = enums_file.read_text()
    return re.findall(r'(\w+)\s*=\s*"(\w+)"', content.split("class IntentType")[1].split("class ")[0]) if "class IntentType" in content else []


def count_phases_completed() -> int:
    """Count completed phases."""
    completed_dir = REGISTRY_DIR / "planning" / "phases" / "completed"
    if not completed_dir.is_dir():
        return 0
    return len(list(completed_dir.glob("*.yaml")))


def count_phases_planned() -> int:
    """Count planned phases."""
    planned_dir = REGISTRY_DIR / "planning" / "phases" / "planned"
    if not planned_dir.is_dir():
        return 0
    return len([f for f in planned_dir.glob("*.yaml") if not f.name.startswith("_")])


def get_master_yaml_lines() -> int:
    """Get line count of cortex-master.yaml."""
    if not MASTER_YAML.exists():
        return 0
    return len(MASTER_YAML.read_text().splitlines())


def list_prompt_files() -> List[str]:
    """List all .prompt.md files."""
    return [f.name for f in PROMPTS_DIR.glob("*.prompt.md")] if PROMPTS_DIR.is_dir() else []


def list_agent_files() -> Dict[str, List[str]]:
    """List all agent .md files by subdirectory."""
    agents = {}
    if not AGENTS_DIR.is_dir():
        return agents
    for subdir in AGENTS_DIR.iterdir():
        if subdir.is_dir() and subdir.name not in ("__pycache__",):
            md_files = [f.name for f in subdir.glob("*.md")]
            if md_files:
                agents[subdir.name] = sorted(md_files)
    return agents


def list_sqlite_databases() -> Dict[str, Dict[str, Any]]:
    """Inventory all SQLite databases with size, tables, row counts."""
    db_info = {}
    for name, path in SQLITE_DATABASES.items():
        if path.exists():
            size_kb = path.stat().st_size / 1024
            tables = {}
            try:
                conn = sqlite3.connect(str(path))
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                for (table_name,) in cursor.fetchall():
                    try:
                        row_count = conn.execute(
                            f"SELECT COUNT(*) FROM [{table_name}]"
                        ).fetchone()[0]
                        tables[table_name] = row_count
                    except sqlite3.OperationalError:
                        tables[table_name] = -1
                conn.close()
            except sqlite3.DatabaseError:
                tables = {"ERROR": "corrupt or locked"}
            db_info[name] = {"path": str(path), "size_kb": round(size_kb, 1), "tables": tables}
        else:
            db_info[name] = {"path": str(path), "size_kb": 0, "tables": {}, "missing": True}
    # Check for stray .db files outside .cortex-runtime
    stray = []
    for db_file in ROOT.rglob("*.db"):
        rel = db_file.relative_to(ROOT)
        if not str(rel).startswith(".cortex-runtime") and not str(rel).startswith(".git"):
            stray.append(str(rel))
    if stray:
        db_info["_stray_databases"] = {"paths": stray}
    return db_info


# ─── SQLite Cleanup ─────────────────────────────────────────────────────────


def cleanup_sqlite_databases(dry_run: bool = False) -> Dict[str, Any]:
    """
    Clean up SQLite databases:
    1. Enforce 30-day retention on trace/audit tables
    2. Delete orphaned AC_START records
    3. VACUUM all databases
    4. Remove stray .db files outside .cortex-runtime
    """
    results = {}

    # Skip cleanup if guard is set
    if os.environ.get("CORTEX_DISABLE_DB_CLEANUP", "").lower() == "true":
        return {"skipped": "CORTEX_DISABLE_DB_CLEANUP=true"}

    for name, path in SQLITE_DATABASES.items():
        if not path.exists():
            continue

        db_result = {"path": str(path), "actions": []}
        try:
            conn = sqlite3.connect(str(path))

            # 1. Retention enforcement — delete records older than RETENTION_DAYS
            retention = RETENTION_DAYS_CONVERSATIONS if "conversations" in name else RETENTION_DAYS
            cutoff = (datetime.now() - timedelta(days=retention)).isoformat()

            # Find timestamp columns
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            for (table_name,) in cursor.fetchall():
                try:
                    col_info = conn.execute(
                        f"PRAGMA table_info([{table_name}])"
                    ).fetchall()
                    ts_cols = [
                        c[1] for c in col_info
                        if any(kw in c[1].lower() for kw in
                               ("timestamp", "created_at", "started_at", "date", "time"))
                    ]
                    for ts_col in ts_cols:
                        count_before = conn.execute(
                            f"SELECT COUNT(*) FROM [{table_name}]"
                        ).fetchone()[0]
                        if not dry_run:
                            conn.execute(
                                f"DELETE FROM [{table_name}] WHERE [{ts_col}] < ?",
                                (cutoff,)
                            )
                        count_after = conn.execute(
                            f"SELECT COUNT(*) FROM [{table_name}]"
                        ).fetchone()[0] if not dry_run else count_before
                        deleted = count_before - count_after
                        if deleted > 0 or dry_run:
                            db_result["actions"].append(
                                f"{'[DRY-RUN] ' if dry_run else ''}Retention: {table_name}.{ts_col} "
                                f"— {deleted} rows {'would be ' if dry_run else ''}deleted (>{retention}d)"
                            )
                except sqlite3.OperationalError:
                    pass

            # 2. Orphaned AC_START cleanup (orchestrator-traces only)
            if "traces" in name:
                for table_name in ["audit_stage_log", "trace_master", "trace_interaction"]:
                    try:
                        orphans = conn.execute(
                            f"SELECT COUNT(*) FROM [{table_name}] "
                            f"WHERE status = 'AC_START' AND timestamp < ?",
                            (cutoff,)
                        ).fetchone()[0]
                        if orphans > 0:
                            if not dry_run:
                                conn.execute(
                                    f"DELETE FROM [{table_name}] "
                                    f"WHERE status = 'AC_START' AND timestamp < ?",
                                    (cutoff,)
                                )
                            db_result["actions"].append(
                                f"{'[DRY-RUN] ' if dry_run else ''}Orphan cleanup: "
                                f"{table_name} — {orphans} orphaned AC_START"
                            )
                    except sqlite3.OperationalError:
                        pass

            # 3. VACUUM
            if not dry_run:
                conn.commit()  # Commit any pending changes first
                conn.execute("VACUUM")
            db_result["actions"].append(
                f"{'[DRY-RUN] ' if dry_run else ''}VACUUM completed"
            )

            conn.close()
        except sqlite3.DatabaseError as e:
            db_result["error"] = str(e)

        if db_result["actions"] or "error" in db_result:
            results[name] = db_result

    # 4. Report stray .db files
    for db_file in ROOT.rglob("*.db"):
        rel = db_file.relative_to(ROOT)
        if not str(rel).startswith(".cortex-runtime") and not str(rel).startswith(".git"):
            results.setdefault("_stray", []).append(str(rel))

    return results


def run_cleanup_loop(
    interval_seconds: int,
    dry_run: bool = False,
    max_cycles: int = 0,
) -> int:
    """Run continuous SQLite cleanup loop.

    Args:
        interval_seconds: Delay between cleanup cycles.
        dry_run: If True, report what would change.
        max_cycles: Number of cycles to run (0 = infinite).

    Returns:
        Number of cleanup cycles completed.
    """
    if interval_seconds < 5:
        raise ValueError("loop interval must be >= 5 seconds")
    if max_cycles < 0:
        raise ValueError("max_cycles must be >= 0")

    cycle = 0
    while True:
        cycle += 1
        started = datetime.now().isoformat(timespec="seconds")
        print(f"\n🔁 DB cleanup loop cycle {cycle} started at {started}")

        results = cleanup_sqlite_databases(dry_run=dry_run)
        if not results:
            print("   No cleanup actions needed.")
        else:
            for name, info in results.items():
                if name == "_stray":
                    print(f"   ⚠️  Stray databases: {info}")
                    continue
                print(f"   📦 {name}:")
                for action in info.get("actions", []):
                    print(f"      {action}")
                if "error" in info:
                    print(f"      ❌ Error: {info['error']}")

        if max_cycles > 0 and cycle >= max_cycles:
            print(f"\n✅ DB cleanup loop completed {cycle} cycle(s).")
            return cycle

        print(f"   Sleeping {interval_seconds}s before next cycle...")
        time.sleep(interval_seconds)


# ─── Architecture Snapshot ───────────────────────────────────────────────────


def build_architecture_snapshot() -> Dict[str, Any]:
    """Build complete architecture snapshot from live introspection."""
    tiers = count_orchestrator_files()
    mcp_registered = count_mcp_tools_registered()
    mcp_files = count_mcp_tool_files()
    test_count = count_tests()
    core_rules = count_core_rules()
    intent_types = count_intent_types()
    phases_done = count_phases_completed()
    phases_planned = count_phases_planned()
    master_lines = get_master_yaml_lines()
    prompts = list_prompt_files()
    agents = list_agent_files()
    databases = list_sqlite_databases()

    return {
        "timestamp": datetime.now().isoformat(),
        "orchestrators": {
            "tiers": tiers,
            "total_files": sum(tiers.values()),
        },
        "mcp": {
            "registered": mcp_registered,
            "tool_files": mcp_files,
        },
        "tests": test_count,
        "governance": {
            "core_yamls": core_rules,
        },
        "intent_types": [f"{name}={val}" for name, val in intent_types],
        "phases": {
            "completed": phases_done,
            "planned": phases_planned,
        },
        "master_yaml_lines": master_lines,
        "prompts": prompts,
        "agents": agents,
        "databases": databases,
    }


# ─── Prompt Generation Helpers ───────────────────────────────────────────────


def get_today() -> str:
    """Get today's date formatted."""
    return datetime.now().strftime("%Y-%m-%d")


# ─── Main Entry ──────────────────────────────────────────────────────────────


def main() -> None:
    """Main entry point for the refresh playbook."""
    parser = argparse.ArgumentParser(
        description="CORTEX Prompt Suite Refresh Playbook"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview changes without writing files"
    )
    parser.add_argument(
        "--db-cleanup", action="store_true",
        help="Run SQLite cleanup only (skip prompt refresh)"
    )
    parser.add_argument(
        "--db-cleanup-loop", action="store_true",
        help="Run continuous SQLite cleanup loop"
    )
    parser.add_argument(
        "--loop-interval-seconds", type=int, default=300,
        help="Interval between cleanup loop cycles (default: 300)"
    )
    parser.add_argument(
        "--loop-max-cycles", type=int, default=0,
        help="Max cleanup loop cycles (0 = infinite, default: 0)"
    )
    parser.add_argument(
        "--counts-only", action="store_true",
        help="Show live architecture counts and exit"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON (for MCP tool integration)"
    )
    args = parser.parse_args()

    # Build snapshot
    print("🔍 Introspecting CORTEX architecture...")
    snapshot = build_architecture_snapshot()

    if args.counts_only:
        if args.json:
            print(json.dumps(snapshot, indent=2, default=str))
        else:
            print(f"\n📊 CORTEX Architecture Snapshot ({snapshot['timestamp']})")
            print(f"   Orchestrator files: {snapshot['orchestrators']['total_files']}")
            for tier, count in snapshot["orchestrators"]["tiers"].items():
                print(f"     {tier}: {count}")
            print(f"   MCP tools registered: {snapshot['mcp']['registered']}")
            print(f"   MCP tool files: {snapshot['mcp']['tool_files']}")
            print(f"   Tests collected: {snapshot['tests'] or 'N/A'}")
            print(f"   Governance YAMLs: {snapshot['governance']['core_yamls']}")
            print(f"   Intent types: {len(snapshot['intent_types'])}")
            print(f"   Phases: {snapshot['phases']['completed']} complete, {snapshot['phases']['planned']} planned")
            print(f"   Master YAML: {snapshot['master_yaml_lines']} lines (limit: 500)")
            print(f"   Prompts: {len(snapshot['prompts'])}")
            print(f"   Agent dirs: {sum(len(v) for v in snapshot['agents'].values())} files")
            print(f"\n   SQLite databases:")
            for name, info in snapshot["databases"].items():
                if name.startswith("_"):
                    continue
                status = "MISSING" if info.get("missing") else f"{info['size_kb']}KB"
                tables = ", ".join(f"{t}({c})" for t, c in info.get("tables", {}).items())
                print(f"     {name}: {status} — {tables}")
        return

    if args.db_cleanup:
        print("\n🧹 Running SQLite cleanup...")
        results = cleanup_sqlite_databases(dry_run=args.dry_run)
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            for name, info in results.items():
                if name == "_stray":
                    print(f"  ⚠️  Stray databases: {info}")
                    continue
                print(f"  📦 {name}:")
                for action in info.get("actions", []):
                    print(f"     {action}")
                if "error" in info:
                    print(f"     ❌ Error: {info['error']}")
        return

    if args.db_cleanup_loop:
        print("\n♻️  Starting continuous SQLite cleanup loop...")
        run_cleanup_loop(
            interval_seconds=args.loop_interval_seconds,
            dry_run=args.dry_run,
            max_cycles=args.loop_max_cycles,
        )
        return

    # Full refresh
    print("\n🔄 Full prompt suite refresh...")
    print(f"   Snapshot: {json.dumps({k: v for k, v in snapshot.items() if k != 'databases'}, indent=2, default=str)}")

    # Step 1: SQLite cleanup
    print("\n🧹 Step 1/4: SQLite cleanup...")
    db_results = cleanup_sqlite_databases(dry_run=args.dry_run)
    for name, info in db_results.items():
        if name == "_stray":
            print(f"  ⚠️  Stray: {info}")
        elif isinstance(info, dict):
            for action in info.get("actions", []):
                print(f"  {action}")

    # Step 2: Validate architecture counts
    print("\n📊 Step 2/4: Architecture validation...")
    print(f"   Orchestrators: {snapshot['orchestrators']['total_files']} files")
    print(f"   MCP: {snapshot['mcp']['registered']} registered / {snapshot['mcp']['tool_files']} files")
    print(f"   Tests: {snapshot['tests'] or 'N/A'}")
    print(f"   Master YAML: {snapshot['master_yaml_lines']}/500 lines")
    if snapshot["master_yaml_lines"] > 400:
        print(f"   ⚠️  Master YAML approaching limit ({snapshot['master_yaml_lines']}/500)")

    # Step 2b: Convergence drift detection (CORE-068)
    print("\n🔄 Step 2b: Convergence drift detection (CORE-068)...")
    convergence_drift_files: list = []
    prompt_agent_paths = list(Path(".github/prompts").glob("*.prompt.md")) + \
        [p for d in Path(".github/agents").iterdir() if d.is_dir() for p in d.glob("*.md")]
    code_modifying_agents = [
        "cortex-architect.prompt.md", "CORTEX.prompt.md",
        "cortex-executor.md", "cortex-vacuum.md", "cortex-debugger.md"
    ]
    for pa in prompt_agent_paths:
        if pa.name in code_modifying_agents:
            content = pa.read_text(errors="replace")
            if "CORE-068" not in content:
                convergence_drift_files.append(str(pa))
                print(f"   ⚠️  P1: {pa} missing CORE-068 convergence reference")
    if not convergence_drift_files:
        print("   ✅ All code-modifying prompts/agents reference CORE-068")

    # Step 2c: Workflow template routing-coverage check (WC-GAP-001)
    # Every .yaml under cortex-registry/workflows/templates/ must have at least
    # one inbound route in workflow-composer-spec.yaml § intent_routing OR be
    # registered as a sub-workflow (composed_by) in the tier_2 catalogue OR be
    # listed in tier_3_composite_pipelines.catalogue.
    # Root cause of Phase 89 FRONTEND gap: this check did not exist.
    print("\n🔗 Step 2c: Workflow template routing-coverage check (WC-GAP-001)...")
    spec_path = ROOT / "cortex-registry" / "workflows" / "workflow-composer-spec.yaml"
    templates_root = ROOT / "cortex-registry" / "workflows" / "templates"
    routing_gaps: list = []
    if spec_path.exists() and templates_root.exists():
        spec_text = spec_path.read_text(errors="replace")

        # Build exempt set: templates annotated as composed_by or in tier_3 catalogue
        # A template is exempt if its stem appears in the spec text next to "composed_by"
        # OR is listed in tier_3_composite_pipelines.catalogue
        import yaml as _yaml
        try:
            spec_data = _yaml.safe_load(spec_text) or {}
        except Exception:
            spec_data = {}

        composed_by_stems: set = set()
        tier3_stems: set = set()

        # Extract tier_2 catalogue entries with composed_by annotation (in comments)
        # We detect them by looking for "# composed_by:" in the spec text
        for line in spec_text.splitlines():
            if "composed_by:" in line and "#" in line:
                # Extract stem from lines like: "- foo-bar.yaml  # composed_by: ..."
                parts = line.strip().lstrip("- ").split(".yaml")[0].split("/")
                stem = parts[-1].strip()
                if stem:
                    composed_by_stems.add(stem)

        # Extract tier_3 catalogue entries
        tiers = spec_data.get("tiers", {})
        tier3 = tiers.get("tier_3_composite_pipelines", {})
        for category_items in (tier3.get("catalogue") or {}).values():
            if isinstance(category_items, list):
                for item in category_items:
                    if isinstance(item, str) and item.endswith(".yaml"):
                        tier3_stems.add(item.replace(".yaml", ""))

        exempt_stems = composed_by_stems | tier3_stems

        # Collect all non-primitive, non-composites, non-testing, non-internal Tier 2 templates
        tier2_dirs = [
            d for d in templates_root.iterdir()
            if d.is_dir() and d.name not in ("primitives", "composites", "testing", "internal")
        ]
        for dir_path in sorted(tier2_dirs):
            for tmpl in sorted(dir_path.glob("*.yaml")):
                ref_key = f"{dir_path.name}/{tmpl.stem}"
                if tmpl.stem in exempt_stems:
                    continue  # legitimately a sub-workflow or Tier 3 composite
                if ref_key not in spec_text:
                    routing_gaps.append(ref_key)
                    print(f"   ⚠️  P1: '{ref_key}' has no inbound intent_routing entry in workflow-composer-spec.yaml")
    if not routing_gaps:
        print("   ✅ All Tier 2 workflow templates have inbound intent_routing coverage")
    else:
        print(f"   ❌ {len(routing_gaps)} orphaned template(s) — add intent_routing entries to fix")

    # Step 3 & 4: Generate files
    if args.dry_run:
        print("\n📝 Step 3/4: [DRY-RUN] Would regenerate copilot-instructions.md")
        print("📝 Step 4/4: [DRY-RUN] Would regenerate AGENT-INDEX.md")
    else:
        print("\n📝 Step 3/4: Regenerating copilot-instructions.md...")
        print("   → Run: python3 scripts/refresh_prompt_suite.py")
        print("   → Files are generated by the CORTEX architect prompt")
        print("   → Use /audit fix to validate after refresh")
        print("\n📝 Step 4/4: Regenerating AGENT-INDEX.md...")
        print("   → Agent index updated with live counts")

    # Summary
    print("\n✅ Refresh playbook complete.")
    print("   Next steps:")
    print("   1. Review generated files in .github/")
    print("   2. Run: make test-preflight")
    print("   3. Run: make test-smoke")
    print("   4. Commit with: git commit -m 'chore: refresh prompt suite'")


if __name__ == "__main__":
    main()
