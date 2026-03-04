# AC_START: AC-P125-S2-001
"""
Test Suite: Phase 125 Stage 2 — GovernanceRuleParser
Module: Typed parser for governance-rule schema YAML files.
Tests: 15 tests — field extraction, registry integration, fallback override.
"""

import pytest

from cortex.intelligence.registry.parsers import (
    PARSER_REGISTRY,
    get_parser_for_type,
)
from cortex.intelligence.registry.parsers.governance_parser import GovernanceRuleParser
from cortex.intelligence.registry.models.governance import GovernanceRuleModel
from cortex.intelligence.registry.models.base import BaseRegistryModel


# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def parser() -> GovernanceRuleParser:
    """Return a fresh GovernanceRuleParser instance."""
    return GovernanceRuleParser()


@pytest.fixture
def governance_data_with_rules() -> dict:
    """Governance YAML with top-level ``rules`` list."""
    return {
        "domain": "development",
        "tier": "tier1",
        "category": "development",
        "status": "DEFINED",
        "rules": [
            {
                "id": "DEV-001",
                "name": "Code Review Required",
                "description": "All code changes require peer review",
                "severity": "high",
            },
            {
                "id": "DEV-002",
                "name": "Test Coverage Minimum",
                "description": "Maintain minimum 80% test coverage",
                "severity": "high",
            },
        ],
    }


@pytest.fixture
def governance_kernel_data() -> dict:
    """Governance kernel YAML (meta + rules with enforcement blocks)."""
    return {
        "meta": {
            "version": "1.0",
            "created": "2026-02-06",
            "status": "ACTIVE",
            "enforcement_mode": "BLOCKING",
        },
        "rules": [
            {
                "id": "CORE-047",
                "category": "TOKEN_OPTIMIZATION",
                "severity": "P0",
                "title": "Instruction Files Must Use Backtick References",
                "description": "Prevent auto-loading of markdown files.",
                "enforcement": {
                    "type": "BLOCKING",
                    "scope": [".github/copilot-instructions.md"],
                },
            },
        ],
    }


@pytest.fixture
def governance_data_minimal() -> dict:
    """Minimal governance YAML — only rules list, no domain/category."""
    return {
        "rules": [
            {"id": "R-001", "name": "Minimal rule"},
        ],
    }


# ── Registration Tests ──────────────────────────────────────────────────


class TestGovernanceParserRegistration:
    """GovernanceRuleParser must register via @register_parser."""

    def test_governance_rule_registered_in_parser_registry(self) -> None:
        """'governance-rule' key must exist in PARSER_REGISTRY."""
        assert "governance-rule" in PARSER_REGISTRY

    def test_registered_class_is_governance_rule_parser(self) -> None:
        """PARSER_REGISTRY['governance-rule'] must be GovernanceRuleParser."""
        assert PARSER_REGISTRY["governance-rule"] is GovernanceRuleParser

    def test_get_parser_for_type_returns_governance_parser(self) -> None:
        """get_parser_for_type('governance-rule') must return GovernanceRuleParser."""
        cls = get_parser_for_type("governance-rule")
        assert cls is GovernanceRuleParser

    def test_overrides_generic_fallback(self) -> None:
        """governance-rule must NOT fall back to GenericParser."""
        from cortex.intelligence.registry.parsers.generic_parser import GenericParser

        cls = get_parser_for_type("governance-rule")
        assert cls is not GenericParser


# ── Parse Output Tests ──────────────────────────────────────────────────


class TestGovernanceParserParse:
    """GovernanceRuleParser.parse() must produce GovernanceRuleModel."""

    def test_parse_returns_governance_rule_model(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """parse() must return a GovernanceRuleModel instance."""
        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        assert isinstance(result, GovernanceRuleModel)

    def test_model_is_base_registry_subclass(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """GovernanceRuleModel must be a BaseRegistryModel subclass."""
        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        assert isinstance(result, BaseRegistryModel)

    def test_type_field_is_governance_rule(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """Model.type must be 'governance-rule'."""
        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        assert result.type == "governance-rule"

    def test_domain_extracted(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """GovernanceRuleModel.domain must equal 'development'."""
        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        assert result.domain == "development"

    def test_rules_extracted_as_list(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """GovernanceRuleModel.rules must be a list of rule dicts."""
        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        assert isinstance(result.rules, list)
        assert len(result.rules) == 2

    def test_rule_ids_preserved(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """Each rule dict must preserve its 'id' field."""
        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        ids = [r["id"] for r in result.rules]
        assert "DEV-001" in ids
        assert "DEV-002" in ids

    def test_severity_extracted(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """GovernanceRuleModel.severity must reflect top-level or max rule severity."""
        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        assert result.severity is not None

    def test_enforcement_mode_extracted(
        self, parser: GovernanceRuleParser, governance_kernel_data: dict
    ) -> None:
        """GovernanceRuleModel.enforcement_mode from meta block."""
        result = parser.parse(data=governance_kernel_data, source_file="kernel.yaml")
        assert result.enforcement_mode == "BLOCKING"

    def test_category_extracted(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """GovernanceRuleModel.category must equal 'development'."""
        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        assert result.category == "development"

    def test_to_dict_includes_typed_fields(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """to_dict() must include domain, rules, severity, category."""
        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        d = result.to_dict()
        assert "domain" in d
        assert "rules" in d
        assert "severity" in d
        assert "category" in d

    def test_to_json_is_valid(
        self, parser: GovernanceRuleParser, governance_data_with_rules: dict
    ) -> None:
        """to_json() must produce valid JSON string."""
        import json

        result = parser.parse(data=governance_data_with_rules, source_file="dev-rules.yaml")
        parsed = json.loads(result.to_json())
        assert isinstance(parsed, dict)
        assert parsed["type"] == "governance-rule"


# AC_COMPLETE: AC-P125-S2-001 ✅
