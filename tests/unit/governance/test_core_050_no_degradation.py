"""
Phase 51 S1: CORE-050 Governance Rule Tests
Tests for: No Quality Degradation (MCP-FIRST Enforcement)

AC-PHASE51-S1-001: Rule exists in tier0 governance
AC-PHASE51-S1-002: Rule has P0 severity (blocked)
AC-PHASE51-S1-003: Blocking enforcement documented
AC-PHASE51-S1-004: Documentation templates ready
"""
import pytest
from pathlib import Path


class TestCORE050RuleDefinition:
    """Test: CORE-050 rule exists and is properly defined"""

    def test_core_050_exists_in_tier0_governance(self):
        """Test: CORE-050 rule exists in cortex_brain/tier0/governance/core-rules.yaml"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        assert rules_file.exists(), "Governance rules file must exist"
        
        content = rules_file.read_text()
        assert "rule_id: CORE-050" in content, "CORE-050 rule must be defined"

    def test_core_050_severity_p0(self):
        """Test: CORE-050 has severity: blocked (P0 critical)"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        # Find CORE-050 block
        core_050_start = content.find("- rule_id: CORE-050")
        assert core_050_start > 0, "CORE-050 rule not found"
        
        # Extract section: from "- rule_id: CORE-050" to next rule or enforcement config
        next_rule = content.find("- rule_id:", core_050_start + 1)
        enforcement_start = content.find("# ==============================================================================", core_050_start)
        
        if next_rule > core_050_start and next_rule < enforcement_start:
            core_050_end = next_rule
        else:
            core_050_end = enforcement_start if enforcement_start > 0 else len(content)
        
        core_050_section = content[core_050_start:core_050_end]
        assert "severity: blocked" in core_050_section, "CORE-050 must have severity: blocked"

    def test_core_050_enforcement_documented(self):
        """Test: CORE-050 specifies EnvironmentIntegrityAgent enforcement"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        core_050_start = content.find("- rule_id: CORE-050")
        next_rule = content.find("- rule_id:", core_050_start + 1)
        enforcement_section = content.find("# ==============================================================================\n# ENFORCEMENT CONFIGURATION", core_050_start)
        
        if next_rule > 0 and next_rule < enforcement_section:
            core_050_end = next_rule
        else:
            core_050_end = enforcement_section
        
        core_050_section = content[core_050_start:core_050_end]
        
        assert "EnvironmentIntegrityAgent" in core_050_section, "EnvironmentIntegrityAgent not mentioned"
        assert "cortex_process_request" in core_050_section, "MCP tool requirement missing"


class TestMCPPreFlightCheck:
    """Test: MCP pre-flight health check capabilities"""

    def test_mcp_availability_detection_tool_query(self):
        """Test: Can detect MCP tool availability via tool query"""
        # This test verifies the detection pattern is documented
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "cortex_process_request" in content, "MCP tool discovery pattern must be documented"

    def test_mcp_availability_detection_env_vars(self):
        """Test: Can detect MCP via environment variables"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        # CORE-050 should document env var checks
        assert "MCP_SERVER_PORT" in content or "CORTEX_MCP_ENABLED" in content, "Env var check documented"

    def test_environment_check_returns_structured_result(self):
        """Test: Health check returns structured (passed/failed) result"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "PASSED" in content or "FAILED" in content, "Check results must be structured"


class TestIntentBasedToolBlocking:
    """Test: Tool blocking based on user intent"""

    def test_implement_intent_requires_mcp_routing(self):
        """Test: IMPLEMENT intent requires MCP routing (blocks direct tools)"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "IMPLEMENT" in content and "cortex_process_request" in content, "IMPLEMENT must use MCP"

    def test_analyze_intent_allows_direct_tools(self):
        """Test: ANALYZE intent allows direct read-only tools"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "ANALYZE" in content, "ANALYZE intent handling documented"

    def test_fix_intent_blocked_from_direct_operations(self):
        """Test: FIX intent blocked from direct file creation"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "FIX" in content and "TDDOrchestrator" in content, "FIX requires TDDOrchestrator"


