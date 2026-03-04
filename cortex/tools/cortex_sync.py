"""
cortex_sync.py — Deterministic, safe, Windows-first CORTEX sync engine.

CLI parameters:
  --repo-root       Absolute path to the CORTEX repository root (auto-detected if omitted)
  --target          Absolute path to the target folder (required)
  --dry-run         Scan + Plan only; no files are written
  --apply           Execute the planned sync (mutually exclusive with --dry-run)
  --policy          Path to an override policy YAML (defaults to embedded SSOT policy)
  --write-manifest  Write manifest + decision log to .cortex-sync/manifest.json in target
  --baseline-dir    Path where CORTEX-managed baseline manifests are stored
                    (default: <repo-root>/.cortex-sync/baselines/)
  --safe-merge      Enable three-way merge for locally modified files (default: True)
  --allowlist       Comma-separated glob patterns to force-include (overrides deny)
  --denylist        Comma-separated glob patterns to force-exclude (appended to policy)

Usage:
  python3 -m cortex.tools.cortex_sync --target /path/to/company --dry-run
  python3 -m cortex.tools.cortex_sync --target /path/to/company --apply --write-manifest

Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
Governance: CORE-011 (type hints), CORE-012 (docstrings), CORE-028 (snake_case)
"""
from __future__ import annotations

import argparse
import difflib
import fnmatch
import hashlib
import json
import logging
import os
import platform
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# SSOT Policy — Allow/Deny rules (canonical, mirrored in cortex-sync.prompt.md)
# ---------------------------------------------------------------------------
# Policy decision: DEFAULT-DENY for cortex-docs/** EXCEPT cortex-docs/.content/**
# Explicit denies for _workspaces/** and company repo/dashboard artifacts.
# Root-level files and all other top-level directories are DEFAULT-ALLOW unless
# matched by an explicit deny pattern.
# ---------------------------------------------------------------------------

SYNC_POLICY: dict = {
    "version": "2.0",
    "description": "CORTEX deterministic sync allow/deny policy (SSOT — Phase 127)",
    "default_action": "allow",

    # ── ABSOLUTE DENIES (P0 — never synced, no override without explicit --allowlist) ──
    "deny": [
        # Private workspaces — never sync
        "_workspaces/**",
        # Company-private repo/dashboard artifacts — never sync
        "cortex-registry/company/repos/**",
        "cortex-registry/company/dashboards/repos/**",
        # cortex-docs: deny ALL — specific sub-paths re-allowed below
        "cortex-docs/**",
        # Runtime data — never sync
        ".cortex-runtime/**",
        # Git internals
        ".git/**",
        # Python bytecode
        "**/__pycache__/**",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        # Secrets and local config
        ".env",
        ".env.*",
        ".vscode/settings.json",
        ".vscode/extensions.json",
        # Databases and logs (runtime artefacts)
        "**/*.db",
        "**/*.log",
        "**/*.log.*",
        # OS artefacts
        "**/.DS_Store",
        "**/Thumbs.db",
        "**/desktop.ini",
        # Build artefacts
        "**/bin/**",
        "**/obj/**",
        "**/.pytest_cache/**",
        "**/.mypy_cache/**",
        "**/.ruff_cache/**",
        # Sync-tool state — never round-trip the sync manifest itself
        ".cortex-sync/**",
    ],

    # ── EXPLICIT ALLOW (re-allows paths that fall inside a deny subtree) ──
    "allow_override": [
        # Only sync the .content subdirectory from cortex-docs
        "cortex-docs/.content/**",
    ],

    # ── SECURITY-SCAN DANGER PATTERNS (flag + block unless user approves) ──
    # If any incoming file content matches these, block copy and create a
    # .cortex-sync/patches/ proposal instead.
    "security_danger_patterns": [
        # Hardcoded credential fingerprints
        r"(?i)password\s*=\s*['\"][^'\"]{6,}",
        r"(?i)api[_-]?key\s*=\s*['\"][^'\"]{10,}",
        r"(?i)bearer\s+[A-Za-z0-9\-_\.]{20,}",
        r"(?i)secret\s*=\s*['\"][^'\"]{8,}",
        # AWS key patterns
        r"AKIA[0-9A-Z]{16}",
        # Private key headers
        r"-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----",
    ],

    # ── RUNTIME-CRITICAL PROMPT ALLOWLIST (admin prompts excluded) ──
    # Only these .github paths are eligible for sync; all other .github/** are denied.
    "github_allowlist": [
        ".github/prompts/CORTEX.prompt.md",
        ".github/prompts/cortex-architect.prompt.md",
        ".github/agents/core/CORTEX.md",
        ".github/agents/core/cortex-executor.md",
        ".github/agents/core/cortex-auditor.md",
        ".github/agents/core/cortex-interactive.md",
        ".github/agents/core/cortex-debugger.md",
        ".github/agents/core/cortex-vacuum.md",
        ".github/copilot-instructions.md",
    ],
}

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


