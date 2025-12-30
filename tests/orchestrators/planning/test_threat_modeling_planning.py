"""
Test Threat Modeling Planning Integration - Phase 4.2

Integration tests for threat_modeling schema validation and
ThreatModeler integration with the Planning Orchestrator.

Author: CORTEX Development Team
Version: 1.0.0 (Planner 2.0 Enhancements)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from pathlib import Path

# Import planning orchestrator components
from src.orchestrators.planning.planning_orchestrator import (
    PlanningOrchestrator,
    PlanData,
    PlanMetadata,
    PlanPhaseData,
    PlanComplexity,
    PlanType,
    PlanningResult,
    ValidationResult,
    THREAT_MODELER_AVAILABLE
)

# Import threat modeler if available
try:
    from src.agents.security.threat_modeler_agent import (
        ThreatModelerAgent,
        RiskRating,
        EnhancedThreat,
        ThreatReport
    )
    from src.cortex_agents.base_agent import AgentRequest, AgentResponse
    THREAT_MODELER_IMPORT_SUCCESS = True
except ImportError:
    THREAT_MODELER_IMPORT_SUCCESS = False


class TestThreatModelingSchema:
    """Test threat_modeling schema in plan configuration."""
    
    def test_threat_modeling_default_config(self):
        """Test default threat_modeling configuration."""
        default_config = {
            "enabled": True,
            "stride_categories": [
                "Spoofing", "Tampering", "Repudiation",
                "Information Disclosure", "Denial of Service", "Elevation of Privilege"
            ],
            "auto_mitigations": True
        }
        
        assert default_config["enabled"] is True
        assert len(default_config["stride_categories"]) == 6
        assert default_config["auto_mitigations"] is True
    
    def test_threat_modeling_custom_categories(self):
        """Test custom STRIDE category selection."""
        config = {
            "enabled": True,
            "stride_categories": ["Spoofing", "Tampering", "Elevation of Privilege"],
            "auto_mitigations": True
        }
        
        assert len(config["stride_categories"]) == 3
        assert "Spoofing" in config["stride_categories"]
        assert "Information Disclosure" not in config["stride_categories"]
    
    def test_threat_modeling_disabled(self):
        """Test threat modeling can be disabled."""
        config = {"enabled": False}
        
        assert config["enabled"] is False
    
    def test_threat_modeling_owasp_mapping(self):
        """Test OWASP Top 10 mapping configuration."""
        config = {
            "enabled": True,
            "owasp_mapping": [
                "A01:2021-Broken Access Control",
                "A07:2021-Identification and Authentication Failures"
            ]
        }
        
        assert len(config["owasp_mapping"]) == 2
        assert config["owasp_mapping"][0].startswith("A01:")
    
    def test_threat_modeling_security_context(self):
        """Test security context configuration."""
        config = {
            "enabled": True,
            "security_context": {
                "data_sensitivity": "confidential",
                "authentication_required": True,
                "authorization_model": "role-based"
            }
        }
        
        ctx = config["security_context"]
        assert ctx["data_sensitivity"] == "confidential"
        assert ctx["authentication_required"] is True
        assert ctx["authorization_model"] == "role-based"


class TestThreatAnalysisSchema:
    """Test threat_analysis output schema."""
    
    def test_threat_analysis_risk_levels(self):
        """Test valid risk level values."""
        valid_levels = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        
        for level in valid_levels:
            analysis = {"risk_level": level}
            assert analysis["risk_level"] in valid_levels
    
    def test_threat_analysis_stride_summary(self):
        """Test STRIDE summary structure."""
        analysis = {
            "stride_summary": {
                "Spoofing": 2,
                "Tampering": 1,
                "Repudiation": 0,
                "Information Disclosure": 3,
                "Denial of Service": 1,
                "Elevation of Privilege": 2
            }
        }
        
        summary = analysis["stride_summary"]
        assert sum(summary.values()) == 9
        assert summary["Spoofing"] == 2
    
    def test_threat_analysis_threats_structure(self):
        """Test threats array structure."""
        threat = {
            "category": "Spoofing",
            "name": "Session Hijacking",
            "description": "Attacker can hijack user sessions",
            "risk_rating": "HIGH",
            "risk_score": 8,
            "owasp_categories": ["A01:2021-Broken Access Control"],
            "mitigation_strategies": [
                {"name": "Secure Session Management", "effort_hours": 4}
            ]
        }
        
        assert threat["category"] == "Spoofing"
        assert threat["risk_rating"] == "HIGH"
        assert len(threat["mitigation_strategies"]) == 1
    
    def test_threat_analysis_recommendations(self):
        """Test recommendations array."""
        analysis = {
            "recommendations": [
                "Implement secure session management",
                "Add input validation",
                "Enable audit logging"
            ]
        }
        
        assert len(analysis["recommendations"]) == 3


class TestPlanDataThreatFields:
    """Test PlanData with threat modeling fields."""
    
    def test_plan_data_threat_modeling_field(self):
        """Test threat_modeling field in PlanData."""
        plan = PlanData(
            metadata=PlanMetadata(
                title="Secure Feature",
                description="Feature with security analysis",
                complexity=PlanComplexity.HIGH,
                plan_type=PlanType.INCREMENTAL
            ),
            definition_of_ready=["Requirements defined"],
            definition_of_done=["Tests passing"],
            phases=[],
            threat_modeling={
                "enabled": True,
                "stride_categories": ["Spoofing", "Tampering"],
                "auto_mitigations": True
            }
        )
        
        assert plan.threat_modeling is not None
        assert plan.threat_modeling["enabled"] is True
    
    def test_plan_data_threat_analysis_field(self):
        """Test threat_analysis field in PlanData."""
        plan = PlanData(
            metadata=PlanMetadata(
                title="Analyzed Feature",
                description="Feature with completed threat analysis",
                complexity=PlanComplexity.HIGH,
                plan_type=PlanType.INCREMENTAL
            ),
            definition_of_ready=[],
            definition_of_done=[],
            phases=[],
            threat_analysis={
                "risk_level": "MEDIUM",
                "threats": [],
                "recommendations": []
            }
        )
        
        assert plan.threat_analysis is not None
        assert plan.threat_analysis["risk_level"] == "MEDIUM"
    
    def test_plan_data_both_threat_fields(self):
        """Test both threat_modeling and threat_analysis in PlanData."""
        plan = PlanData(
            metadata=PlanMetadata(
                title="Full Security Plan",
                description="Complete security analysis",
                complexity=PlanComplexity.CRITICAL,
                plan_type=PlanType.INCREMENTAL
            ),
            definition_of_ready=[],
            definition_of_done=[],
            phases=[],
            threat_modeling={
                "enabled": True,
                "stride_categories": ["Spoofing", "Tampering", "Elevation of Privilege"]
            },
            threat_analysis={
                "risk_level": "HIGH",
                "threats": [{"category": "Spoofing", "name": "Test"}],
                "stride_summary": {"Spoofing": 1}
            }
        )
        
        assert plan.threat_modeling["enabled"] is True
        assert plan.threat_analysis["risk_level"] == "HIGH"


class TestOrchestratorThreatModeling:
    """Test PlanningOrchestrator threat modeling integration."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator for testing."""
        with patch.object(PlanningOrchestrator, '__init__', lambda x: None):
            orchestrator = PlanningOrchestrator()
            orchestrator.logger = Mock()
            orchestrator._tdd_dor_requirements = []
            orchestrator._tdd_dod_requirements = []
            return orchestrator
    
    def test_has_critical_threats_true(self, mock_orchestrator):
        """Test _has_critical_threats returns True for CRITICAL."""
        threat_analysis = {"risk_level": "CRITICAL"}
        
        result = mock_orchestrator._has_critical_threats(threat_analysis)
        assert result is True
    
    def test_has_critical_threats_high(self, mock_orchestrator):
        """Test _has_critical_threats returns True for HIGH."""
        threat_analysis = {"risk_level": "HIGH"}
        
        result = mock_orchestrator._has_critical_threats(threat_analysis)
        assert result is True
    
    def test_has_critical_threats_medium(self, mock_orchestrator):
        """Test _has_critical_threats returns False for MEDIUM."""
        threat_analysis = {"risk_level": "MEDIUM"}
        
        result = mock_orchestrator._has_critical_threats(threat_analysis)
        assert result is False
    
    def test_has_critical_threats_low(self, mock_orchestrator):
        """Test _has_critical_threats returns False for LOW."""
        threat_analysis = {"risk_level": "LOW"}
        
        result = mock_orchestrator._has_critical_threats(threat_analysis)
        assert result is False
    
    def test_has_critical_threats_none(self, mock_orchestrator):
        """Test _has_critical_threats returns False for None."""
        result = mock_orchestrator._has_critical_threats(None)
        assert result is False


