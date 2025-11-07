"""
Tests for ChangeGovernor Agent

Validates governance rule enforcement, risk assessment,
and change validation functionality.
"""

import pytest
from datetime import datetime
from CORTEX.src.cortex_agents.change_governor import ChangeGovernor
from CORTEX.src.cortex_agents.base_agent import AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import IntentType, RiskLevel


class TestChangeGovernorBasics:
    """Test basic ChangeGovernor functionality"""
    
    def test_governor_initialization(self, mock_tier_apis):
        """Test ChangeGovernor initialization"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        assert governor.name == "Governor"
        assert governor.tier1 is not None
        assert governor.tier2 is not None
        assert governor.tier3 is not None
        assert len(governor.supported_intents) > 0
        assert len(governor.protected_paths) > 0
    
    def test_governor_can_handle_check_governance(self, mock_tier_apis):
        """Test ChangeGovernor handles check_governance intents"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="check_governance",
            context={"files": ["src/app.py"], "operation": "modify"},
            user_message="Check if I can modify app.py"
        )
        
        assert governor.can_handle(request) is True
    
    def test_governor_can_handle_assess_risk(self, mock_tier_apis):
        """Test ChangeGovernor handles assess_risk intents"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="assess_risk",
            context={"files": ["data.py"], "operation": "delete"},
            user_message="Assess risk of deleting data.py"
        )
        
        assert governor.can_handle(request) is True
    
    def test_governor_rejects_invalid_intent(self, mock_tier_apis):
        """Test ChangeGovernor rejects non-governance intents"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="code",
            context={},
            user_message="Write some code"
        )
        
        assert governor.can_handle(request) is False


class TestRuleCompliance:
    """Test governance rule compliance checking"""
    
    def test_rule_3_archive_forbidden(self, mock_tier_apis):
        """Test Rule #3: Delete over archive"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="check_governance",
            context={"files": ["old_code.py"], "operation": "archive"},
            user_message="Archive old code"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        assert len(response.result["violations"]) > 0
        assert any("Rule #3" in v for v in response.result["violations"])
    
    def test_rule_20_tdd_required(self, mock_tier_apis):
        """Test Rule #20: TDD requires tests"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="check_governance",
            context={"files": ["src/feature.py"], "operation": "create"},
            user_message="Create new feature without tests"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        violations = response.result["violations"]
        assert any("Rule #20" in v and "test" in v.lower() for v in violations)
        assert response.result["requires_tests"] is True
    
    def test_rule_22_protected_file_deletion(self, mock_tier_apis):
        """Test Rule #22: Brain protection"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="check_governance",
            context={
                "files": ["governance/rules.md"],
                "operation": "delete"
            },
            user_message="Delete governance rules"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        assert len(response.result["violations"]) > 0
        assert any("Rule #22" in v and "protected" in v.lower() for v in response.result["violations"])
        assert response.result["allowed"] is False
    
    def test_rule_23_incremental_creation(self, mock_tier_apis):
        """Test Rule #23: Incremental file creation"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="check_governance",
            context={
                "files": ["large_module.py"],
                "operation": "create",
                "file_size_estimate": 300  # > 150 lines
            },
            user_message="Create large file"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        violations = response.result["violations"]
        assert any("Rule #23" in v and "incremental" in v.lower() for v in violations)


class TestRiskAssessment:
    """Test risk level assessment"""
    
    def test_low_risk_simple_modification(self, mock_tier_apis):
        """Test LOW risk for simple modifications"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="assess_risk",
            context={
                "files": ["utils.py"],
                "operation": "modify"
            },
            user_message="Update utility function"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        assert response.result["risk_level"] == RiskLevel.LOW.value
        assert response.result["allowed"] is True
    
    def test_medium_risk_multiple_files(self, mock_tier_apis):
        """Test MEDIUM risk for multiple files"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="assess_risk",
            context={
                "files": [f"file{i}.py" for i in range(10)],
                "operation": "modify"
            },
            user_message="Update 10 files"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        assert response.result["risk_level"] == RiskLevel.MEDIUM.value
    
    def test_high_risk_deletion(self, mock_tier_apis):
        """Test HIGH risk for deletions"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="assess_risk",
            context={
                "files": ["module.py"],
                "operation": "delete"
            },
            user_message="Delete module"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        assert response.result["risk_level"] == RiskLevel.HIGH.value
    
    def test_high_risk_protected_file(self, mock_tier_apis):
        """Test HIGH risk for protected file modification"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="assess_risk",
            context={
                "files": ["CORTEX/src/tier1/conversation_manager.py"],
                "operation": "modify"
            },
            user_message="Modify tier1 core file"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        assert response.result["risk_level"] == RiskLevel.HIGH.value
    
    def test_critical_risk_governance_violations(self, mock_tier_apis):
        """Test CRITICAL risk for governance violations"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="assess_risk",
            context={
                "files": ["code.py"],
                "operation": "archive"  # Violates Rule #3
            },
            user_message="Archive old code"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        assert response.result["risk_level"] == RiskLevel.CRITICAL.value


class TestMultiRuleValidation:
    """Test validation of multiple rules simultaneously"""
    
    def test_multiple_violations(self, mock_tier_apis):
        """Test detection of multiple rule violations"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="check_governance",
            context={
                "files": ["governance/rules.md"],
                "operation": "delete"
            },
            user_message="Delete governance rules"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        # Should detect Rule #22 violation (protected file)
        assert len(response.result["violations"]) > 0
        assert response.result["risk_level"] == RiskLevel.CRITICAL.value
        assert response.result["allowed"] is False
    
    def test_tdd_with_tests_provided(self, mock_tier_apis):
        """Test TDD rule with tests provided"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="check_governance",
            context={
                "files": ["src/feature.py", "tests/test_feature.py"],
                "operation": "create"
            },
            user_message="Create feature with tests"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        # Should NOT violate Rule #20 because tests are included
        tdd_violations = [v for v in response.result["violations"] if "Rule #20" in v]
        assert len(tdd_violations) == 0
        assert response.result["requires_tests"] is True  # Still requires tests
    
    def test_allowed_with_warnings(self, mock_tier_apis):
        """Test change allowed but with warnings"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="check_governance",
            context={
                "files": ["app.py"],
                "operation": "delete"  # HIGH risk but no violations
            },
            user_message="Delete app file"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        assert response.result["allowed"] is True  # Allowed
        assert response.result["risk_level"] == RiskLevel.HIGH.value  # But risky
    
    def test_clean_change_approval(self, mock_tier_apis):
        """Test clean change with no violations"""
        governor = ChangeGovernor("Governor", **mock_tier_apis)
        
        request = AgentRequest(
            intent="check_governance",
            context={
                "files": ["docs/README.md"],
                "operation": "modify"
            },
            user_message="Update documentation"
        )
        
        response = governor.execute(request)
        
        assert response.success is True
        assert response.result["allowed"] is True
        assert len(response.result["violations"]) == 0
        assert response.result["risk_level"] == RiskLevel.LOW.value