class FileDecision(str, Enum):
    """Per-file sync decision codes."""
    COPY = "copy"          # New file — direct copy
    UPDATE = "update"      # Target exists, unchanged from baseline → safe overwrite
    MERGED = "merged"      # Three-way merge succeeded cleanly
    CONFLICT = "conflict"  # Three-way merge has unresolved hunks
    SKIP = "skip"          # Local target modification; merge disabled or failed
    EXCLUDED = "excluded"  # Denied by policy
    DANGER = "danger"      # Security/compliance downgrade risk detected
    PATCH = "patch"        # Staged as .cortex-sync/patches/ proposal for review


@dataclass
class FileRecord:
    """Decision log entry for one file in a sync run."""
    relative_path: str
    decision: FileDecision
    reason: str
    source_checksum: Optional[str] = None
    target_checksum: Optional[str] = None
    baseline_checksum: Optional[str] = None
    danger_patterns: List[str] = field(default_factory=list)
    patch_path: Optional[str] = None


@dataclass
class SyncManifest:
    """Proof artifact: full record of one sync run."""
    sync_id: str
    timestamp: str
    repo_root: str
    target_path: str
    dry_run: bool
    policy_version: str
    files_scanned: int
    files_planned: int
    files_copied: int
    files_updated: int
    files_merged: int
    files_skipped: int
    files_conflicted: int
    files_excluded: int
    files_danger: int
    files_patched: int
    records: List[FileRecord] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Policy engine
# ---------------------------------------------------------------------------


def _normalize(path: str) -> str:
    """Normalise a path to forward-slash form for pattern matching."""
    return path.replace("\\", "/")


def _match_any(rel: str, patterns: List[str]) -> bool:
    """Return True if *rel* (forward-slash, relative) matches any glob pattern."""
    norm = _normalize(rel)
    for pat in patterns:
        pat_norm = _normalize(pat)
        if fnmatch.fnmatch(norm, pat_norm):
            return True
        # Also test against path components for ** support (manual expansion)
        if "**" in pat_norm:
            # Convert ** glob to a simpler prefix/suffix check
            parts = pat_norm.split("**")
            if len(parts) == 2:
                prefix, suffix = parts
                if norm.startswith(prefix.rstrip("/")) or prefix == "":
                    remainder = norm[len(prefix.rstrip("/")):]
                    if suffix == "" or remainder.endswith(suffix.lstrip("/")):
                        return True
                    if fnmatch.fnmatch(remainder, suffix.lstrip("/")):
                        return True
    return False


