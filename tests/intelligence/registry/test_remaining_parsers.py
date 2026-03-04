# AC_START: AC-P125-S3-001
"""
Test Suite: Phase 125 — PlanParser, ConfigParser, KnowledgeParser, TemplateParser
Module: Typed parsers for plan, config, knowledge, response-template schemas.
Tests: 44 tests — registration + field extraction for all 4 parser types.
"""

import json

import pytest

from cortex.intelligence.registry.parsers import PARSER_REGISTRY, get_parser_for_type
from cortex.intelligence.registry.parsers.plan_parser import PlanParser
from cortex.intelligence.registry.parsers.config_parser import ConfigParser
from cortex.intelligence.registry.parsers.knowledge_parser import KnowledgeParser
from cortex.intelligence.registry.parsers.template_parser import TemplateParser
from cortex.intelligence.registry.models.plan import PlanModel
from cortex.intelligence.registry.models.config import ConfigModel
from cortex.intelligence.registry.models.knowledge import KnowledgeModel
from cortex.intelligence.registry.models.response_template import ResponseTemplateModel
from cortex.intelligence.registry.models.base import BaseRegistryModel


# ═══════════════════════════════════════════════════════════════════════════════
# PlanParser Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPlanParserRegistration:
    """PlanParser must register via @register_parser."""

    def test_plan_registered(self) -> None:
        assert "plan" in PARSER_REGISTRY

    def test_registered_class(self) -> None:
        assert PARSER_REGISTRY["plan"] is PlanParser

    def test_get_parser_returns_plan(self) -> None:
        assert get_parser_for_type("plan") is PlanParser


class TestPlanParserParse:
    """PlanParser.parse() must produce PlanModel."""

    @pytest.fixture
    def plan_data(self) -> dict:
        return {
            "id": "phase-125",
            "title": "Registry Documentation Viewer",
            "version": "1.0",
            "status": "PLANNED",
            "priority": "P1",
            "governance_authority": ["CORE-008", "CORE-064"],
            "phases": [
                {"id": "phase-125-a", "title": "Base models", "status": "COMPLETE"},
                {"id": "phase-125-b", "title": "Typed parsers", "status": "PLANNED"},
            ],
            "sweep_catalogue": [
                {"id": "GAP-125-01", "title": "No typed models", "status": "OPEN"},
            ],
            "acceptance_criteria": ["All GAPs CLOSED", "Smoke ≥ 2582"],
        }

    def test_returns_plan_model(self, plan_data: dict) -> None:
        result = PlanParser().parse(data=plan_data, source_file="phase-125.yaml")
        assert isinstance(result, PlanModel)

    def test_is_base_subclass(self, plan_data: dict) -> None:
        result = PlanParser().parse(data=plan_data, source_file="phase-125.yaml")
        assert isinstance(result, BaseRegistryModel)

    def test_type_is_plan(self, plan_data: dict) -> None:
        result = PlanParser().parse(data=plan_data, source_file="phase-125.yaml")
        assert result.type == "plan"

    def test_id_extracted(self, plan_data: dict) -> None:
        result = PlanParser().parse(data=plan_data, source_file="phase-125.yaml")
        assert result.id == "phase-125"

    def test_status_extracted(self, plan_data: dict) -> None:
        result = PlanParser().parse(data=plan_data, source_file="phase-125.yaml")
        assert result.status == "PLANNED"

    def test_phases_extracted(self, plan_data: dict) -> None:
        result = PlanParser().parse(data=plan_data, source_file="phase-125.yaml")
        assert isinstance(result.phases, list)
        assert len(result.phases) == 2

    def test_sweep_catalogue_extracted(self, plan_data: dict) -> None:
        result = PlanParser().parse(data=plan_data, source_file="phase-125.yaml")
        assert len(result.sweep_catalogue) == 1
        assert result.sweep_catalogue[0]["id"] == "GAP-125-01"

    def test_acceptance_criteria_extracted(self, plan_data: dict) -> None:
        result = PlanParser().parse(data=plan_data, source_file="phase-125.yaml")
        assert len(result.acceptance_criteria) == 2

    def test_to_json_valid(self, plan_data: dict) -> None:
        result = PlanParser().parse(data=plan_data, source_file="phase-125.yaml")
        parsed = json.loads(result.to_json())
        assert parsed["type"] == "plan"


