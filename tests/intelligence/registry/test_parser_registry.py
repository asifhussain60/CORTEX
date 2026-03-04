"""
Golden tests: Parser registration mechanism.
Proves that @register_parser decorator auto-registers parsers,
and that the registry dispatches to the correct parser by schema type.
"""

import pytest

from cortex.intelligence.registry.parsers import (
    PARSER_REGISTRY,
    get_parser_for_type,
    register_parser,
)
from cortex.intelligence.registry.parsers.generic_parser import GenericParser


class TestParserRegistryDecorator:
    """Tests for the @register_parser decorator mechanism."""

    def test_generic_parser_is_registered(self):
        """GenericParser must be in PARSER_REGISTRY under 'generic'."""
        assert "generic" in PARSER_REGISTRY
        assert PARSER_REGISTRY["generic"] is GenericParser

    def test_register_parser_decorator_adds_to_registry(self):
        """A new parser decorated with @register_parser appears in PARSER_REGISTRY."""

        @register_parser("test_custom_type")
        class _TestParser:
            pass

        assert "test_custom_type" in PARSER_REGISTRY
        assert PARSER_REGISTRY["test_custom_type"] is _TestParser
        # cleanup
        del PARSER_REGISTRY["test_custom_type"]

    def test_register_parser_returns_class_unchanged(self):
        """The decorator must return the class without modification."""

        @register_parser("test_passthrough")
        class _Passthrough:
            sentinel = 42

        assert _Passthrough.sentinel == 42
        del PARSER_REGISTRY["test_passthrough"]

    def test_get_parser_for_known_type(self):
        """get_parser_for_type returns the registered parser class."""
        parser_cls = get_parser_for_type("generic")
        assert parser_cls is GenericParser

    def test_get_parser_for_unknown_type_returns_generic(self):
        """Unknown type falls back to GenericParser."""
        parser_cls = get_parser_for_type("nonexistent_type_xyz")
        assert parser_cls is GenericParser

    def test_parser_registry_is_dict(self):
        """PARSER_REGISTRY is a plain dict mapping str → class."""
        assert isinstance(PARSER_REGISTRY, dict)


class TestGenericParserParse:
    """Tests for GenericParser.parse() — the fallback parser."""

    def test_parse_returns_generic_model(self):
        """GenericParser.parse() returns a GenericModel instance."""
        from cortex.intelligence.registry.models.generic import GenericModel

        parser = GenericParser()
        result = parser.parse(
            data={"key": "value"},
            source_file="test.yaml",
        )
        assert isinstance(result, GenericModel)

    def test_parse_preserves_raw_data(self):
        """GenericModel.raw_data must contain the original dict."""
        from cortex.intelligence.registry.models.generic import GenericModel

        parser = GenericParser()
        data = {"rules": [{"id": "R1"}], "extra": True}
        result = parser.parse(data=data, source_file="test.yaml")
        assert result.raw_data == data

    def test_parse_sets_source_file(self):
        """GenericModel.source_file must be set from the argument."""
        parser = GenericParser()
        result = parser.parse(data={}, source_file="path/to/file.yaml")
        assert result.source_file == "path/to/file.yaml"

    def test_parse_sets_schema_warning(self):
        """GenericModel must have schema_warning=True (no dedicated parser matched)."""
        parser = GenericParser()
        result = parser.parse(data={"x": 1}, source_file="f.yaml")
        assert result.schema_warning is True

    def test_parse_with_id_field(self):
        """If data has an 'id' field, GenericModel.id should use it."""
        parser = GenericParser()
        result = parser.parse(data={"id": "MY-001", "name": "test"}, source_file="f.yaml")
        assert result.id == "MY-001"

    def test_parse_without_id_generates_one(self):
        """If data has no 'id', GenericModel.id should be auto-generated from filename."""
        parser = GenericParser()
        result = parser.parse(data={"name": "test"}, source_file="some/path/my-file.yaml")
        assert result.id is not None
        assert len(result.id) > 0


class TestBaseRegistryModel:
    """Tests for BaseRegistryModel — the abstract base for all models."""

    def test_base_model_importable(self):
        """BaseRegistryModel must be importable."""
        from cortex.intelligence.registry.models.base import BaseRegistryModel
        assert BaseRegistryModel is not None

    def test_base_model_has_required_fields(self):
        """BaseRegistryModel must define id, type, source_file, title, source_hash."""
        from cortex.intelligence.registry.models.base import BaseRegistryModel
        import dataclasses

        fields = {f.name for f in dataclasses.fields(BaseRegistryModel)}
        required = {"id", "type", "source_file", "title", "source_hash"}
        assert required.issubset(fields), f"Missing fields: {required - fields}"

    def test_base_model_to_dict(self):
        """BaseRegistryModel.to_dict() must return a dict with sorted keys."""
        from cortex.intelligence.registry.models.base import BaseRegistryModel

        model = BaseRegistryModel(
            id="TEST-001",
            type="test",
            source_file="test.yaml",
            title="Test Model",
            source_hash="sha256:abc123",
        )
        d = model.to_dict()
        assert isinstance(d, dict)
        assert d["id"] == "TEST-001"
        assert d["type"] == "test"
        # Keys must be sorted for deterministic JSON
        keys = list(d.keys())
        assert keys == sorted(keys)

    def test_base_model_to_json_deterministic(self):
        """Same input → identical JSON output (byte-for-byte)."""
        from cortex.intelligence.registry.models.base import BaseRegistryModel

        model = BaseRegistryModel(
            id="DET-001",
            type="test",
            source_file="det.yaml",
            title="Deterministic",
            source_hash="sha256:det",
        )
        json1 = model.to_json()
        json2 = model.to_json()
        assert json1 == json2
        assert isinstance(json1, str)

    def test_base_model_stable_hash(self):
        """stable_hash() must return the same hash for the same model data."""
        from cortex.intelligence.registry.models.base import BaseRegistryModel

        model = BaseRegistryModel(
            id="HASH-001",
            type="test",
            source_file="hash.yaml",
            title="Hash Test",
            source_hash="sha256:hash",
        )
        h1 = model.stable_hash()
        h2 = model.stable_hash()
        assert h1 == h2
        assert h1.startswith("sha256:")
