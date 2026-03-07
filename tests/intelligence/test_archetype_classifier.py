"""Tests for ArchetypeClassifier — Phase 131-a (GAP-131-01).

TDD RED phase: All tests must FAIL before implementation exists.
Target: cortex/intelligence/archetype_classifier.py

CORE-008: TDD mandatory — write failing tests first.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Module import
# ─────────────────────────────────────────────────────────────────────────────

class TestArchetypeClassifierImport:
    """Verify ArchetypeClassifier can be imported."""

    def test_module_importable(self) -> None:
        """ArchetypeClassifier module must exist and be importable."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier  # noqa: F401

    def test_class_importable(self) -> None:
        """ArchetypeClassifier class must be importable."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        assert ArchetypeClassifier is not None

    def test_get_classifier_singleton(self) -> None:
        """get_archetype_classifier() singleton helper must exist."""
        from cortex.intelligence.archetype_classifier import get_archetype_classifier
        c1 = get_archetype_classifier()
        c2 = get_archetype_classifier()
        assert c1 is c2  # singleton


# ─────────────────────────────────────────────────────────────────────────────
# Instantiation
# ─────────────────────────────────────────────────────────────────────────────

class TestArchetypeClassifierInstantiation:
    """ArchetypeClassifier construction."""

    def test_instantiates_without_args(self) -> None:
        """ArchetypeClassifier() must construct without required arguments."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        clf = ArchetypeClassifier()
        assert clf is not None

    def test_has_classify_method(self) -> None:
        """classify() method must exist."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        clf = ArchetypeClassifier()
        assert callable(getattr(clf, "classify", None))

    def test_has_list_archetypes_method(self) -> None:
        """list_archetypes() must return all known archetype ids."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        clf = ArchetypeClassifier()
        assert callable(getattr(clf, "list_archetypes", None))

    def test_has_get_signals_method(self) -> None:
        """get_signals() must return scoring signals for a given archetype."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        clf = ArchetypeClassifier()
        assert callable(getattr(clf, "get_signals", None))


# ─────────────────────────────────────────────────────────────────────────────
# Archetype definitions YAML
# ─────────────────────────────────────────────────────────────────────────────

class TestArchetypeDefinitionsYaml:
    """Canonical archetype-definitions.yaml must exist and be well-formed."""

    _YAML_PATH = (
        Path(__file__).parent.parent.parent
        / "cortex-registry" / "knowledge" / "archetypes" / "archetype-definitions.yaml"
    )

    def test_yaml_exists(self) -> None:
        """archetype-definitions.yaml must exist."""
        assert self._YAML_PATH.exists(), f"Missing: {self._YAML_PATH}"

    def test_yaml_parseable(self) -> None:
        """archetype-definitions.yaml must be valid YAML."""
        import yaml
        content = yaml.safe_load(self._YAML_PATH.read_text())
        assert isinstance(content, dict)

    def test_yaml_has_archetypes_key(self) -> None:
        """Top-level 'archetypes' key must exist."""
        import yaml
        content = yaml.safe_load(self._YAML_PATH.read_text())
        assert "archetypes" in content

    def test_yaml_has_13_archetypes(self) -> None:
        """Must define exactly 13 canonical archetypes."""
        import yaml
        content = yaml.safe_load(self._YAML_PATH.read_text())
        archetypes = content.get("archetypes", [])
        assert len(archetypes) == 13, (
            f"Expected 13 archetypes, got {len(archetypes)}: "
            f"{[a.get('id') for a in archetypes]}"
        )

    def test_all_archetypes_have_id_and_signals(self) -> None:
        """Every archetype entry must have 'id' and 'signals' fields."""
        import yaml
        content = yaml.safe_load(self._YAML_PATH.read_text())
        for arch in content.get("archetypes", []):
            assert "id" in arch, f"Missing 'id' in {arch}"
            assert "signals" in arch, f"Missing 'signals' in archetype {arch.get('id')}"


# ─────────────────────────────────────────────────────────────────────────────
# Individual archetype YAML files
# ─────────────────────────────────────────────────────────────────────────────

class TestArchetypeKnowledgeYamls:
    """13 individual archetype knowledge YAML files must exist."""

    _ARCHETYPES_DIR = (
        Path(__file__).parent.parent.parent
        / "cortex-registry" / "knowledge" / "archetypes"
    )

    _EXPECTED_FILES = [
        "dotnet-monolith.yaml",
        "microservices-mesh.yaml",
        "spa-frontend.yaml",
        "legacy-batch.yaml",
        "event-driven.yaml",
        "data-platform.yaml",
        "mobile-native.yaml",
        "embedded-systems.yaml",
        "saas-multi-tenant.yaml",
        "serverless.yaml",
        "ml-platform.yaml",
        "cli-tooling.yaml",
        "archetype-definitions.yaml",  # master definitions file
    ]

    def test_archetypes_directory_exists(self) -> None:
        """cortex-registry/knowledge/archetypes/ directory must exist."""
        assert self._ARCHETYPES_DIR.exists(), (
            f"Missing directory: {self._ARCHETYPES_DIR}"
        )

    def test_all_13_archetype_files_exist(self) -> None:
        """All 13 individual archetype YAML files must exist."""
        missing = [
            f for f in self._EXPECTED_FILES
            if not (self._ARCHETYPES_DIR / f).exists()
        ]
        assert not missing, f"Missing archetype YAML files: {missing}"

    def test_individual_yamls_are_parseable(self) -> None:
        """Each individual archetype YAML must be valid YAML."""
        import yaml
        for fname in self._EXPECTED_FILES:
            path = self._ARCHETYPES_DIR / fname
            if path.exists():
                content = yaml.safe_load(path.read_text())
                assert isinstance(content, dict), f"{fname} must be a YAML mapping"


# ─────────────────────────────────────────────────────────────────────────────
# Classification logic
# ─────────────────────────────────────────────────────────────────────────────

class TestClassificationLogic:
    """ArchetypeClassifier.classify() returns expected results."""

    def test_classify_returns_dict(self, tmp_path: Path) -> None:
        """classify() must return a dict with 'archetype' and 'score' keys."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        clf = ArchetypeClassifier()
        result = clf.classify(tmp_path)
        assert isinstance(result, dict)
        assert "archetype" in result
        assert "score" in result

    def test_empty_repo_returns_generic(self, tmp_path: Path) -> None:
        """An empty directory must return GENERIC archetype (graceful degradation)."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        clf = ArchetypeClassifier()
        result = clf.classify(tmp_path)
        assert result["archetype"] in ("GENERIC", "UNKNOWN")

    def test_dotnet_signals_detected(self, tmp_path: Path) -> None:
        """A .sln file must trigger DotNetMonolith archetype scoring."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        (tmp_path / "MyApp.sln").write_text("Microsoft Visual Studio Solution")
        (tmp_path / "MyApp.csproj").write_text("<Project></Project>")
        clf = ArchetypeClassifier()
        result = clf.classify(tmp_path)
        assert result["archetype"] == "DotNetMonolith", (
            f"Expected DotNetMonolith, got {result['archetype']} (score: {result['score']})"
        )

    def test_spa_signals_detected(self, tmp_path: Path) -> None:
        """package.json with Angular/React signals must produce SPAFrontend archetype."""
        import json
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        (tmp_path / "package.json").write_text(json.dumps({
            "name": "my-app",
            "dependencies": {"@angular/core": "^17.0.0"}
        }))
        (tmp_path / "angular.json").write_text("{}")
        clf = ArchetypeClassifier()
        result = clf.classify(tmp_path)
        assert result["archetype"] == "SPAFrontend", (
            f"Expected SPAFrontend, got {result['archetype']} (score: {result['score']})"
        )

    def test_microservices_signals_detected(self, tmp_path: Path) -> None:
        """docker-compose.yaml with multiple services triggers MicroservicesMesh."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        (tmp_path / "docker-compose.yaml").write_text(
            "version: '3'\nservices:\n  api:\n    image: node\n  worker:\n    image: node\n  gateway:\n    image: nginx\n"
        )
        (tmp_path / "k8s").mkdir()
        (tmp_path / "k8s" / "deployment.yaml").write_text("apiVersion: apps/v1")
        clf = ArchetypeClassifier()
        result = clf.classify(tmp_path)
        assert result["archetype"] == "MicroservicesMesh", (
            f"Expected MicroservicesMesh, got {result['archetype']} (score: {result['score']})"
        )

    def test_score_is_numeric(self, tmp_path: Path) -> None:
        """score must be numeric (int or float)."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        clf = ArchetypeClassifier()
        result = clf.classify(tmp_path)
        assert isinstance(result["score"], (int, float))

    def test_nonexistent_path_returns_generic(self) -> None:
        """A non-existent path must return GENERIC gracefully (no exception)."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        clf = ArchetypeClassifier()
        result = clf.classify(Path("/nonexistent/path/xyz"))
        assert result["archetype"] in ("GENERIC", "UNKNOWN")

    def test_list_archetypes_returns_13(self) -> None:
        """list_archetypes() must return exactly 12 content archetype ids (GENERIC excluded)."""
        from cortex.intelligence.archetype_classifier import ArchetypeClassifier
        clf = ArchetypeClassifier()
        archetypes = clf.list_archetypes()
        assert isinstance(archetypes, list)
        assert len(archetypes) == 12, f"Expected 12, got {len(archetypes)}: {archetypes}"


# ─────────────────────────────────────────────────────────────────────────────
# IntelligenceFacade integration
# ─────────────────────────────────────────────────────────────────────────────

class TestFacadeIntegration:
    """IntelligenceFacade must expose classify_archetype()."""

    def test_facade_has_classify_archetype(self) -> None:
        """IntelligenceFacade must have classify_archetype() method."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert callable(getattr(facade, "classify_archetype", None))

    def test_facade_classify_archetype_returns_dict(self, tmp_path: Path) -> None:
        """facade.classify_archetype() must return a dict with archetype key."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.classify_archetype(tmp_path)
        assert isinstance(result, dict)
        assert "archetype" in result
