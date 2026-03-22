"""Shared Constants — Health-Vacuum Pipeline

Single source of truth for all constants used by HealthOrchestrator,
VacuumOrchestrator, and the unified pipeline.

Phase: PHASE-51
CORE: CORE-011 (type hints), CORE-012 (docstrings), CORE-028 (naming)
"""

from typing import Dict, FrozenSet

# ─────────────────────────────────────────────────────────────────────────────
# Filesystem traversal
# ─────────────────────────────────────────────────────────────────────────────

EXCLUDED_DIRS: FrozenSet[str] = frozenset({
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    ".eggs",
    "*.egg-info",
    ".cortex-runtime",
    "_archives",
    "_quarantine",
    "_legacy_broken",
    "_archived",
})
"""Directories that FileContext.build() will never descend into."""

# ─────────────────────────────────────────────────────────────────────────────
# Root-file governance
# ─────────────────────────────────────────────────────────────────────────────

PROTECTED_FILES: FrozenSet[str] = frozenset({
    # Build / packaging
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    "Makefile",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    # Test configuration
    "pytest.ini",
    "conftest.py",
    "tox.ini",
    ".coveragerc",
    # Documentation
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "LICENSE.md",
    "CONTRIBUTING.md",
    "CLAUDE.md",
    # Git
    ".gitignore",
    ".gitattributes",
    # Editor / CI
    ".editorconfig",
    ".pre-commit-config.yaml",
})
"""Files that MUST stay in the project root — never relocated by Vacuum."""

PROTECTED_ROOT_EXTENSIONS: FrozenSet[str] = frozenset({
    ".toml",
    ".cfg",
    ".ini",
    ".lock",
    ".txt",  # requirements.txt
})
"""File extensions commonly allowed in the project root."""

# ─────────────────────────────────────────────────────────────────────────────
# Markdown governance
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_MARKDOWN_PREFIXES: FrozenSet[str] = frozenset({
    "README",
    "CHANGELOG",
    "CONTRIBUTING",
    "LICENSE",
    "SECURITY",
    "CODE_OF_CONDUCT",
})
"""Markdown files whose stem (uppercase) starts with these are allowed in root."""

ROOT_CLEANUP_RECENCY_EXEMPT_SUFFIXES: FrozenSet[str] = frozenset({
    ".prompt.md",
})
"""Root-level filename suffixes exempt from recency guard during root cleanup.

These files are considered root clutter by policy and should be relocated even
when recently created (for example, ad-hoc review prompts created at repo root).
"""

PROTECTED_DIRS: FrozenSet[str] = frozenset({
    # Core source directories — NEVER modified by Vacuum
    "cortex",
    "tests",
    "scripts",
    # Configuration and governance
    ".github",
    ".claude",
    ".vscode",
    "cortex-registry",
    # Documentation and deployment
    "docs",
    "cortex-docs",
    "deployment",
    # Workspace and workspace-adjacent
    "_workspaces",
    # Version-control internals
    ".git",
    # Virtual environments
    ".venv",
    "venv",
    "env",
    # Runtime data (logs, traces, DBs)
    ".cortex-runtime",
    # Node.js dependencies
    "node_modules",
})
"""Directories that VacuumOrchestrator must never touch — no renames, deletes,
relocations, or markdown archival inside these trees.

Expanded from 9 → 15 entries (Phase 141 — SWEEP-141-VACUUM-SOURCE-PROTECTION).

Includes:
- ``cortex``         — Python source package
- ``tests``          — test mirror tree
- ``scripts``        — cross-platform runner scripts
- ``deployment``     — Prometheus/Grafana/health-check configs
- ``.github``        — agents, prompts, copilot instructions, CI
- ``.vscode``        — VS Code workspace settings
- ``docs``           — user-facing HTML documentation
- ``cortex-docs``    — protected documentation workspace and tests
- ``cortex-registry``— YAML governance rules and registry
- ``_workspaces``    — intentional workspace area; ALL subfolders are protected:
                         • ``approved-orchestrator-view/`` — approved orchestrator dashboard
                         • ``recommend/``                  — copilot review artefacts (permanent)
                         • ``prompts/``                    — workspace-scoped prompt overrides
                         • ``.chats/``                     — chat session logs
                         • ``cortex-sts/`` — STS demo material (relocated from root)
- ``.git``           — version control internals
- ``.venv`` / ``venv`` / ``env`` — virtual environment directories
- ``.cortex-runtime``— runtime data (logs, traces, SQLite DBs)
- ``node_modules``   — Node.js dependencies
"""

# ─────────────────────────────────────────────────────────────────────────────
# VACUUM_PROTECTED_ROOTS — root-level tree guard  (Phase 151, GV-028, GV-033)
# ─────────────────────────────────────────────────────────────────────────────

