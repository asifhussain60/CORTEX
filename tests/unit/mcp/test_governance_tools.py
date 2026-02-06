"""Tests for MCP YAML Loader Tools.

Part of ENH-048 Phase 4: MCP Tool Integration
Tests governance YAML loader tools exposed via MCP.

Author: CORTEX Framework
"""

import pytest
from typing import Dict, Any
from cortex.mcp.tools.governance.yaml_loader_tools import (
    cortex_load_core_rules,
    cortex_load_audit_checklist,
    cortex_load_modes,
    cortex_load_response_format,
    cortex_validate_against_rules,
)


class TestCortexLoadCoreRules:
    """Test cortex_load_core_rules MCP tool."""
    
    def test_load_all_rules(self):
        """Test loading all CORE rules."""
        result = cortex_load_core_rules()
        
        assert "rules" in result
        assert "meta" in result
        assert "total_rules" in result
        assert result["total_rules"] > 0
        assert len(result["rules"]) == result["total_rules"]
        
        # Check first rule structure
        if result["rules"]:
            rule = result["rules"][0]
            assert "id" in rule
            assert "name" in rule
            assert "description" in rule
            assert "enforcement" in rule
    
    def test_load_specific_rule(self):
        """Test loading specific CORE rule by ID."""
        result = cortex_load_core_rules(rule_id="CORE-002")
        
        assert result["total_rules"] == 1
        assert len(result["rules"]) == 1
        assert result["rules"][0]["id"] == "CORE-002"
        assert "Markdown" in result["rules"][0]["name"]
        assert result["rules"][0]["enforcement"] == "BLOCKED"
    
    def test_load_by_enforcement_level(self):
        """Test filtering rules by enforcement level."""
        result = cortex_load_core_rules(enforcement_level="BLOCKED")
        
        assert result["total_rules"] > 0
        for rule in result["rules"]:
            assert rule["enforcement"] == "BLOCKED"
    
    def test_meta_info_present(self):
        """Test meta information is included."""
        result = cortex_load_core_rules()
        
        assert "meta" in result
        assert "version" in result["meta"]
        assert "last_updated" in result["meta"]
        assert "authority" in result["meta"]
    
    def test_load_time_reported(self):
        """Test load time is reported."""
        result = cortex_load_core_rules()
        
        assert "load_time_ms" in result


class TestCortexLoadAuditChecklist:
    """Test cortex_load_audit_checklist MCP tool."""
    
    def test_load_all_checks(self):
        """Test loading all audit checks."""
        result = cortex_load_audit_checklist()
        
        assert "priority_checks" in result
        assert "total_checks" in result
        assert result["total_checks"] > 0
        
        # Check all priorities present
        for priority in ["P0", "P1", "P2", "P3"]:
            if priority in result["priority_checks"]:
                assert "checks" in result["priority_checks"][priority]
                assert "name" in result["priority_checks"][priority]
    
    def test_load_p0_checks_only(self):
        """Test loading P0 checks only."""
        result = cortex_load_audit_checklist(priority="P0")
        
        assert "priority_checks" in result
        assert "P0" in result["priority_checks"]
        # Should only have P0
        assert len(result["priority_checks"]) == 1
        
        # Check P0 structure
        p0 = result["priority_checks"]["P0"]
        assert p0["mandatory"] == True
        assert p0["blocking"] == True
        assert len(p0["checks"]) > 0
    
    def test_load_by_tool_name(self):
        """Test filtering by tool name."""
        result = cortex_load_audit_checklist(tool_name="cortex_lens_analyze")
        
        assert result["total_checks"] > 0
        
        # All returned checks should use cortex_lens_analyze
        for priority_data in result["priority_checks"].values():
            for check in priority_data["checks"]:
                assert "cortex_lens_analyze" in check["tool"]
    
    def test_check_structure(self):
        """Test individual check structure."""
        result = cortex_load_audit_checklist(priority="P0")
        
        assert "P0" in result["priority_checks"]
        checks = result["priority_checks"]["P0"]["checks"]
        assert len(checks) > 0
        
        check = checks[0]
        assert "id" in check
        assert "name" in check
        assert "description" in check
        assert "tool" in check
        assert check["id"].startswith("P0-")
    
    def test_execution_flow_present(self):
        """Test execution flow is included."""
        result = cortex_load_audit_checklist()
        
        assert "execution_flow" in result
        assert isinstance(result["execution_flow"], dict)


