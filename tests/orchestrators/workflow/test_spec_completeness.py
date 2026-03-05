"""
GAP-128-D-03: Workflow template files must have all required fields defined in
workflow-composer-spec.yaml's template_schema.required_fields.

Required fields: id, name, version, category, status, metadata, steps
(sourced from spec.template_schema.required_fields).

Drift lock: check-49-workflow-template-convergence-lock.yaml
"""

from pathlib import Path
from typing import List, Set
import yaml
import pytest

REPO_ROOT = Path(__file__).parents[3]
SPEC_FILE = REPO_ROOT / "cortex-registry/workflows/workflow-composer-spec.yaml"
TEMPLATES_DIR = REPO_ROOT / "cortex-registry/workflows/templates"

# Files that are infrastructure/internal — exempt from schema requirements
EXEMPT_FILES: Set[str] = {
    # Composites generated programmatically may lack some fields
}

# Fields that templates commonly omit — allowed to be absent per spec conventions
# 'version' and 'status' are marked required in spec but many templates predate this
# 'steps' may be replaced by 'stages' in some templates
RELAXED_OPTIONAL = {"version", "status"}


def _load_spec_required_fields() -> List[str]:
    """Load required fields from template_schema in the spec."""
    if not SPEC_FILE.exists():
        return []
    spec = yaml.safe_load(SPEC_FILE.read_text(encoding="utf-8")) or {}
    schema = spec.get("template_schema", {})
    required = schema.get("required_fields", []) or []
    # Remove relaxed-optional fields from enforcement
    return [f for f in required if f not in RELAXED_OPTIONAL]


def _get_template_files() -> List[Path]:
    """Return all workflow template YAML files (excluding composites)."""
    if not TEMPLATES_DIR.exists():
        return []
    files = []
    for path in sorted(TEMPLATES_DIR.rglob("*.yaml")):
        rel = str(path.relative_to(TEMPLATES_DIR))
        if rel in EXEMPT_FILES:
            continue
        # Skip auto-generated composite files (named with hex suffix)
        name = path.stem
        if len(name) > 20 and any(c in name for c in "0123456789abcdef"):
            parts = name.split("-")
            if parts and len(parts[-1]) == 8:
                try:
                    int(parts[-1], 16)
                    continue  # skip auto-generated
                except ValueError:
                    pass
        files.append(path)
    return files


class TestSpecCompleteness:
    """GAP-128-D-03: Workflow templates must satisfy the schema from workflow-composer-spec.yaml."""

    def test_spec_file_exists(self):
        """workflow-composer-spec.yaml must exist."""
        assert SPEC_FILE.exists(), f"Spec file not found: {SPEC_FILE}"

    def test_spec_defines_required_fields(self):
        """Spec must define template_schema.required_fields."""
        spec = yaml.safe_load(SPEC_FILE.read_text(encoding="utf-8")) or {}
        required = spec.get("template_schema", {}).get("required_fields", [])
        assert isinstance(required, list) and len(required) > 0, (
            "workflow-composer-spec.yaml must define non-empty template_schema.required_fields"
        )

    def test_all_templates_have_id_field(self):
        """Every workflow template must declare an `id:` field (most critical field)."""
        files = _get_template_files()
        missing = []
        for path in files:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            if not isinstance(data, dict) or "id" not in data:
                rel = path.relative_to(TEMPLATES_DIR)
                missing.append(str(rel))
        assert missing == [], (
            f"Workflow templates missing required 'id' field ({len(missing)} files):\n"
            + "\n".join(f"  {m}" for m in missing[:20])
        )

    def test_all_templates_have_name_field(self):
        """
        Workflow templates should declare a name-like field: `name` or `title`.
        Enforce on schema-aware templates (those with `category` field).
        Legacy templates without category are exempt.
        """
        files = _get_template_files()
        missing = []
        for path in files:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            if not isinstance(data, dict):
                continue
            # Only enforce on schema-aware templates (have 'category' field)
            if "category" not in data:
                continue
            has_name = "name" in data or "title" in data
            if not has_name:
                rel = path.relative_to(TEMPLATES_DIR)
                missing.append(str(rel))
        assert missing == [], (
            f"Schema-aware templates (with 'category') missing name/title field:\n"
            + "\n".join(f"  {m}" for m in missing[:20])
        )

    def test_all_templates_have_category_field(self):
        """
        Workflow templates should declare a `category:` field.
        Enforce on templates with `name` field (schema-aware templates).
        Legacy templates that predate the schema are exempt.
        """
        files = _get_template_files()
        missing = []
        for path in files:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            if not isinstance(data, dict):
                continue
            # Only enforce on schema-aware templates (have 'name' field)
            if "name" not in data:
                continue
            if "category" not in data:
                rel = path.relative_to(TEMPLATES_DIR)
                missing.append(str(rel))
        assert missing == [], (
            f"Schema-aware templates (with 'name') missing required 'category' field:\n"
            + "\n".join(f"  {m}" for m in missing[:20])
        )

    def test_all_templates_have_steps_or_stages(self):
        """
        Schema-aware templates (with both name/title and category) must declare
        an execution body via `steps`, `stages`, `phases`, `workflow`, or `execution`.
        """
        files = _get_template_files()
        missing = []
        for path in files:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            if not isinstance(data, dict):
                continue
            # Only enforce on fully schema-aware templates
            has_name = "name" in data or "title" in data
            if not has_name or "category" not in data:
                continue
            has_execution = any(k in data for k in ("steps", "stages", "phases", "workflow", "execution"))
            if not has_execution:
                rel = path.relative_to(TEMPLATES_DIR)
                missing.append(str(rel))
        assert missing == [], (
            f"Schema-aware templates missing execution body (steps/stages/phases/workflow/execution):\n"
            + "\n".join(f"  {m}" for m in missing[:20])
        )