VACUUM_PROTECTED_ROOTS: FrozenSet[str] = frozenset({
    # Core Python source
    "cortex",
    # YAML governance / registry
    "cortex-registry",
    # All tests
    "tests",
    # CI / agents / prompts
    ".github",
    ".claude",
    # Cross-platform scripts
    "scripts",
    # User-facing HTML documentation
    "docs",
    # Protected documentation workspace
    "cortex-docs",
})
"""Canonical root-level protection guard (GV-028, GV-033) — Phase 151.

VACUUM_PROTECTED_ROOTS is the **highest-priority** guard: if the top-level
directory of a path appears in this frozenset, NO destructive vacuum operation
may proceed — regardless of any other config.

Complements PROTECTED_DIRS (the path-level guard added in Phase 141).  Both
guards are active simultaneously:

  VACUUM_PROTECTED_ROOTS  →  root/tree-level (Phase 151, GV-028/033)
  PROTECTED_DIRS          →  path-level       (Phase 141, GV-012..GV-019)

GV-033 contract: VACUUM_PROTECTED_ROOTS is the *canonical* root guard.
PROTECTED_DIRS remains the *subordinate* path guard.

This frozenset is **immutable at runtime** — never add/remove entries via
code; always update this constant and commit (GV-028).
"""

# ─────────────────────────────────────────────────────────────────────────────
# Naming conventions  (CORE-028)
# ─────────────────────────────────────────────────────────────────────────────

KEBAB_MAX_LEN: int = 80
"""Maximum length for a kebab-case filename (excluding extension)."""

PYTHON_EXTENSIONS: FrozenSet[str] = frozenset({".py", ".pyi"})
"""File extensions that must follow snake_case naming."""

NON_PYTHON_EXTENSIONS: FrozenSet[str] = frozenset({
    ".yaml", ".yml", ".json", ".md", ".txt", ".html", ".css", ".js",
    ".ts", ".sh", ".bat", ".xml", ".toml", ".cfg", ".ini", ".env",
})
"""Common file extensions that should follow kebab-case naming."""

# ─────────────────────────────────────────────────────────────────────────────
# Handoff / runtime
# ─────────────────────────────────────────────────────────────────────────────

RUNTIME_DIR: str = ".cortex-runtime"
"""Root directory for all runtime artifacts."""

ARCHIVE_DIR: str = ".cortex-runtime/archived-docs"
"""Destination for stale markdown files archived by Vacuum."""

HANDOFF_FILENAME: str = "health-issues.yaml"
"""Filename for the Health → Vacuum handoff contract."""

ROLLBACK_FILENAME: str = "rollback-manifest.json"
"""Filename for the Vacuum rollback manifest."""

# ─────────────────────────────────────────────────────────────────────────────
# Dissolved packages — NEVER recreate directories for these
# ─────────────────────────────────────────────────────────────────────────────

DISSOLVED_PACKAGES: FrozenSet[str] = frozenset({
    "cortex_brain",
    "cortex_intelligence",
    "cortex_lens",
})
"""Package names that were dissolved/relocated into ``cortex/``.

These names MUST NOT appear as new directories anywhere in the workspace.
Audit Check #10 (test-source mirror) and Check #27 (stale test dir) must
skip directory creation for any path containing a dissolved package name.
Vacuum orchestrator treats recreation of these directories as a P0 violation.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Legacy folder relocation rules
# ─────────────────────────────────────────────────────────────────────────────

LEGACY_ROOT_FOLDERS_RELOCATION: Dict[str, str] = {
    # source_folder: destination_folder
    # Runtime state artifacts → .cortex-runtime/
    "cortex_brain": ".cortex-runtime/state/cortex_brain",
    # Demo/sample material → _workspaces/
    "cortex-sts": "_workspaces/cortex-sts",
}
"""Root-level legacy folders that should be relocated to proper locations.

- ``cortex_brain/`` — Legacy runtime state (governance.db) → ``.cortex-runtime/state/``
- ``cortex-sts/`` — STS demo material → ``_workspaces/`` for isolation
"""


VACUUM_RECENCY_GUARD_HOURS: int = 24
"""Files modified within this many hours are never deleted or archived by VacuumOrchestrator.

Any file or directory whose ``st_mtime`` is less than ``VACUUM_RECENCY_GUARD_HOURS`` old is
unconditionally skipped during planning stages (_plan_empty_cleanup, _plan_orphan_cleanup,
_plan_markdown_archive, _plan_root_cleanup).  This prevents accidental removal of work
in progress during active development sessions.

GAP-REF: GAP-130-01 (Phase 130-a — Foundation Backport)
"""

__all__ = [
    "EXCLUDED_DIRS",
    "PROTECTED_FILES",
    "PROTECTED_ROOT_EXTENSIONS",
    "ALLOWED_MARKDOWN_PREFIXES",
    "ROOT_CLEANUP_RECENCY_EXEMPT_SUFFIXES",
    "PROTECTED_DIRS",
    "VACUUM_PROTECTED_ROOTS",
    "KEBAB_MAX_LEN",
    "PYTHON_EXTENSIONS",
    "NON_PYTHON_EXTENSIONS",
    "RUNTIME_DIR",
    "ARCHIVE_DIR",
    "HANDOFF_FILENAME",
    "ROLLBACK_FILENAME",
    "DISSOLVED_PACKAGES",
    "LEGACY_ROOT_FOLDERS_RELOCATION",
    "VACUUM_RECENCY_GUARD_HOURS",
]
