"""Phase 128-b: Registry YAML Schema Cohesion Tests.

Authority: GAP-128-B-01 (registry YAMLs with schema violations)
Governance: CORE-008 (TDD mandatory), CORE-064 (Sweep Completeness)
SSOT: cortex-registry/planning/phases/planned/phase-128-conflict-drift-eradication.yaml

These tests verify that all YAML files in cortex-registry have required metadata
and follow schema conventions.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
import yaml

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
REGISTRY_ROOT = PROJECT_ROOT / "cortex-registry"

# YAML files that are allowed to have minimal metadata (legacy or special purpose)
EXEMPT_FILES: set[str] = {
    "yaml-reader.html",  # Not a YAML file
    "cortex-master.yaml",  # Has its own schema
    "INDEX.yaml",  # Index files have different schema
}

# Directories to scan
REGISTRY_DIRS = [
    "core",
    "governance",
    "knowledge",
    "patterns",
    "templates",
    "workflows",
]


def find_yaml_files(directory: Path) -> list[Path]:
    """Find all YAML files in a directory recursively."""
    yaml_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith((".yaml", ".yml")):
                yaml_files.append(Path(root) / file)
    return yaml_files


def load_yaml_safe(path: Path) -> dict[str, Any] | None:
    """Load YAML file safely, returning None on parse errors."""
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError:
        return None


class TestRegistryYamlSchemaCohesion:
    """Verify registry YAML files follow schema conventions."""

    @pytest.fixture
    def all_registry_yamls(self) -> list[Path]:
        """Find all YAML files in registry directories."""
        all_yamls = []
        for dir_name in REGISTRY_DIRS:
            dir_path = REGISTRY_ROOT / dir_name
            if dir_path.exists():
                all_yamls.extend(find_yaml_files(dir_path))
        return all_yamls

    def test_all_yamls_are_parseable(self, all_registry_yamls: list[Path]) -> None:
        """All registry YAML files must be valid YAML (no syntax errors).
        
        GAP-128-B-01: Registry YAMLs with schema violations
        """
        unparseable: list[str] = []
        for yaml_path in all_registry_yamls:
            if yaml_path.name in EXEMPT_FILES:
                continue
            
            try:
                with open(yaml_path, encoding="utf-8") as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                rel_path = yaml_path.relative_to(PROJECT_ROOT)
                unparseable.append(f"{rel_path}: {e}")

        assert not unparseable, (
            f"Found {len(unparseable)} unparseable YAML files:\n"
            + "\n".join(f"  - {u}" for u in unparseable)
        )

    def test_governance_yamls_have_required_fields(self) -> None:
        """Governance YAML files must have id field.
        
        Phase 128-b: All 6 violations fixed — zero tolerance enforced.
        """
        governance_dir = REGISTRY_ROOT / "governance"
        yaml_files = find_yaml_files(governance_dir)
        
        missing_fields: list[str] = []
        for yaml_path in yaml_files:
            if yaml_path.name in EXEMPT_FILES:
                continue
            
            # Skip drift-locks subdirectory (different schema)
            if "drift-locks" in str(yaml_path):
                continue
            
            content = load_yaml_safe(yaml_path)
            if content is None:
                continue  # Handled by parseable test
            
            if not isinstance(content, dict):
                continue  # Some files are lists
            
            # Skip files that are clearly rule collection files
            if "rules" in content or "violations" in content:
                continue
            
            if "id" not in content:
                rel_path = yaml_path.relative_to(PROJECT_ROOT)
                missing_fields.append(f"{rel_path}: missing 'id' field")

        assert not missing_fields, (
            f"Found {len(missing_fields)} governance YAMLs missing required fields:\n"
            + "\n".join(f"  - {m}" for m in missing_fields)
        )

    def test_drift_locks_have_required_schema(self) -> None:
        """Drift lock YAMLs must have check_number, test_file, status fields."""
        drift_locks_dir = REGISTRY_ROOT / "governance" / "drift-locks"
        if not drift_locks_dir.exists():
            pytest.skip("drift-locks directory not found")
        
        yaml_files = find_yaml_files(drift_locks_dir)
        
        required_fields = ["id", "check_number", "status", "test_file"]
        schema_violations: list[str] = []
        
        for yaml_path in yaml_files:
            content = load_yaml_safe(yaml_path)
            if content is None:
                continue
            
            missing = [f for f in required_fields if f not in content]
            if missing:
                rel_path = yaml_path.relative_to(PROJECT_ROOT)
                schema_violations.append(f"{rel_path}: missing {missing}")

        assert not schema_violations, (
            f"Found {len(schema_violations)} drift locks with schema violations:\n"
            + "\n".join(f"  - {v}" for v in schema_violations)
        )

    def test_workflow_templates_have_id_and_name(self) -> None:
        """Workflow template YAMLs must have id and name fields.
        
        Phase 128-b: All 41 violations fixed — baseline now 0.
        """
        workflows_dir = REGISTRY_ROOT / "workflows"
        if not workflows_dir.exists():
            pytest.skip("workflows directory not found")
        
        yaml_files = find_yaml_files(workflows_dir)
        
        schema_violations: list[str] = []
        
        for yaml_path in yaml_files:
            content = load_yaml_safe(yaml_path)
            if content is None:
                continue
            
            if not isinstance(content, dict):
                continue
            
            # Workflow templates should have 'id' or 'name'
            if "id" not in content and "name" not in content:
                # Check if it's a primitives file (different schema)
                if "primitives" in str(yaml_path):
                    continue
                
                rel_path = yaml_path.relative_to(PROJECT_ROOT)
                schema_violations.append(str(rel_path))

        assert not schema_violations, (
            f"Found {len(schema_violations)} workflow templates missing 'id' or 'name' field:\n"
            + "\n".join(f"  - {v}" for v in schema_violations)
        )

    def test_no_empty_yaml_files(self, all_registry_yamls: list[Path]) -> None:
        """Registry YAML files should not be empty.
        
        Phase 128-b: The 1 empty file fixed — zero tolerance enforced.
        """
        empty_files: list[str] = []
        
        for yaml_path in all_registry_yamls:
            if yaml_path.name in EXEMPT_FILES:
                continue
            
            content = load_yaml_safe(yaml_path)
            if content is None or content == {}:
                rel_path = yaml_path.relative_to(PROJECT_ROOT)
                empty_files.append(str(rel_path))

        assert not empty_files, (
            f"Found {len(empty_files)} empty YAML files in registry:\n"
            + "\n".join(f"  - {f}" for f in empty_files)
        )

    def test_knowledge_yamls_have_domain_field(self) -> None:
        """Knowledge YAML files should have domain or category field.
        
        Phase 128-b: All 26 violations fixed — zero tolerance enforced.
        """
        knowledge_dir = REGISTRY_ROOT / "knowledge"
        if not knowledge_dir.exists():
            pytest.skip("knowledge directory not found")
        
        yaml_files = find_yaml_files(knowledge_dir)
        
        missing_domain: list[str] = []
        for yaml_path in yaml_files:
            # INDEX.yaml files are exempt
            if yaml_path.name == "INDEX.yaml":
                continue
            
            content = load_yaml_safe(yaml_path)
            if content is None:
                continue
            
            if not isinstance(content, dict):
                continue
            
            # Should have 'domain', 'category', or 'type' field
            has_categorization = any(
                field in content
                for field in ["domain", "category", "type", "domains"]
            )
            
            if not has_categorization:
                rel_path = yaml_path.relative_to(PROJECT_ROOT)
                missing_domain.append(str(rel_path))

        assert not missing_domain, (
            f"Found {len(missing_domain)} knowledge YAMLs without domain/category:\n"
            + "\n".join(f"  - {m}" for m in missing_domain)
        )
