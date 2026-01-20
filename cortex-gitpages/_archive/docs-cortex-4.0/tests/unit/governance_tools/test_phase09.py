"""Tests for PHASE-09: Governance Tools - 8 ACs"""
import pytest
from src.governance_tools.governance_cli import GovernanceValidator, GovernanceCLI

class TestGovernanceValidator:
    def test_type_hints_valid(self): v = GovernanceValidator(); assert v.validate_type_hints("def func() -> int: pass") is True
    def test_type_hints_invalid(self): v = GovernanceValidator(); assert v.validate_type_hints("def func(): pass") is False
    def test_docstrings_valid(self): v = GovernanceValidator(); assert v.validate_docstrings('"""doc"""') is True
    def test_paths_valid(self): v = GovernanceValidator(); assert v.validate_paths("x = 1") is True
    def test_paths_invalid(self): v = GovernanceValidator(); assert v.validate_paths("/Users/test") is False
    def test_validate_all(self): v = GovernanceValidator(); result = v.validate("def f() -> int:\n  \"\"\"doc\"\"\"\n  pass"); assert result["type_hints"] is True

class TestGovernanceCLI:
    def test_cli_init(self): cli = GovernanceCLI(); assert cli is not None
    def test_report_violations(self): cli = GovernanceCLI(); assert isinstance(cli.report_violations(), list)