# ═══════════════════════════════════════════════════════════════════════════════
# ConfigParser Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestConfigParserRegistration:
    """ConfigParser must register via @register_parser."""

    def test_config_registered(self) -> None:
        assert "config" in PARSER_REGISTRY

    def test_registered_class(self) -> None:
        assert PARSER_REGISTRY["config"] is ConfigParser

    def test_get_parser_returns_config(self) -> None:
        assert get_parser_for_type("config") is ConfigParser


class TestConfigParserParse:
    """ConfigParser.parse() must produce ConfigModel."""

    @pytest.fixture
    def config_data(self) -> dict:
        return {
            "repo_id": "cortex",
            "version": "1.0.0",
            "repo_type": "source",
            "description": "CORTEX Repository Configuration",
            "governance_enabled": True,
            "architecture": {
                "orchestrators_wired": 51,
                "mcp_tools_active": 29,
            },
            "file_naming": {
                "python": {"pattern": "^[a-z].*\\.py$"},
            },
        }

    def test_returns_config_model(self, config_data: dict) -> None:
        result = ConfigParser().parse(data=config_data, source_file="system.yaml")
        assert isinstance(result, ConfigModel)

    def test_is_base_subclass(self, config_data: dict) -> None:
        result = ConfigParser().parse(data=config_data, source_file="system.yaml")
        assert isinstance(result, BaseRegistryModel)

    def test_type_is_config(self, config_data: dict) -> None:
        result = ConfigParser().parse(data=config_data, source_file="system.yaml")
        assert result.type == "config"

    def test_id_from_repo_id(self, config_data: dict) -> None:
        result = ConfigParser().parse(data=config_data, source_file="system.yaml")
        assert result.id == "cortex"

    def test_scope_from_repo_type(self, config_data: dict) -> None:
        result = ConfigParser().parse(data=config_data, source_file="system.yaml")
        assert result.scope == "source"

    def test_sections_extracted(self, config_data: dict) -> None:
        result = ConfigParser().parse(data=config_data, source_file="system.yaml")
        assert "architecture" in result.sections
        assert "file_naming" in result.sections

    def test_scalar_in_content(self, config_data: dict) -> None:
        result = ConfigParser().parse(data=config_data, source_file="system.yaml")
        assert result.content.get("governance_enabled") is True

    def test_to_json_valid(self, config_data: dict) -> None:
        result = ConfigParser().parse(data=config_data, source_file="system.yaml")
        parsed = json.loads(result.to_json())
        assert parsed["type"] == "config"


# ═══════════════════════════════════════════════════════════════════════════════
# KnowledgeParser Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestKnowledgeParserRegistration:
    """KnowledgeParser must register via @register_parser."""

    def test_knowledge_registered(self) -> None:
        assert "knowledge" in PARSER_REGISTRY

    def test_registered_class(self) -> None:
        assert PARSER_REGISTRY["knowledge"] is KnowledgeParser

    def test_get_parser_returns_knowledge(self) -> None:
        assert get_parser_for_type("knowledge") is KnowledgeParser