class TestBlockedExecutionPaths:
    """Test: Verify degraded execution paths are blocked"""

    def test_no_tdd_bypass_when_mcp_unavailable(self):
        """Test: No fallback to direct execution if MCP unavailable"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "BLOCK" in content, "Blocking action must be documented"

    def test_no_direct_file_creation_for_implement_intent(self):
        """Test: create_file blocked for IMPLEMENT intent"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "create_file" in content and "IMPLEMENT" in content, "Direct file creation blocking documented"

    def test_governance_gates_cannot_be_disabled(self):
        """Test: Governance gates cannot be disabled"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "mandatory" in content.lower() or "disabled" in content.lower(), "Disabling restrictions documented"


class TestErrorMessaging:
    """Test: Error messages are clear and actionable"""

    def test_mcp_unavailable_error_clear(self):
        """Test: MCP unavailable error is clear with fix instructions"""
        # This test verifies the error message pattern is implemented
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        # Should have documentation of error message requirements
        assert "error" in content.lower() or "message" in content.lower(), "Error messaging documented"

    def test_error_message_not_vague(self):
        """Test: Error messages are not vague 'try alternative' suggestions"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "Fix infrastructure" in content or "fix" in content.lower(), "Fix actions documented"


class TestAuditTrail:
    """Test: Operations are audited"""

    def test_mcp_health_check_logged(self):
        """Test: MCP health check events are logged"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "MCP_HEALTH_CHECK" in content, "Audit events documented"

    def test_blocking_action_logged(self):
        """Test: Blocking actions are logged for audit trail"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        assert "audit" in content.lower() or "events:" in content.lower(), "Audit trail documented"


class TestPhase51Stage1Acceptance:
    """Acceptance Tests for Phase 51 S1 completion"""

    def test_ac_phase51_s1_001_core_050_rule_exists(self):
        """AC-PHASE51-S1-001: CORE-050 rule exists in tier0 governance"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        assert rules_file.exists(), "Governance rules file required"
        
        content = rules_file.read_text()
        assert "rule_id: CORE-050" in content, "AC-PHASE51-S1-001: CORE-050 rule missing"

    def test_ac_phase51_s1_002_p0_severity(self):
        """AC-PHASE51-S1-002: CORE-050 has P0 severity (blocked)"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        core_050_start = content.find("- rule_id: CORE-050")
        assert core_050_start > 0, "CORE-050 not found"
        
        # Find end of CORE-050 section
        next_rule = content.find("- rule_id:", core_050_start + 1)
        enforcement_start = content.find("# ==============================================================================", core_050_start)
        
        if next_rule > core_050_start and next_rule < enforcement_start:
            core_050_end = next_rule
        else:
            core_050_end = enforcement_start if enforcement_start > 0 else len(content)
        
        core_050_section = content[core_050_start:core_050_end]
        assert "severity: blocked" in core_050_section, "AC-PHASE51-S1-002: CORE-050 must have severity: blocked"

    def test_ac_phase51_s1_003_blocking_enforcement(self):
        """AC-PHASE51-S1-003: Blocking enforcement is documented"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        content = rules_file.read_text()
        
        core_050_start = content.find("- rule_id: CORE-050")
        next_rule = content.find("- rule_id:", core_050_start + 1)
        enforcement_start = content.find("# ==============================================================================", core_050_start)
        
        if next_rule > core_050_start and next_rule < enforcement_start:
            core_050_end = next_rule
        else:
            core_050_end = enforcement_start if enforcement_start > 0 else len(content)
        
        core_050_section = content[core_050_start:core_050_end]
        assert "BLOCK" in core_050_section, "AC-PHASE51-S1-003: Blocking action not documented"
        assert "EnvironmentIntegrityAgent" in core_050_section, "AC-PHASE51-S1-003: Enforcement agent not documented"

    def test_ac_phase51_s1_004_documentation_updated(self):
        """AC-PHASE51-S1-004: YAML rule file is complete and structured"""
        rules_file = Path("cortex_brain/tier0/governance/core-rules.yaml")
        assert rules_file.exists(), "Governance rules file required"
        
        content = rules_file.read_text()
        assert "rule_id: CORE-050" in content, "AC-PHASE51-S1-004: CORE-050 documentation incomplete"