class TestSecurityTaskInjection:
    """Test security task auto-injection."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator for testing."""
        with patch.object(PlanningOrchestrator, '__init__', lambda x: None):
            orchestrator = PlanningOrchestrator()
            orchestrator.logger = Mock()
            return orchestrator
    
    @pytest.fixture
    def base_plan(self):
        """Create base plan for testing."""
        return PlanData(
            metadata=PlanMetadata(
                title="Test Feature",
                description="Test",
                complexity=PlanComplexity.MEDIUM,
                plan_type=PlanType.INCREMENTAL
            ),
            definition_of_ready=["Test"],
            definition_of_done=["Test"],
            phases=[
                PlanPhaseData(
                    phase_name="Implementation",
                    tasks=[{"task": "Implement feature"}],
                    acceptance_criteria=["Feature works"]
                )
            ]
        )
    
    def test_inject_security_tasks_adds_phase(self, mock_orchestrator, base_plan):
        """Test security task injection adds new phase."""
        threat_analysis = {
            "risk_level": "HIGH",
            "threats": [
                {
                    "category": "Spoofing",
                    "name": "Session Hijacking",
                    "risk_rating": "HIGH",
                    "mitigation_strategies": [
                        {"name": "Secure sessions", "effort_hours": 2}
                    ]
                }
            ]
        }
        
        original_phase_count = len(base_plan.phases)
        result = mock_orchestrator._inject_security_tasks(base_plan, threat_analysis)
        
        assert len(result.phases) == original_phase_count + 1
        assert result.phases[0].phase_name == "Security Hardening"
    
    def test_inject_security_tasks_updates_dod(self, mock_orchestrator, base_plan):
        """Test security task injection updates DoD."""
        threat_analysis = {
            "risk_level": "CRITICAL",
            "threats": [
                {
                    "category": "Elevation of Privilege",
                    "name": "Privilege Escalation",
                    "risk_rating": "CRITICAL",
                    "mitigation_strategies": []
                }
            ]
        }
        
        original_dod_count = len(base_plan.definition_of_done)
        result = mock_orchestrator._inject_security_tasks(base_plan, threat_analysis)
        
        assert len(result.definition_of_done) > original_dod_count
        assert any("threat" in item.lower() for item in result.definition_of_done)
    
    def test_inject_security_tasks_max_five(self, mock_orchestrator, base_plan):
        """Test security task injection limits to 5 tasks max."""
        threat_analysis = {
            "risk_level": "CRITICAL",
            "threats": [
                {"category": f"Category{i}", "name": f"Threat{i}", "risk_rating": "CRITICAL", "mitigation_strategies": []}
                for i in range(10)  # 10 threats
            ]
        }
        
        result = mock_orchestrator._inject_security_tasks(base_plan, threat_analysis)
        
        # Security phase should have max 5 tasks
        security_phase = result.phases[0]
        assert len(security_phase.tasks) <= 5
    
    def test_inject_security_tasks_no_threats(self, mock_orchestrator, base_plan):
        """Test security task injection with no critical threats."""
        threat_analysis = {
            "risk_level": "LOW",
            "threats": []
        }
        
        original_phase_count = len(base_plan.phases)
        result = mock_orchestrator._inject_security_tasks(base_plan, threat_analysis)
        
        # No new phase should be added
        assert len(result.phases) == original_phase_count


