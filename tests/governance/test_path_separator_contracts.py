"""
GAP-128-A-02: Windows path separators (backslash) in YAML files.

Asserts that all YAML files under cortex-registry/ that contain path-like
values use forward-slash notation only — no raw backslashes that would
break on macOS/Linux CI and cause portability bugs on Windows.

Drift lock: check-42-master-yaml-path-contract-lock.yaml
"""

import re
from pathlib import Path

import pytest

REGISTRY_ROOT = Path(__file__).parent.parent.parent / "cortex-registry"

# Patterns that are ALLOWED to contain backslash (escaped newlines in string
# literals such as \n, or regex patterns stored in YAML).
ALLOWED_BACKSLASH_PATTERNS = re.compile(
    r"\\n|\\t|\\r|\\u[0-9a-fA-F]{4}|\\\\|\\\'|\\\""
)

# File-level allowlist — these files are known to store shell/regex strings.
ALLOWED_FILES = {
    "format-standards.yaml",
    "response-templates.yaml",
}


def _yaml_files():
    return [
        p
        for p in REGISTRY_ROOT.rglob("*.yaml")
        if not any(part.startswith(".") for part in p.parts)
    ]


def _path_like_values(text: str):
    """Yield (line_number, line) for lines that look like Windows file path values.

    Only scans lines where the YAML key is `file:` or `path:` — these are
    the only keys that should contain filesystem paths. Ignores description
    text, regex patterns, and example strings which legitimately contain
    backslash escape sequences.
    """
    for i, line in enumerate(text.splitlines(), 1):
        # Only examine file: or path: keys
        if not re.match(r"^\s*(file|path)\s*:", line):
            continue
        # Drive-letter Windows paths: e.g. file: C:\Users\foo
        if re.search(r"[A-Za-z]:\\", line):
            yield i, line


class TestPathSeparatorContracts:
    """YAML files must not contain raw Windows backslash path separators."""

    def test_no_raw_backslash_paths_in_registry_yaml(self):
        """No YAML file should contain a Windows-style path (C:\\foo\\bar)."""
        violations = []
        for yaml_file in _yaml_files():
            if yaml_file.name in ALLOWED_FILES:
                continue
            text = yaml_file.read_text(encoding="utf-8", errors="replace")
            for lineno, line in _path_like_values(text):
                # Strip allowed escape sequences, then check for bare backslash
                stripped = ALLOWED_BACKSLASH_PATTERNS.sub("", line)
                if "\\" in stripped:
                    violations.append(
                        f"{yaml_file.relative_to(REGISTRY_ROOT)}:{lineno}: {line.strip()}"
                    )

        assert violations == [], (
            f"Found {len(violations)} raw Windows backslash path(s) in YAML files:\n"
            + "\n".join(violations[:20])
        )

    def test_cortex_master_yaml_file_pointers_use_forward_slash(self):
        """All file: pointers in cortex-master.yaml use forward slashes."""
        import yaml

        master = (
            Path(__file__).parent.parent.parent
            / "cortex-registry"
            / "cortex-master.yaml"
        )
        data = yaml.safe_load(master.read_text(encoding="utf-8"))

        def collect_file_values(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    yield from collect_file_values(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for item in obj:
                    yield from collect_file_values(item, path)
            elif isinstance(obj, str) and "\\" in obj:
                yield path, obj

        violations = list(collect_file_values(data))
        assert violations == [], (
            f"cortex-master.yaml contains backslash paths:\n"
            + "\n".join(f"  {p}: {v}" for p, v in violations[:10])
        )

    def test_yaml_files_count_is_stable(self):
        """Regression: registry should have at least 300 YAML files."""
        count = len(_yaml_files())
        assert count >= 300, f"Expected ≥300 YAML files, found {count}"