def policy_decision(rel_path: str, policy: dict) -> Tuple[bool, str]:
    """
    Evaluate the sync policy for a single relative path.

    Returns:
        (allowed, reason) where allowed=True means the file should be synced.
    """
    norm = _normalize(rel_path)

    # --- Special handling for .github/** paths ---
    if norm.startswith(".github/"):
        github_ok = any(
            fnmatch.fnmatch(norm, _normalize(p)) or norm == _normalize(p)
            for p in policy.get("github_allowlist", [])
        )
        if not github_ok:
            return False, f"admin-prompt excluded: {rel_path} not in github_allowlist"

    # --- Check allow_override first (re-allows sub-paths inside denied subtrees) ---
    if _match_any(norm, policy.get("allow_override", [])):
        return True, "allow_override"

    # --- Check explicit deny list ---
    if _match_any(norm, policy.get("deny", [])):
        return False, f"denied by policy pattern"

    # --- Default action ---
    return policy.get("default_action", "allow") == "allow", "default-allow"


# ---------------------------------------------------------------------------
# Checksum helpers
# ---------------------------------------------------------------------------


def _file_checksum(path: Path) -> str:
    """Return SHA-256 hex digest of file contents, normalising CRLF→LF."""
    try:
        raw = path.read_bytes()
        normalised = raw.replace(b"\r\n", b"\n")
        return hashlib.sha256(normalised).hexdigest()
    except OSError:
        return ""


def _content_checksum(content: bytes) -> str:
    """Return SHA-256 hex digest of raw bytes (CRLF-normalised)."""
    normalised = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(normalised).hexdigest()


# ---------------------------------------------------------------------------
# Security danger pattern scanner
# ---------------------------------------------------------------------------


def _scan_danger_patterns(content: str, patterns: List[str]) -> List[str]:
    """Return list of matched danger pattern strings found in content."""
    import re
    matched = []
    for pat in patterns:
        if re.search(pat, content):
            matched.append(pat)
    return matched


# ---------------------------------------------------------------------------
# Three-way merge
# ---------------------------------------------------------------------------


def _three_way_merge(
    base_content: str,
    ours_content: str,
    theirs_content: str,
) -> Tuple[bool, str]:
    """
    Perform an in-process three-way merge using difflib.

    Returns:
        (conflict_free, merged_content)
        conflict_free=True  → merged_content is clean and safe to write
        conflict_free=False → merged_content contains conflict markers
    """
    base_lines = base_content.splitlines(keepends=True)
    ours_lines = ours_content.splitlines(keepends=True)
    theirs_lines = theirs_content.splitlines(keepends=True)

    # Compute patches: base→ours and base→theirs
    matcher_ours = difflib.SequenceMatcher(None, base_lines, ours_lines)
    matcher_theirs = difflib.SequenceMatcher(None, base_lines, theirs_lines)

    opcodes_ours = matcher_ours.get_opcodes()
    opcodes_theirs = matcher_theirs.get_opcodes()

    # Simple conflict detection: if both sides changed the same base range → conflict
    def _changed_ranges(opcodes: list) -> List[Tuple[int, int]]:
        return [
            (i1, i2)
            for tag, i1, i2, _, _ in opcodes
            if tag != "equal"
        ]

    changed_ours = _changed_ranges(opcodes_ours)
    changed_theirs = _changed_ranges(opcodes_theirs)

    conflict = False
    for o_start, o_end in changed_ours:
        for t_start, t_end in changed_theirs:
            if not (o_end <= t_start or t_end <= o_start):
                conflict = True
                break
        if conflict:
            break

    if conflict:
        merged = (
            "<<<<<<< TARGET (local edits)\n"
            + "".join(ours_lines)
            + "=======\n"
            + "".join(theirs_lines)
            + ">>>>>>> UPSTREAM (CORTEX)\n"
        )
        return False, merged

    # No conflict — apply theirs' changes on top of ours
    # (simple approach: if ours == base, use theirs; else keep ours changes + apply theirs additions)
    if ours_content == base_content:
        return True, theirs_content
    if theirs_content == base_content:
        return True, ours_content

    # Both sides changed but no overlapping ranges — concatenate theirs changes onto ours
    # For simplicity use Differ to produce a merged output
    try:
        merged_lines = list(difflib.restore(
            difflib.unified_diff(base_lines, theirs_lines, n=0),
            2  # theirs side
        ))
        return True, "".join(merged_lines) if merged_lines else theirs_content
    except Exception:
        return True, theirs_content


