# AC_START: AC-P125-E-001
"""
Test Suite: Phase 125-e — RegistryIndexer (full pipeline) + build script.
Module: End-to-end YAML→Model→JSON pipeline.
Tests: 22 tests — indexer loading, parsing, resolving, emitting.
"""

import json
import os
import tempfile

import pytest
import yaml

from cortex.intelligence.registry.indexer import RegistryIndexer


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def sample_registry(tmp_path: object) -> str:
    """Create a minimal registry tree with 3 YAML files."""
    gov_dir = os.path.join(str(tmp_path), "governance")
    wf_dir = os.path.join(str(tmp_path), "workflows", "templates")
    os.makedirs(gov_dir)
    os.makedirs(wf_dir)

    # governance-rule YAML
    gov = {
        "schema_type": "governance-rule",
        "id": "test-gov-001",
        "title": "Test Governance Rule",
        "domain": "testing",
        "category": "quality",
        "severity": "P1",
        "rules": [{"id": "CORE-008", "description": "TDD mandatory"}],
    }
    with open(os.path.join(gov_dir, "test-gov.yaml"), "w") as f:
        yaml.dump(gov, f)

    # workflow-template YAML
    wf = {
        "schema_type": "workflow-template",
        "id": "test-wf-001",
        "title": "Test Workflow",
        "version": "1.0",
        "category": "sdlc",
        "steps": [
            {"name": "step1", "action": "build"},
            {"name": "step2", "action": "test"},
        ],
    }
    with open(os.path.join(wf_dir, "test-wf.yaml"), "w") as f:
        yaml.dump(wf, f)

    # unknown-type YAML (should fall back to generic)
    unknown = {
        "schema_type": "custom-thing",
        "id": "custom-001",
        "title": "Custom YAML",
        "foo": "bar",
    }
    with open(os.path.join(str(tmp_path), "custom.yaml"), "w") as f:
        yaml.dump(unknown, f)

    return str(tmp_path)


@pytest.fixture
def indexer(sample_registry: str) -> RegistryIndexer:
    return RegistryIndexer(root_dir=sample_registry)


# ═══════════════════════════════════════════════════════════════════════════════
# RegistryIndexer Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegistryIndexerDiscovery:
    """discover() must find all YAML files recursively."""

    def test_discover_returns_list(self, indexer: RegistryIndexer) -> None:
        files = indexer.discover()
        assert isinstance(files, list)

    def test_discover_finds_yamls(self, indexer: RegistryIndexer) -> None:
        files = indexer.discover()
        assert len(files) == 3

    def test_discover_returns_absolute_paths(self, indexer: RegistryIndexer) -> None:
        files = indexer.discover()
        for f in files:
            assert os.path.isabs(f)


class TestRegistryIndexerParsing:
    """parse_all() must produce typed models for known schema_types."""

    def test_parse_all_returns_models(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        models = indexer.parse_all()
        assert len(models) == 3

    def test_governance_model_is_typed(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        models = indexer.parse_all()
        gov = [m for m in models if m.type == "governance-rule"]
        assert len(gov) == 1
        assert gov[0].id == "test-gov-001"

    def test_workflow_model_is_typed(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        models = indexer.parse_all()
        wf = [m for m in models if m.type == "workflow-template"]
        assert len(wf) == 1

    def test_unknown_type_falls_back_to_generic(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        models = indexer.parse_all()
        # GenericModel.from_data() sets type="generic" for unrecognized schema_types
        generic = [m for m in models if m.type == "generic"]
        assert len(generic) == 1
        assert hasattr(generic[0], "schema_warning")
        assert generic[0].schema_warning is True


class TestRegistryIndexerResolve:
    """resolve() must cross-link references across models."""

    def test_resolve_runs_without_error(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        indexer.parse_all()
        indexer.resolve()  # should not raise

    def test_resolve_populates_integrity(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        models = indexer.parse_all()
        indexer.resolve()
        for m in models:
            assert "all_refs_resolved" in m.integrity


class TestRegistryIndexerEmit:
    """emit() must produce deterministic JSON output."""

    def test_emit_returns_dict(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        indexer.parse_all()
        indexer.resolve()
        output = indexer.emit()
        assert isinstance(output, dict)

    def test_emit_has_artifacts(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        indexer.parse_all()
        indexer.resolve()
        output = indexer.emit()
        assert "artifacts" in output
        assert len(output["artifacts"]) == 3

    def test_emit_has_graph(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        indexer.parse_all()
        indexer.resolve()
        output = indexer.emit()
        assert "graph" in output

    def test_emit_has_integrity(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        indexer.parse_all()
        indexer.resolve()
        output = indexer.emit()
        assert "integrity" in output

    def test_emit_json_is_deterministic(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        indexer.parse_all()
        indexer.resolve()
        j1 = indexer.to_json()
        j2 = indexer.to_json()
        assert j1 == j2

    def test_emit_valid_json(self, indexer: RegistryIndexer) -> None:
        indexer.discover()
        indexer.parse_all()
        indexer.resolve()
        parsed = json.loads(indexer.to_json())
        assert "artifacts" in parsed


class TestRegistryIndexerWriteToFile:
    """write_to() must persist JSON to disk."""

    def test_write_to_creates_file(self, indexer: RegistryIndexer, tmp_path: object) -> None:
        indexer.discover()
        indexer.parse_all()
        indexer.resolve()
        out_path = os.path.join(str(tmp_path), "output", "registry.json")
        indexer.write_to(out_path)
        assert os.path.exists(out_path)

    def test_written_file_is_valid_json(self, indexer: RegistryIndexer, tmp_path: object) -> None:
        indexer.discover()
        indexer.parse_all()
        indexer.resolve()
        out_path = os.path.join(str(tmp_path), "output", "registry.json")
        indexer.write_to(out_path)
        with open(out_path) as f:
            data = json.load(f)
        assert "artifacts" in data


class TestRegistryIndexerFullPipeline:
    """run() must execute discover→parse→resolve→emit in one call."""

    def test_run_returns_output(self, indexer: RegistryIndexer) -> None:
        output = indexer.run()
        assert isinstance(output, dict)
        assert "artifacts" in output
        assert "graph" in output
        assert "integrity" in output

    def test_run_with_output_path(self, indexer: RegistryIndexer, tmp_path: object) -> None:
        out_path = os.path.join(str(tmp_path), "out", "all.json")
        output = indexer.run(output_path=out_path)
        assert os.path.exists(out_path)


# AC_COMPLETE: AC-P125-E-001 ✅
