import os
from pathlib import Path

import pytest

from src.operations.documentation_component_registry import create_default_registry


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = WORKSPACE_ROOT / "cortex-brain" / "admin" / "documentation" / ".test-output"


def setup_module(module):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def test_registry_lists_components():
    registry = create_default_registry(WORKSPACE_ROOT)
    components = registry.list_components()
    ids = {c["id"] for c in components}
    assert {"diagrams", "feature_list", "mkdocs", "executive_summary", "publish"}.issubset(ids)


def test_execute_single_component_diagrams():
    registry = create_default_registry(WORKSPACE_ROOT)
    result = registry.execute(
        component_id="diagrams",
        output_path=OUTPUT_DIR,
        profile="standard",
    )
    assert isinstance(result, dict)
    assert result.get("generator_type") == "diagrams"


def test_execute_pipeline_all():
    registry = create_default_registry(WORKSPACE_ROOT)
    pipeline = ["diagrams", "feature_list", "mkdocs"]
    result = registry.execute_pipeline(
        component_ids=pipeline,
        output_path=OUTPUT_DIR,
        profile="standard",
    )
    assert result.get("success") is True
    assert isinstance(result.get("components"), list)
    assert len(result.get("components")) == len(pipeline)


def test_execute_executive_summary():
    """Test executive summary generator"""
    registry = create_default_registry(WORKSPACE_ROOT)
    result = registry.execute(
        component_id="executive_summary",
        output_path=OUTPUT_DIR,
        profile="standard",
    )
    assert isinstance(result, dict)
    assert result.get("generator_type") == "executive-summary"
    assert result.get("success") is True


def test_execute_publish_dry_run():
    """Test publish generator in dry-run mode (no actual deployment)"""
    registry = create_default_registry(WORKSPACE_ROOT)
    result = registry.execute(
        component_id="publish",
        output_path=OUTPUT_DIR,
        profile="standard",
        metadata={"deploy": False},  # Dry-run mode
    )
    assert isinstance(result, dict)
    assert result.get("generator_type") == "publish"
    # Note: success may be False if mkdocs not installed, that's okay for testing


def test_publish_depends_on_mkdocs():
    """Verify publish component has mkdocs as dependency"""
    registry = create_default_registry(WORKSPACE_ROOT)
    components = {c["id"]: c for c in registry.list_components()}
    
    publish = components.get("publish")
    assert publish is not None
    assert "mkdocs" in publish["dependencies"]

