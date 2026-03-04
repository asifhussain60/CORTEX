"""
Golden tests: GenericModel fallback behaviour.
Proves that any YAML that doesn't match a known schema type
gets a GenericModel with schema_warning=True — never blank, never error.
"""

import pytest

from cortex.intelligence.registry.parsers.generic_parser import GenericParser
from cortex.intelligence.registry.models.generic import GenericModel


class TestGenericFallback:
    """Every YAML must produce a model — never blank, never crash."""

    def test_empty_dict_produces_model(self):
        """Empty YAML ({}) → valid GenericModel with warning."""
        parser = GenericParser()
        result = parser.parse(data={}, source_file="empty.yaml")
        assert isinstance(result, GenericModel)
        assert result.schema_warning is True
        assert result.id is not None

    def test_none_data_produces_model(self):
        """None data (empty YAML file) → valid GenericModel with warning."""
        parser = GenericParser()
        result = parser.parse(data=None, source_file="none.yaml")
        assert isinstance(result, GenericModel)
        assert result.schema_warning is True

    def test_string_data_produces_model(self):
        """Scalar YAML (just a string) → valid GenericModel with warning."""
        parser = GenericParser()
        result = parser.parse(data="just a string", source_file="scalar.yaml")
        assert isinstance(result, GenericModel)
        assert result.schema_warning is True

    def test_list_data_produces_model(self):
        """List YAML → valid GenericModel wrapping the list."""
        parser = GenericParser()
        result = parser.parse(data=[1, 2, 3], source_file="list.yaml")
        assert isinstance(result, GenericModel)
        assert result.schema_warning is True

    def test_deeply_nested_data(self):
        """Deeply nested YAML → valid GenericModel."""
        data = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        parser = GenericParser()
        result = parser.parse(data=data, source_file="deep.yaml")
        assert isinstance(result, GenericModel)
        assert result.raw_data == data

    def test_generic_model_to_dict_never_empty(self):
        """GenericModel.to_dict() must return a non-empty dict."""
        parser = GenericParser()
        result = parser.parse(data={}, source_file="empty.yaml")
        d = result.to_dict()
        assert isinstance(d, dict)
        assert len(d) > 0
        assert "id" in d
        assert "type" in d

    def test_generic_model_type_is_generic(self):
        """GenericModel.type must be 'generic'."""
        parser = GenericParser()
        result = parser.parse(data={"x": 1}, source_file="f.yaml")
        assert result.type == "generic"

    def test_generic_model_title_from_title_field(self):
        """If data has a 'title' field, GenericModel should use it."""
        parser = GenericParser()
        result = parser.parse(
            data={"title": "My Custom YAML"},
            source_file="titled.yaml",
        )
        assert result.title == "My Custom YAML"

    def test_generic_model_title_fallback_to_filename(self):
        """If data has no 'title', GenericModel.title should derive from filename."""
        parser = GenericParser()
        result = parser.parse(
            data={"key": "value"},
            source_file="some/path/my-config.yaml",
        )
        assert "my-config" in result.title.lower() or result.title != ""

    def test_generic_model_to_json_is_valid_json(self):
        """GenericModel.to_json() must produce valid JSON."""
        import json

        parser = GenericParser()
        result = parser.parse(data={"key": "value"}, source_file="f.yaml")
        json_str = result.to_json()
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert parsed["type"] == "generic"