class TestCortexLoadModes:
    """Test cortex_load_modes MCP tool."""
    
    def test_load_all_modes(self):
        """Test loading all HEXA-MODEs."""
        result = cortex_load_modes()
        
        assert "modes" in result
        assert "total_modes" in result
        assert result["total_modes"] >= 7  # At least 7 HEXA-MODEs
        
        # Check for key modes
        mode_names = [m["name"] for m in result["modes"].values()]
        assert "AUDIT" in mode_names or "Audit" in mode_names
    
    def test_load_specific_mode(self):
        """Test loading specific mode."""
        result = cortex_load_modes(mode_name="AUDIT")
        
        assert result["total_modes"] == 1
        assert len(result["modes"]) == 1
        
        # Get the mode (key might vary)
        mode = list(result["modes"].values())[0]
        assert "AUDIT" in mode["name"].upper()
        assert "trigger" in mode
        assert "flow" in mode
    
    def test_mode_structure(self):
        """Test mode structure completeness."""
        result = cortex_load_modes()
        
        mode = list(result["modes"].values())[0]
        assert "name" in mode
        assert "trigger" in mode
        assert "description" in mode
        assert "agent" in mode
        assert "priority" in mode
        assert "flow" in mode
        assert isinstance(mode["flow"], list)
    
    def test_meta_info(self):
        """Test meta information is included."""
        result = cortex_load_modes()
        
        assert "meta" in result
        assert "version" in result["meta"]


class TestCortexLoadResponseFormat:
    """Test cortex_load_response_format MCP tool."""
    
    def test_load_response_format(self):
        """Test loading response format standards."""
        result = cortex_load_response_format()
        
        assert "header" in result
        assert "icons" in result
        assert "structure" in result
        assert "meta" in result
    
    def test_header_structure(self):
        """Test header format is present."""
        result = cortex_load_response_format()
        
        assert isinstance(result["header"], dict)
        # Should have header-related keys
        assert len(result["header"]) > 0
    
    def test_icons_present(self):
        """Test icon system is present."""
        result = cortex_load_response_format()
        
        assert isinstance(result["icons"], dict)
        # Should have icon definitions
        assert len(result["icons"]) > 0
    
    def test_structure_present(self):
        """Test structure requirements are present."""
        result = cortex_load_response_format()
        
        assert isinstance(result["structure"], dict)
        assert len(result["structure"]) > 0
    
    def test_anti_patterns_present(self):
        """Test anti-patterns are present."""
        result = cortex_load_response_format()
        
        assert "anti_patterns" in result
        assert isinstance(result["anti_patterns"], list)