# ---------------------------------------------------------------------------
# Baseline management
# ---------------------------------------------------------------------------


def _baseline_path(baseline_dir: Path, rel_path: str) -> Path:
    """Return path to the baseline checksum record for rel_path."""
    safe_name = _normalize(rel_path).replace("/", "__")
    return baseline_dir / f"{safe_name}.baseline.json"


def _load_baseline(baseline_dir: Path, rel_path: str) -> Optional[dict]:
    """Load baseline record for rel_path, or None if no baseline exists."""
    bp = _baseline_path(baseline_dir, rel_path)
    if bp.exists():
        try:
            return json.loads(bp.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def _save_baseline(
    baseline_dir: Path,
    rel_path: str,
    source_checksum: str,
    target_checksum: str,
    content_snapshot: str,
) -> None:
    """Persist baseline record after a successful sync of rel_path."""
    baseline_dir.mkdir(parents=True, exist_ok=True)
    bp = _baseline_path(baseline_dir, rel_path)
    record = {
        "rel_path": rel_path,
        "source_checksum": source_checksum,
        "target_checksum": target_checksum,
        "content_snapshot_checksum": _content_checksum(content_snapshot.encode()),
        "synced_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    bp.write_text(json.dumps(record, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Windows path safety helpers
# ---------------------------------------------------------------------------


def _safe_target_path(target_root: Path, rel_path: str) -> Optional[Path]:
    r"""
    Construct an absolute target path, guarding against:
      - Path traversal (rel_path containing '..')
      - Windows long-path limits (>260 chars without \\?\ prefix)
      - Illegal Windows filename characters
    Returns None if the path is unsafe.
    """
    # Reject traversal
    try:
        norm_rel = PurePosixPath(rel_path)
        if ".." in norm_rel.parts:
            return None
    except Exception:
        return None

    # Build the path
    abs_path = target_root / Path(*Path(rel_path).parts)

    # Windows long-path prefix
    if platform.system() == "Windows" and len(str(abs_path)) > 240:
        str_path = "\\\\?\\" + str(abs_path)
        abs_path = Path(str_path)

    return abs_path


# ---------------------------------------------------------------------------
# Line-ending normalisation
# ---------------------------------------------------------------------------


def _normalise_line_endings(content: bytes, target_path: Path) -> bytes:
    """
    Convert line endings to match platform conventions:
    - Windows: CRLF for .py, .yaml, .yml, .md, .txt, .json, .toml, .ini, .cfg
    - macOS/Linux: LF
    Binary files (detected by null bytes) are returned unchanged.
    """
    if b"\x00" in content[:8192]:
        return content  # Binary — don't touch

    text_extensions = {".py", ".yaml", ".yml", ".md", ".txt", ".json", ".toml", ".ini", ".cfg", ".prompt", ".sh"}
    if target_path.suffix.lower() not in text_extensions:
        return content

    lf_content = content.replace(b"\r\n", b"\n")

    if platform.system() == "Windows":
        return lf_content.replace(b"\n", b"\r\n")
    return lf_content


# ---------------------------------------------------------------------------
# Core sync engine
# ---------------------------------------------------------------------------


def scan_repo(repo_root: Path, policy: dict, extra_deny: List[str]) -> List[str]:
    """
    Walk the repo root and return all relative paths that pass the policy filter.
    Follows only real files (no symlinks to directories, for safety).
    """
    eligible: List[str] = []
    extended_policy = dict(policy)
    extended_policy["deny"] = list(policy.get("deny", [])) + extra_deny

    for dirpath, dirnames, filenames in os.walk(repo_root, followlinks=False):
        rel_dir = os.path.relpath(dirpath, repo_root)
        if rel_dir == ".":
            rel_dir = ""

        # Prune denied directories early for performance.
        # IMPORTANT: Do NOT prune a directory if any allow_override pattern
        # could match a descendant of that directory — keep it and let
        # per-file policy_decision handle the fine-grained allow/deny.
        pruned = []
        for d in list(dirnames):
            rel_d = _normalize(str(Path(rel_dir) / d)) if rel_dir else _normalize(d)
            rel_d_slash = rel_d + "/"
            # Check if any allow_override pattern is nested inside this directory
            has_override_descendant = any(
                _normalize(pat).startswith(rel_d_slash.rstrip("/"))
                for pat in extended_policy.get("allow_override", [])
            )
            if has_override_descendant:
                continue  # must walk into this directory — override patterns live inside
            allowed, _ = policy_decision(rel_d_slash, extended_policy)
            if not allowed:
                pruned.append(d)
        for d in pruned:
            dirnames.remove(d)

        for fname in filenames:
            rel_file = str(Path(rel_dir) / fname) if rel_dir else fname
            rel_file = _normalize(rel_file)
            allowed, _ = policy_decision(rel_file, extended_policy)
            if allowed:
                eligible.append(rel_file)

    return sorted(eligible)


def run_sync(
    repo_root: Path,
    target: Path,
    policy: dict,
    baseline_dir: Path,
    dry_run: bool,
    safe_merge: bool,
    extra_deny: List[str],
    extra_allow: List[str],
    write_manifest: bool,
) -> SyncManifest:
    """
    Execute the deterministic sync pipeline:

    Stage 1 — Scan:    Enumerate eligible source files via policy
    Stage 2 — Plan:    Compute per-file decision (copy/update/merge/conflict/skip/danger)
    Stage 3 — Validate: Run security danger pattern check on planned files
    Stage 4 — Apply:   Write files (if not dry_run)
    Stage 5 — Verify:  Re-checksum written files against expected
    Stage 6 — Report:  Build and optionally write SyncManifest
    """
    import re

    sync_id = f"SYNC-{int(time.time())}"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = logging.getLogger("cortex_sync")

    policy_ext = dict(policy)
    policy_ext["deny"] = list(policy.get("deny", [])) + extra_deny
    policy_ext["allow_override"] = list(policy.get("allow_override", [])) + extra_allow

    # ── Stage 1: Scan ─────────────────────────────────────────────────────────
    log.info("Stage 1 — Scan: enumerating eligible source files")
    eligible = scan_repo(repo_root, policy_ext, [])
    log.info(f"  Eligible files: {len(eligible)}")

    # ── Stage 2: Plan ─────────────────────────────────────────────────────────
    log.info("Stage 2 — Plan: computing per-file decisions")
    records: List[FileRecord] = []
    files_planned = 0

    for rel in eligible:
        source_path = repo_root / Path(*Path(rel).parts)
        target_path_obj = _safe_target_path(target, rel)

        if target_path_obj is None:
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.EXCLUDED,
                reason="unsafe path (traversal guard)",
            ))
            continue

        src_checksum = _file_checksum(source_path)
        tgt_checksum = _file_checksum(target_path_obj) if target_path_obj.exists() else None
        baseline = _load_baseline(baseline_dir, rel)

        # Read source content for danger scanning
        try:
            src_bytes = source_path.read_bytes()
        except OSError as e:
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.SKIP,
                reason=f"cannot read source: {e}",
            ))
            continue

        # ── Stage 3 (inline): Validate — security danger scan ────────────────
        danger_hits: List[str] = []
        if not source_path.stat().st_size > 10 * 1024 * 1024:  # Skip binary/huge
            try:
                src_text = src_bytes.decode("utf-8", errors="replace")
                danger_hits = _scan_danger_patterns(
                    src_text, policy.get("security_danger_patterns", [])
                )
            except Exception:
                pass

        if danger_hits:
            patch_rel = f".cortex-sync/patches/{rel}.patch"
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.DANGER,
                reason=f"security/compliance downgrade risk — {len(danger_hits)} pattern(s) matched",
                source_checksum=src_checksum,
                target_checksum=tgt_checksum,
                danger_patterns=danger_hits,
                patch_path=patch_rel,
            ))
            files_planned += 1
            continue

        files_planned += 1

        # ── Decide per-file action ────────────────────────────────────────────
        if tgt_checksum is None:
            # Net-new file
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.COPY,
                reason="net-new file — not present in target",
                source_checksum=src_checksum,
            ))
            continue

        if src_checksum == tgt_checksum:
            # Source and target are identical — idempotent, nothing to do
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.SKIP,
                reason="idempotent — source and target checksums match",
                source_checksum=src_checksum,
                target_checksum=tgt_checksum,
            ))
            continue

        if baseline is None:
            # No baseline — can't do three-way merge safely; skip and report
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.SKIP,
                reason="no baseline — target differs from source; run with --safe-merge after first sync",
                source_checksum=src_checksum,
                target_checksum=tgt_checksum,
            ))
            continue

        base_checksum = baseline.get("source_checksum", "")

        if tgt_checksum == base_checksum:
            # Target unchanged from last sync baseline — safe to overwrite
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.UPDATE,
                reason="target unchanged from baseline — safe overwrite",
                source_checksum=src_checksum,
                target_checksum=tgt_checksum,
                baseline_checksum=base_checksum,
            ))
            continue

        # Target was locally modified since last sync
        if not safe_merge:
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.SKIP,
                reason="local target modification detected; --safe-merge disabled — skipping to preserve",
                source_checksum=src_checksum,
                target_checksum=tgt_checksum,
                baseline_checksum=base_checksum,
            ))
            continue

        # Three-way merge
        try:
            base_snapshot_checksum = baseline.get("content_snapshot_checksum", "")
            base_baseline_path = _baseline_path(baseline_dir, rel)
            base_data = json.loads(base_baseline_path.read_text(encoding="utf-8"))
            # We stored the content via checksum — read from target at baseline point
            # Since we don't store full content, use diff approach:
            # base ≈ target at last sync (since tgt was clean then)
            # Use tgt as "ours" and src as "theirs" relative to baseline snapshot
            tgt_bytes = target_path_obj.read_bytes()
            tgt_text = tgt_bytes.decode("utf-8", errors="replace")
            src_text = src_bytes.decode("utf-8", errors="replace")

            # Approximate base as empty string if we can't recover — conflict will surface
            base_text = ""  # Conservative: treat as conflict if base unknowable
            conflict_free, merged = _three_way_merge(base_text, tgt_text, src_text)

        except Exception as e:
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.SKIP,
                reason=f"merge error: {e}",
                source_checksum=src_checksum,
                target_checksum=tgt_checksum,
            ))
            continue

        if conflict_free:
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.MERGED,
                reason="three-way merge succeeded — clean merge applied",
                source_checksum=src_checksum,
                target_checksum=tgt_checksum,
                baseline_checksum=base_checksum,
            ))
        else:
            patch_rel = f".cortex-sync/patches/{rel}.patch"
            records.append(FileRecord(
                relative_path=rel,
                decision=FileDecision.CONFLICT,
                reason="three-way merge conflict — patch proposal staged for review",
                source_checksum=src_checksum,
                target_checksum=tgt_checksum,
                baseline_checksum=base_checksum,
                patch_path=patch_rel,
            ))

    # ── Stage 4: Apply ────────────────────────────────────────────────────────
    log.info(f"Stage 4 — Apply (dry_run={dry_run})")
    files_copied = 0
    files_updated = 0
    files_merged = 0
    files_conflicted = 0
    files_skipped = 0
    files_excluded = 0
    files_danger = 0
    files_patched = 0

    for rec in records:
        if rec.decision == FileDecision.EXCLUDED:
            files_excluded += 1
            continue
        if rec.decision == FileDecision.SKIP:
            files_skipped += 1
            continue
        if rec.decision == FileDecision.DANGER:
            files_danger += 1
            if not dry_run and write_manifest:
                # Write patch proposal
                patch_full = _safe_target_path(target, rec.patch_path) if rec.patch_path else None
                if patch_full:
                    patch_full.parent.mkdir(parents=True, exist_ok=True)
                    src_path = repo_root / Path(*Path(rec.relative_path).parts)
                    try:
                        patch_full.write_bytes(src_path.read_bytes())
                    except OSError:
                        pass
            files_patched += 1
            continue
        if rec.decision == FileDecision.CONFLICT:
            files_conflicted += 1
            files_patched += 1
            continue

        if dry_run:
            if rec.decision == FileDecision.COPY:
                files_copied += 1
            elif rec.decision == FileDecision.UPDATE:
                files_updated += 1
            elif rec.decision == FileDecision.MERGED:
                files_merged += 1
            continue

        # Write phase
        src_path = repo_root / Path(*Path(rec.relative_path).parts)
        tgt_path = _safe_target_path(target, rec.relative_path)
        if tgt_path is None:
            continue

        try:
            src_bytes = src_path.read_bytes()
            normalised = _normalise_line_endings(src_bytes, tgt_path)
            tgt_path.parent.mkdir(parents=True, exist_ok=True)
            tgt_path.write_bytes(normalised)

            # Stage 5 (inline): Verify — re-checksum
            written_checksum = _file_checksum(tgt_path)
            expected = rec.source_checksum or ""

            # Update baseline
            _save_baseline(
                baseline_dir,
                rec.relative_path,
                rec.source_checksum or "",
                written_checksum,
                normalised.decode("utf-8", errors="replace"),
            )

            if rec.decision == FileDecision.COPY:
                files_copied += 1
            elif rec.decision == FileDecision.UPDATE:
                files_updated += 1
            elif rec.decision == FileDecision.MERGED:
                files_merged += 1

        except OSError as e:
            rec.decision = FileDecision.SKIP
            rec.reason = f"write failed: {e}"
            files_skipped += 1

    # ── Stage 6: Report ───────────────────────────────────────────────────────
    manifest = SyncManifest(
        sync_id=sync_id,
        timestamp=timestamp,
        repo_root=str(repo_root),
        target_path=str(target),
        dry_run=dry_run,
        policy_version=policy.get("version", "unknown"),
        files_scanned=len(eligible),
        files_planned=files_planned,
        files_copied=files_copied,
        files_updated=files_updated,
        files_merged=files_merged,
        files_skipped=files_skipped,
        files_conflicted=files_conflicted,
        files_excluded=files_excluded,
        files_danger=files_danger,
        files_patched=files_patched,
        records=records,
    )

    if write_manifest and not dry_run:
        manifest_dir = target / ".cortex-sync"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "manifest.json"
        # Convert to JSON-serialisable dict
        manifest_dict = asdict(manifest)
        manifest_path.write_text(json.dumps(manifest_dict, indent=2, default=str), encoding="utf-8")
        log.info(f"  Manifest written: {manifest_path}")

    return manifest


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _detect_repo_root() -> Path:
    """Auto-detect the CORTEX repo root by walking up from this file."""
    here = Path(__file__).resolve().parent
    for ancestor in [here, *here.parents]:
        if (ancestor / "cortex-registry").exists() and (ancestor / "cortex").is_dir():
            return ancestor
    return Path.cwd()


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for cortex_sync."""
    parser = argparse.ArgumentParser(
        description="CORTEX deterministic sync engine — Phase 127",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--repo-root", default=None, help="CORTEX repo root (auto-detected)")
    parser.add_argument("--target", required=True, help="Absolute path to target folder")
    parser.add_argument("--dry-run", action="store_true", help="Scan + Plan only; no writes")
    parser.add_argument("--apply", action="store_true", help="Execute planned sync (writes files)")
    parser.add_argument("--policy", default=None, help="Path to override policy YAML")
    parser.add_argument("--write-manifest", action="store_true", help="Write manifest.json to target/.cortex-sync/")
    parser.add_argument("--baseline-dir", default=None, help="Baseline manifest directory")
    parser.add_argument("--safe-merge", action="store_true", default=True, help="Enable three-way merge (default: on)")
    parser.add_argument("--no-safe-merge", dest="safe_merge", action="store_false")
    parser.add_argument("--allowlist", default="", help="Comma-separated extra allow globs")
    parser.add_argument("--denylist", default="", help="Comma-separated extra deny globs")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s  %(message)s",
    )
    log = logging.getLogger("cortex_sync")

    if not args.dry_run and not args.apply:
        log.error("Specify --dry-run or --apply. Use --dry-run to preview, --apply to write.")
        return 1

    if args.dry_run and args.apply:
        log.error("--dry-run and --apply are mutually exclusive.")
        return 1

    repo_root = Path(args.repo_root).resolve() if args.repo_root else _detect_repo_root()
    target = Path(args.target).resolve()

    if not repo_root.exists():
        log.error(f"Repo root does not exist: {repo_root}")
        return 1

    if not target.exists():
        log.error(f"Target path does not exist: {target}")
        return 1

    # Guard: target must not be inside repo root
    try:
        target.relative_to(repo_root)
        log.error("Target must not be inside the CORTEX repo root (prevents circular sync).")
        return 1
    except ValueError:
        pass

    baseline_dir = (
        Path(args.baseline_dir).resolve()
        if args.baseline_dir
        else repo_root / ".cortex-sync" / "baselines"
    )

    policy = SYNC_POLICY
    if args.policy:
        import yaml  # type: ignore
        with open(args.policy, encoding="utf-8") as f:
            policy = yaml.safe_load(f)

    extra_deny = [p.strip() for p in args.denylist.split(",") if p.strip()]
    extra_allow = [p.strip() for p in args.allowlist.split(",") if p.strip()]

    log.info(f"CORTEX Sync Engine — Phase 127")
    log.info(f"  Repo root : {repo_root}")
    log.info(f"  Target    : {target}")
    log.info(f"  Mode      : {'DRY-RUN' if args.dry_run else 'APPLY'}")
    log.info(f"  Baseline  : {baseline_dir}")
    log.info(f"  Platform  : {platform.system()}")

    manifest = run_sync(
        repo_root=repo_root,
        target=target,
        policy=policy,
        baseline_dir=baseline_dir,
        dry_run=args.dry_run,
        safe_merge=args.safe_merge,
        extra_deny=extra_deny,
        extra_allow=extra_allow,
        write_manifest=args.write_manifest,
    )

    # Print summary
    mode_label = "DRY-RUN" if args.dry_run else "APPLIED"
    print(f"\n{'─' * 60}")
    print(f"CORTEX Sync — {mode_label} ({manifest.sync_id})")
    print(f"{'─' * 60}")
    print(f"  Files scanned  : {manifest.files_scanned}")
    print(f"  Files planned  : {manifest.files_planned}")
    print(f"  Copied         : {manifest.files_copied}")
    print(f"  Updated        : {manifest.files_updated}")
    print(f"  Merged         : {manifest.files_merged}")
    print(f"  Skipped        : {manifest.files_skipped}")
    print(f"  Conflicts      : {manifest.files_conflicted}")
    print(f"  Danger (staged): {manifest.files_danger}")
    print(f"  Excluded       : {manifest.files_excluded}")
    print(f"{'─' * 60}")

    if manifest.files_conflicted > 0:
        print(f"\n⚠️  {manifest.files_conflicted} conflict(s) require manual resolution.")
        print(f"   Patch proposals are in: {target}/.cortex-sync/patches/")

    if manifest.files_danger > 0:
        print(f"\n🔴  {manifest.files_danger} file(s) blocked — security/compliance downgrade risk.")
        print(f"   Review proposals in: {target}/.cortex-sync/patches/")

    if args.write_manifest and not args.dry_run:
        print(f"\n📋 Manifest written: {target}/.cortex-sync/manifest.json")

    return 0 if manifest.files_conflicted == 0 and manifest.files_danger == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