class TestKnowledgeParserParse:
    """KnowledgeParser.parse() must produce KnowledgeModel."""

    @pytest.fixture
    def knowledge_data(self) -> dict:
        return {
            "created": "2026-02-09",
            "updated": "2026-02-25",
            "testing-validation": {
                "guides": [
                    {
                        "path": "testing-validation/tdd-best-practices.yaml",
                        "title": "TDD Best Practices",
                        "keywords": ["tdd", "test", "coverage"],
                    },
                ],
            },
            "security": {
                "guides": [
                    {
                        "path": "security/secure-coding.yaml",
                        "title": "Secure Coding",
                        "keywords": ["security", "owasp"],
                    },
                ],
            },
        }

    def test_returns_knowledge_model(self, knowledge_data: dict) -> None:
        result = KnowledgeParser().parse(data=knowledge_data, source_file="INDEX.yaml")
        assert isinstance(result, KnowledgeModel)

    def test_is_base_subclass(self, knowledge_data: dict) -> None:
        result = KnowledgeParser().parse(data=knowledge_data, source_file="INDEX.yaml")
        assert isinstance(result, BaseRegistryModel)

    def test_type_is_knowledge(self, knowledge_data: dict) -> None:
        result = KnowledgeParser().parse(data=knowledge_data, source_file="INDEX.yaml")
        assert result.type == "knowledge"

    def test_domains_extracted(self, knowledge_data: dict) -> None:
        result = KnowledgeParser().parse(data=knowledge_data, source_file="INDEX.yaml")
        assert "testing-validation" in result.domains
        assert "security" in result.domains

    def test_guides_extracted(self, knowledge_data: dict) -> None:
        result = KnowledgeParser().parse(data=knowledge_data, source_file="INDEX.yaml")
        assert len(result.guides) == 2

    def test_keywords_deduplicated(self, knowledge_data: dict) -> None:
        result = KnowledgeParser().parse(data=knowledge_data, source_file="INDEX.yaml")
        assert isinstance(result.keywords, list)
        assert len(result.keywords) == len(set(result.keywords))

    def test_to_json_valid(self, knowledge_data: dict) -> None:
        result = KnowledgeParser().parse(data=knowledge_data, source_file="INDEX.yaml")
        parsed = json.loads(result.to_json())
        assert parsed["type"] == "knowledge"


# ═══════════════════════════════════════════════════════════════════════════════
# TemplateParser Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestTemplateParserRegistration:
    """TemplateParser must register via @register_parser."""

    def test_response_template_registered(self) -> None:
        assert "response-template" in PARSER_REGISTRY

    def test_registered_class(self) -> None:
        assert PARSER_REGISTRY["response-template"] is TemplateParser

    def test_get_parser_returns_template(self) -> None:
        assert get_parser_for_type("response-template") is TemplateParser


class TestTemplateParserParse:
    """TemplateParser.parse() must produce ResponseTemplateModel."""

    @pytest.fixture
    def template_data(self) -> dict:
        return {
            "name": "CORTEX Response Template",
            "version": "2.0",
            "blocks": [
                {"id": "header", "zone": 1, "required": True},
                {"id": "quote", "zone": 2, "required": True},
            ],
            "zones": [
                {"id": 1, "name": "Identity"},
                {"id": 2, "name": "Quote"},
            ],
            "composable_sections": ["header", "quote", "orchestration", "metrics"],
        }

    def test_returns_response_template_model(self, template_data: dict) -> None:
        result = TemplateParser().parse(data=template_data, source_file="resp.yaml")
        assert isinstance(result, ResponseTemplateModel)

    def test_is_base_subclass(self, template_data: dict) -> None:
        result = TemplateParser().parse(data=template_data, source_file="resp.yaml")
        assert isinstance(result, BaseRegistryModel)

    def test_type_is_response_template(self, template_data: dict) -> None:
        result = TemplateParser().parse(data=template_data, source_file="resp.yaml")
        assert result.type == "response-template"

    def test_blocks_extracted(self, template_data: dict) -> None:
        result = TemplateParser().parse(data=template_data, source_file="resp.yaml")
        assert len(result.blocks) == 2

    def test_zones_extracted(self, template_data: dict) -> None:
        result = TemplateParser().parse(data=template_data, source_file="resp.yaml")
        assert len(result.zones) == 2

    def test_composable_sections_extracted(self, template_data: dict) -> None:
        result = TemplateParser().parse(data=template_data, source_file="resp.yaml")
        assert "header" in result.composable_sections

    def test_to_json_valid(self, template_data: dict) -> None:
        result = TemplateParser().parse(data=template_data, source_file="resp.yaml")
        parsed = json.loads(result.to_json())
        assert parsed["type"] == "response-template"


# AC_COMPLETE: AC-P125-S3-001 ✅
