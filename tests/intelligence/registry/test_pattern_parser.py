# AC_START: AC-P125-S2-003
"""
Test Suite: Phase 125 Stage 2 — PatternParser
Module: Typed parser for pattern schema YAML files.
Tests: 15 tests — field extraction, registry integration, fallback override.
"""

import pytest

from cortex.intelligence.registry.parsers import (
    PARSER_REGISTRY,
    get_parser_for_type,
)
from cortex.intelligence.registry.parsers.pattern_parser import PatternParser
from cortex.intelligence.registry.models.pattern import PatternModel
from cortex.intelligence.registry.models.base import BaseRegistryModel


# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def parser() -> PatternParser:
    """Return a fresh PatternParser instance."""
    return PatternParser()


@pytest.fixture
def pattern_data() -> dict:
    """Pattern YAML with top-level ``pattern`` block."""
    return {
        "pattern": {
            "name": "Strategy Workflow",
            "type": "behavioral",
            "description": (
                "Workflow execution strategy is selected at runtime based on context."
            ),
            "cortex_usage": [
                "ParallelRunner selects EXECUTION_PROFILES based on test tier",
                "WorkflowEngine selects step execution strategy",
            ],
            "participants": {
                "context": "WorkflowEngine / ParallelRunner",
                "strategy_interface": "ExecutionProfile / WorkflowStep",
                "concrete_strategies": "SmokePlan, UnitPlan, IntegrationPlan",
            },
            "when_to_use": [
                "Multiple algorithms exist for the same operation",
                "Runtime context determines optimal approach",
            ],
            "anti_patterns": [
                "Hard-coded if/elif chains for strategy selection",
            ],
            "references": [
                "cortex/testing/framework/parallel_runner.py",
                "cortex/core/workflow_engine.py",
            ],
        },
    }


@pytest.fixture
def pattern_data_minimal() -> dict:
    """Minimal pattern YAML — only name."""
    return {
        "pattern": {
            "name": "Minimal Pattern",
        },
    }


# ── Registration Tests ──────────────────────────────────────────────────


class TestPatternParserRegistration:
    """PatternParser must register via @register_parser."""

    def test_pattern_registered_in_parser_registry(self) -> None:
        """'pattern' key must exist in PARSER_REGISTRY."""
        assert "pattern" in PARSER_REGISTRY

    def test_registered_class_is_pattern_parser(self) -> None:
        """PARSER_REGISTRY['pattern'] must be PatternParser."""
        assert PARSER_REGISTRY["pattern"] is PatternParser

    def test_get_parser_for_type_returns_pattern_parser(self) -> None:
        """get_parser_for_type('pattern') must return PatternParser."""
        cls = get_parser_for_type("pattern")
        assert cls is PatternParser

    def test_overrides_generic_fallback(self) -> None:
        """pattern must NOT fall back to GenericParser."""
        from cortex.intelligence.registry.parsers.generic_parser import GenericParser

        cls = get_parser_for_type("pattern")
        assert cls is not GenericParser


# ── Parse Output Tests ──────────────────────────────────────────────────


class TestPatternParserParse:
    """PatternParser.parse() must produce PatternModel."""

    def test_parse_returns_pattern_model(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """parse() must return a PatternModel instance."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert isinstance(result, PatternModel)

    def test_model_is_base_registry_subclass(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """PatternModel must be a BaseRegistryModel subclass."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert isinstance(result, BaseRegistryModel)

    def test_type_field_is_pattern(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """Model.type must be 'pattern'."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert result.type == "pattern"

    def test_pattern_name_extracted(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """PatternModel.pattern_name must equal 'Strategy Workflow'."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert result.pattern_name == "Strategy Workflow"

    def test_pattern_type_extracted(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """PatternModel.pattern_type must equal 'behavioral'."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert result.pattern_type == "behavioral"

    def test_description_extracted(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """PatternModel.description must contain the description text."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert "runtime" in result.description.lower()

    def test_cortex_usage_extracted(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """PatternModel.cortex_usage must be a list."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert isinstance(result.cortex_usage, list)
        assert len(result.cortex_usage) == 2

    def test_participants_extracted(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """PatternModel.participants must be a dict."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert isinstance(result.participants, dict)
        assert "context" in result.participants

    def test_when_to_use_extracted(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """PatternModel.when_to_use must be a list."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert isinstance(result.when_to_use, list)
        assert len(result.when_to_use) == 2

    def test_anti_patterns_extracted(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """PatternModel.anti_patterns must be a list."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert isinstance(result.anti_patterns, list)
        assert len(result.anti_patterns) == 1

    def test_references_extracted(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """PatternModel.file_references must be a list of paths."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        assert isinstance(result.file_references, list)
        assert len(result.file_references) == 2

    def test_to_dict_includes_typed_fields(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """to_dict() must include pattern_name, pattern_type, cortex_usage."""
        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        d = result.to_dict()
        assert "pattern_name" in d
        assert "pattern_type" in d
        assert "cortex_usage" in d

    def test_to_json_is_valid(
        self, parser: PatternParser, pattern_data: dict
    ) -> None:
        """to_json() must produce valid JSON string."""
        import json

        result = parser.parse(data=pattern_data, source_file="strategy.yaml")
        parsed = json.loads(result.to_json())
        assert isinstance(parsed, dict)
        assert parsed["type"] == "pattern"


# AC_COMPLETE: AC-P125-S2-003 ✅
