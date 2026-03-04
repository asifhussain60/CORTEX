# AC_START: AC-P125-S2-004
"""
Test Suite: Phase 125 Stage 2 — JSON Stability
Module: Cross-parser deterministic serialization guarantee.
Tests: 6 tests — every typed parser produces stable JSON hashes.
"""

import json

import pytest

from cortex.intelligence.registry.parsers.governance_parser import GovernanceRuleParser
from cortex.intelligence.registry.parsers.workflow_parser import WorkflowTemplateParser
from cortex.intelligence.registry.parsers.pattern_parser import PatternParser


class TestJsonStability:
    """All typed parsers must produce deterministic JSON — identical runs → identical hash."""

    def test_governance_stable_hash(self) -> None:
        """GovernanceRuleModel.stable_hash() returns same value on two calls."""
        parser = GovernanceRuleParser()
        data = {
            "domain": "dev",
            "rules": [{"id": "R-1", "name": "rule", "severity": "high"}],
        }
        m1 = parser.parse(data=data, source_file="g.yaml")
        m2 = parser.parse(data=data, source_file="g.yaml")
        assert m1.stable_hash() == m2.stable_hash()

    def test_workflow_stable_hash(self) -> None:
        """WorkflowTemplateModel.stable_hash() returns same value on two calls."""
        parser = WorkflowTemplateParser()
        data = {
            "workflow": {
                "id": "w/1",
                "name": "Test",
                "steps": [{"id": "s1", "name": "step"}],
            },
        }
        m1 = parser.parse(data=data, source_file="w.yaml")
        m2 = parser.parse(data=data, source_file="w.yaml")
        assert m1.stable_hash() == m2.stable_hash()

    def test_pattern_stable_hash(self) -> None:
        """PatternModel.stable_hash() returns same value on two calls."""
        parser = PatternParser()
        data = {
            "pattern": {
                "name": "Observer",
                "type": "behavioral",
                "description": "event-driven",
            },
        }
        m1 = parser.parse(data=data, source_file="p.yaml")
        m2 = parser.parse(data=data, source_file="p.yaml")
        assert m1.stable_hash() == m2.stable_hash()

    def test_governance_json_sorted_keys(self) -> None:
        """GovernanceRuleModel.to_json() must have sorted keys."""
        parser = GovernanceRuleParser()
        data = {"rules": [{"id": "R-1", "name": "r"}]}
        model = parser.parse(data=data, source_file="g.yaml")
        parsed = json.loads(model.to_json())
        keys = list(parsed.keys())
        assert keys == sorted(keys)

    def test_workflow_json_sorted_keys(self) -> None:
        """WorkflowTemplateModel.to_json() must have sorted keys."""
        parser = WorkflowTemplateParser()
        data = {"workflow": {"id": "w/1", "name": "W"}}
        model = parser.parse(data=data, source_file="w.yaml")
        parsed = json.loads(model.to_json())
        keys = list(parsed.keys())
        assert keys == sorted(keys)

    def test_pattern_json_sorted_keys(self) -> None:
        """PatternModel.to_json() must have sorted keys."""
        parser = PatternParser()
        data = {"pattern": {"name": "P", "type": "structural"}}
        model = parser.parse(data=data, source_file="p.yaml")
        parsed = json.loads(model.to_json())
        keys = list(parsed.keys())
        assert keys == sorted(keys)


# AC_COMPLETE: AC-P125-S2-004 ✅
