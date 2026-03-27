#!/usr/bin/env python3
"""
Update execution_progress fields for a specific phase in v3.2-unified-architecture-plan.yaml.
The dashboard polls this file every 5 seconds, so progress bars update automatically.

Usage examples:
  python3 scripts/update_phase_progress.py --phase P2 --completed 7
  python3 scripts/update_phase_progress.py --phase P2 --completed 7 --total 15
  python3 scripts/update_phase_progress.py --phase P3 --completed 5 --note "Step 5 of 9 done"
  python3 scripts/update_phase_progress.py --show
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

YAML_PATH = (
    Path(__file__).parent.parent
    / "_workspaces/cortex-v3/v3.2-unified-architecture-plan.yaml"
)
HTML_PATH = (
    Path(__file__).parent.parent
    / "_workspaces/cortex-v3/v32-plan/execution.html"
)


def _build_progress_json(yaml_text: str) -> str:
    """Parse all phases from YAML and return a compact JSON array for the HTML embed."""
    import json as _json

    lines = yaml_text.split("\n")
    phases: list = []
    cur: Optional[dict] = None
    in_exec = False

    for line in lines:
        pm = re.match(r"^\s*-\s+phase:\s+(P\d+)\s*$", line)
        if pm:
            if cur:
                phases.append(cur)
            cur = {
                "id": pm.group(1), "title": pm.group(1), "status": "PLANNED",
                "totalSteps": 0, "completedSteps": 0, "percent": 0,
                "note": "No note", "updated": "--",
            }
            in_exec = False
            continue
        if not cur:
            continue
        if re.match(r"^\s{4}execution_progress:\s*$", line):
            in_exec = True
            continue
        if re.match(r"^\s{4}[a-z_]+:\s", line) and not re.match(r"^\s{4}execution_progress:\s*$", line):
            in_exec = False
        tm = re.match(r'^\s{4}title:\s+"([^"]+)"\s*$', line)
        if tm:
            cur["title"] = tm.group(1)
        sm = re.match(r"^\s{4}status:\s+([A-Z_]+)\s*$", line)
        if sm:
            cur["status"] = sm.group(1)
        if in_exec:
            m = re.match(r"^\s{6}total_steps:\s+(\d+)\s*$", line)
            if m:
                cur["totalSteps"] = int(m.group(1))
            m = re.match(r"^\s{6}completed_steps:\s+(\d+)\s*$", line)
            if m:
                cur["completedSteps"] = int(m.group(1))
            m = re.match(r"^\s{6}percent:\s+(\d+)\s*$", line)
            if m:
                cur["percent"] = int(m.group(1))
            m = re.match(r'^\s{6}status_note:\s+"([^"]*)"\s*$', line)
            if m:
                cur["note"] = m.group(1)
            m = re.match(r'^\s{6}last_updated:\s+"([^"]+)"\s*$', line)
            if m:
                cur["updated"] = m.group(1)
    if cur:
        phases.append(cur)
    return _json.dumps(phases, ensure_ascii=False, separators=(",", ":"))


def _update_html_snapshot() -> None:
    """Replace the embedded progress data block in execution.html."""
    if not HTML_PATH.exists():
        return
    progress_json = _build_progress_json(YAML_PATH.read_text(encoding="utf-8"))
    html = HTML_PATH.read_text(encoding="utf-8")
    new_block = (
        f'  <!-- PROGRESS-DATA-START -->'
        f'<script>window.__CORTEX_PROGRESS__={progress_json};</script>'
        f'<!-- PROGRESS-DATA-END -->'
    )
    patched = re.sub(
        r"  <!-- PROGRESS-DATA-START -->.*?<!-- PROGRESS-DATA-END -->",
        new_block,
        html,
        flags=re.DOTALL,
    )
    if patched != html:
        HTML_PATH.write_text(patched, encoding="utf-8")
        print("    HTML snapshot updated — dashboard will reflect changes on next reload.")


def _get_phase_slice(text: str, phase_id: str) -> tuple[int, int]:
    """Return (start, end) byte offsets for one phase block within text."""
    phase_marker = re.search(
        rf"^\s+-\s+phase:\s+{re.escape(phase_id)}\s*$", text, re.MULTILINE
    )
    if not phase_marker:
        print(f"ERROR: phase '{phase_id}' not found in YAML.")
        sys.exit(1)

    # Next phase starts the boundary (or end-of-file)
    next_phase = re.search(
        r"^\s+-\s+phase:\s+P\d+\s*$", text[phase_marker.end():], re.MULTILINE
    )
    end = (
        phase_marker.end() + next_phase.start()
        if next_phase
        else len(text)
    )
    return phase_marker.start(), end


def _read_field(chunk: str, field: str) -> Optional[str]:
    m = re.search(rf"^\s{{6}}{field}:\s+(.+)$", chunk, re.MULTILINE)
    return m.group(1).strip().strip('"') if m else None


def show_all(text: str) -> None:
    phases = re.findall(r"^\s+-\s+phase:\s+(P\d+)\s*$", text, re.MULTILINE)
    print(f"\n{'PHASE':<6}  {'DONE':>5}  {'TOTAL':>5}  {'PCT':>4}  {'STATUS NOTE'}")
    print("─" * 72)
    for pid in phases:
        s, e = _get_phase_slice(text, pid)
        chunk = text[s:e]
        done = _read_field(chunk, "completed_steps") or "?"
        total = _read_field(chunk, "total_steps") or "?"
        pct = _read_field(chunk, "percent") or "?"
        note = _read_field(chunk, "status_note") or ""
        print(f"{pid:<6}  {done:>5}  {total:>5}  {pct:>3}%  {note[:52]}")
    print()


def update_phase(
    phase_id: str,
    completed: int,
    total: Optional[int] = None,
    note: Optional[str] = None,
    timestamp: Optional[str] = None,
) -> None:
    text = YAML_PATH.read_text(encoding="utf-8")

    start, end = _get_phase_slice(text, phase_id)
    chunk = text[start:end]

    # Resolve total from existing YAML if not supplied
    if total is None:
        existing = _read_field(chunk, "total_steps")
        total = int(existing) if existing and existing.isdigit() else 0

    percent = round((completed / total) * 100) if total > 0 else 0
    percent = max(0, min(100, percent))

    ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Preserve existing note when caller omits --note
    if note is None:
        note = _read_field(chunk, "status_note") or ""

    # Surgical in-place replacements inside this phase's slice only
    def patch(chunk_text: str, field: str, new_val: str) -> str:
        return re.sub(
            rf"(^\s{{6}}{field}:\s+).+$",
            lambda m: m.group(1) + new_val,
            chunk_text,
            flags=re.MULTILINE,
        )

    new_chunk = chunk
    new_chunk = patch(new_chunk, "total_steps", str(total))
    new_chunk = patch(new_chunk, "completed_steps", str(completed))
    new_chunk = patch(new_chunk, "percent", str(percent))
    new_chunk = patch(new_chunk, "status_note", f'"{note}"')
    new_chunk = patch(new_chunk, "last_updated", f'"{ts}"')

    YAML_PATH.write_text(text[:start] + new_chunk + text[end:], encoding="utf-8")
    _update_html_snapshot()

    bar_len = 36
    filled = round(percent / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"\n✅  {phase_id}  [{bar}]  {percent}%")
    print(f"    Steps: {completed}/{total}  ·  {note}")
    print(f"    Updated: {ts}")
    print(f"    HTTP: dashboard refreshes within 5 seconds. file://: reload the page.\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update CORTEX v3.2 phase execution progress in the YAML plan."
    )
    parser.add_argument(
        "--phase", help="Phase ID to update (e.g. P2, P3)"
    )
    parser.add_argument(
        "--completed", type=int, help="Number of completed steps"
    )
    parser.add_argument(
        "--total",
        type=int,
        default=None,
        help="Total steps override (optional; preserves existing value if omitted)",
    )
    parser.add_argument(
        "--note",
        type=str,
        default=None,
        help='Status note string (optional; preserves existing if omitted)',
    )
    parser.add_argument(
        "--timestamp",
        type=str,
        default=None,
        help="ISO-8601 UTC timestamp override (optional; defaults to now)",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Print current progress for all phases and exit",
    )

    args = parser.parse_args()

    if not YAML_PATH.exists():
        print(f"ERROR: YAML plan not found at:\n  {YAML_PATH}")
        sys.exit(1)

    text = YAML_PATH.read_text(encoding="utf-8")

    if args.show:
        show_all(text)
        sys.exit(0)

    if args.phase is None or args.completed is None:
        parser.error("--phase and --completed are required (or use --show)")

    update_phase(args.phase, args.completed, args.total, args.note, args.timestamp)


if __name__ == "__main__":
    main()