class TestCortexValidateAgainstRules:
    """Test cortex_validate_against_rules MCP tool."""
    
    def test_valid_operation(self):
        """Test validation of valid operation."""
        result = cortex_validate_against_rules(
            operation_type="REFACTOR",
            context={
                "intent": "Improve code quality",
                "has_tests": True,
                "markdown_files": [],
            }
        )
        
        assert "valid" in result
        assert "blocked" in result
        assert "violations" in result
        assert result["valid"] == True
        assert result["blocked"] == False
        assert len(result["violations"]) == 0
    
    def test_markdown_violation(self):
        """Test detection of CORE-002 violation."""
        result = cortex_validate_against_rules(
            operation_type="IMPLEMENT",
            context={
                "intent": "Add feature",
                "has_tests": True,
                "markdown_files": ["summary.md", "report.md"],
            }
        )
        
        assert result["valid"] == False
        assert result["blocked"] == True  # CORE-002 is BLOCKED
        assert len(result["violations"]) > 0
        
        # Check violation details
        violation = result["violations"][0]
        assert violation["rule_id"] == "CORE-002"
        assert violation["enforcement"] == "BLOCKED"
        assert "markdown" in violation["violation"].lower()
    
    def test_tdd_violation(self):
        """Test detection of CORE-008 violation."""
        result = cortex_validate_against_rules(
            operation_type="IMPLEMENT",
            context={
                "intent": "Add feature",
                "has_tests": False,
                "markdown_files": [],
            }
        )
        
        assert result["valid"] == False
        assert len(result["violations"]) > 0
        
        # Find CORE-008 violation
        core_008_violation = next(
            (v for v in result["violations"] if v["rule_id"] == "CORE-008"),
            None
        )
        assert core_008_violation is not None
        assert "test" in core_008_violation["violation"].lower()
    
    def test_multiple_violations(self):
        """Test detection of multiple violations."""
        result = cortex_validate_against_rules(
            operation_type="IMPLEMENT",
            context={
                "intent": "Add feature",
                "has_tests": False,
                "markdown_files": ["summary.md"],
            }
        )
        
        assert result["valid"] == False
        assert result["blocked"] == True
        assert len(result["violations"]) >= 2  # CORE-002 and CORE-008
        assert result["total_violations"] >= 2
    
    def test_violation_structure(self):
        """Test violation object structure."""
        result = cortex_validate_against_rules(
            operation_type="IMPLEMENT",
            context={
                "intent": "Add feature",
                "has_tests": False,
                "markdown_files": [],
            }
        )
        
        if result["violations"]:
            violation = result["violations"][0]
            assert "rule_id" in violation
            assert "rule_name" in violation
            assert "enforcement" in violation
            assert "violation" in violation
            assert "description" in violation


class TestToolIntegration:
    """Test integration between tools."""
    
    def test_load_and_validate_workflow(self):
        """Test workflow of loading rules and validating."""
        # Load rules
        rules = cortex_load_core_rules()
        assert rules["total_rules"] > 0
        
        # Validate operation
        result = cortex_validate_against_rules(
            operation_type="IMPLEMENT",
            context={"intent": "Test", "has_tests": True, "markdown_files": []}
        )
        assert "valid" in result
    
    def test_checklist_and_modes_integration(self):
        """Test loading checklist and modes together."""
        checklist = cortex_load_audit_checklist()
        modes = cortex_load_modes()
        
        assert checklist["total_checks"] > 0
        assert modes["total_modes"] > 0
        
        # Both should have meta info
        assert "meta" in checklist
        assert "meta" in modes
    
    def test_all_tools_load_successfully(self):
        """Test that all tools can load without errors."""
        rules = cortex_load_core_rules()
        checklist = cortex_load_audit_checklist()
        modes = cortex_load_modes()
        format_std = cortex_load_response_format()
        
        assert "error" not in rules
        assert "error" not in checklist
        assert "error" not in modes
        assert "error" not in format_std


class TestPerformance:
    """Test performance characteristics."""
    
    def test_load_time_under_threshold(self):
        """Test that load times are acceptable."""
        import time
        
        start = time.time()
        cortex_load_core_rules()
        load_time_1 = (time.time() - start) * 1000
        
        # First load should be < 100ms
        assert load_time_1 < 100, f"Load time {load_time_1}ms exceeds 100ms threshold"
        
        # Second load should be even faster (cached)
        start = time.time()
        cortex_load_core_rules()
        load_time_2 = (time.time() - start) * 1000
        
        # Cached load should be < 50ms
        assert load_time_2 < 50, f"Cached load time {load_time_2}ms exceeds 50ms threshold"
    
    def test_multiple_tools_load_quickly(self):
        """Test that multiple tools load quickly together."""
        import time
        
        start = time.time()
        cortex_load_core_rules()
        cortex_load_audit_checklist()
        cortex_load_modes()
        cortex_load_response_format()
        total_time = (time.time() - start) * 1000
        
        # All tools should load in < 200ms combined
        assert total_time < 200, f"Total load time {total_time}ms exceeds 200ms threshold"
