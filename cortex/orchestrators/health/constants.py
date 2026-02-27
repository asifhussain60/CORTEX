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
    # Git
    ".gitignore",
    ".gitattributes",
    # Editor / CI
    ".editorconfig",
    ".pre-commit-config.yaml",
    # Docker
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".dockerignore",
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

PROTECTED_DIRS: FrozenSet[str] = frozenset({
    ".github",
    "cortex-docs",
    "cortex-registry",
    "_workspaces",
    "scripts",
    "deployment",
    "tests",
    "docs",
})
"""Directories that VacuumOrchestrator must never touch — no renames, deletes,
relocations, or markdown archival inside these trees.

Includes:
- ``.github``        — agents, prompts, copilot instructions, CI
- ``cortex-docs``    — user-facing HTML documentation
- ``cortex-registry``— YAML governance rules and registry
- ``_workspaces``    — intentional workspace area; ALL subfolders are protected:
                         • ``approved-orchestrator-view/`` — approved orchestrator dashboard
                         • ``recommend/``                  — copilot review artefacts (permanent)
                         • ``prompts/``                    — workspace-scoped prompt overrides
                         • ``.chats/``                     — chat session logs
                         • ``cortex-sts/`` — STS demo material (relocated from root)
- ``scripts``        — cross-platform runner scripts
- ``deployment``     — Docker/K8s/Prometheus/Nginx configs
- ``tests``          — test mirror tree
- ``docs``           — generic docs directories
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


__all__ = [
    "EXCLUDED_DIRS",
    "PROTECTED_FILES",
    "PROTECTED_ROOT_EXTENSIONS",
    "ALLOWED_MARKDOWN_PREFIXES",
    "PROTECTED_DIRS",
    "KEBAB_MAX_LEN",
    "PYTHON_EXTENSIONS",
    "NON_PYTHON_EXTENSIONS",
    "RUNTIME_DIR",
    "ARCHIVE_DIR",
    "HANDOFF_FILENAME",
    "ROLLBACK_FILENAME",
    "LEGACY_ROOT_FOLDERS_RELOCATION",
]