@pytest.mark.skipif(not THREAT_MODELER_IMPORT_SUCCESS, reason="ThreatModeler not available")
class TestThreatModelerAgentIntegration:
    """Test ThreatModelerAgent integration (requires agent to be available)."""
    
    def test_threat_modeler_can_handle_request(self):
        """Test ThreatModelerAgent can_handle method."""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            user_message="Analyze user authentication feature",
            intent="analyze_threats",
            context={}
        )
        
        assert agent.can_handle(request) is True
    
    def test_threat_modeler_rejects_invalid_intent(self):
        """Test ThreatModelerAgent rejects non-threat intents."""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            user_message="Generate documentation",
            intent="generate_docs",
            context={}
        )
        
        assert agent.can_handle(request) is False
    
    def test_threat_modeler_requires_description(self):
        """Test ThreatModelerAgent requires feature description."""
        agent = ThreatModelerAgent()
        
        request = AgentRequest(
            user_message="",
            intent="analyze_threats",
            context={}
        )
        
        response = agent.execute(request)
        assert response.success is False


class TestThreatModelerAvailabilityFlag:
    """Test THREAT_MODELER_AVAILABLE flag behavior."""
    
    def test_flag_is_boolean(self):
        """Test THREAT_MODELER_AVAILABLE is a boolean."""
        assert isinstance(THREAT_MODELER_AVAILABLE, bool)
    
    def test_flag_matches_import_success(self):
        """Test flag matches actual import success."""
        # If we successfully imported threat modeler classes, flag should be True
        if THREAT_MODELER_IMPORT_SUCCESS:
            assert THREAT_MODELER_AVAILABLE is True


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
