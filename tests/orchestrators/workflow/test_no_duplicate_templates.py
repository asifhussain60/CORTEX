"""
GAP-128-D-02: No duplicate workflow template IDs across all template YAML files.

Each .yaml file in cortex-registry/workflows/templates/ must declare a unique `id`.
Duplicate ids cause routing ambiguity in the WorkflowComposer.

Drift lock: check-49-workflow-template-convergence-lock.yaml
"""

from pathlib import Path
from typing import List, Tuple
import yaml
import pytest

REPO_ROOT = Path(__file__).parents[3]
TEMPLATES_DIR = REPO_ROOT / "cortex-registry/workflows/templates"


def _collect_template_ids() -> List[Tuple[str, str]]:
    """Collect (relative_path, id) from all YAML files in templates/."""
    results: List[Tuple[str, str]] = []
    if not TEMPLATES_DIR.exists():
        return results
    for yaml_file in sorted(TEMPLATES_DIR.rglob("*.yaml")):
        rel = str(yaml_file.relative_to(TEMPLATES_DIR))
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        if isinstance(data, dict) and "id" in data:
            results.append((rel, str(data["id"])))
    return results


class TestNoDuplicateTemplates:
    """GAP-128-D-02: Workflow template IDs must be unique across all template files."""

    def test_templates_dir_exists(self):
        """cortex-registry/workflows/templates/ must exist."""
        assert TEMPLATES_DIR.exists(), f"Templates directory not found: {TEMPLATES_DIR}"

    def test_template_count_is_substantial(self):
        """At least 50 workflow template files should exist (sanity check)."""
        count = len(list(TEMPLATES_DIR.rglob("*.yaml")))
        assert count >= 50, (
            f"Expected ≥50 workflow template files, found {count}"
        )

    def test_no_duplicate_template_ids(self):
        """Every workflow template that declares an `id:` field must be unique."""
        pairs = _collect_template_ids()
        seen: dict = {}
        duplicates: List[str] = []
        for rel_path, template_id in pairs:
            if template_id in seen:
                duplicates.append(
                    f"'{template_id}' in '{rel_path}' (first in '{seen[template_id]}')"
                )
            else:
                seen[template_id] = rel_path
        assert duplicates == [], (
            f"Duplicate workflow template IDs detected:\n"
            + "\n".join(f"  {d}" for d in duplicates)
        )

    def test_all_templates_valid_yaml(self):
        """Every workflow template YAML must parse without errors."""
        invalid: List[str] = []
        for yaml_file in sorted(TEMPLATES_DIR.rglob("*.yaml")):
            rel = str(yaml_file.relative_to(TEMPLATES_DIR))
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                invalid.append(f"{rel}: {e}")
        assert invalid == [], (
            f"YAML parse errors in workflow templates:\n"
            + "\n".join(f"  {i}" for i in invalid)
        )

    def test_no_template_file_name_collisions(self):
        """No two template files may have the same filename (even in different subdirs)."""
        names: dict = {}
        duplicates: List[str] = []
        for yaml_file in sorted(TEMPLATES_DIR.rglob("*.yaml")):
            name = yaml_file.name
            rel = str(yaml_file.relative_to(TEMPLATES_DIR))
            if name in names:
                duplicates.append(
                    f"'{name}' in '{rel}' (first at '{names[name]}')"
                )
            else:
                names[name] = rel
        assert duplicates == [], (
            f"Duplicate workflow template filenames (different dirs — ambiguous):\n"
            + "\n".join(f"  {d}" for d in duplicates)
        )
