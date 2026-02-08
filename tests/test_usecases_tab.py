"""Phase S6: Use Cases Tab (📋) - TDD Test Suite
Tests for business capabilities, flows, integrations, and LLM insights
"""

import pytest
from pydantic import ValidationError
from cortex.orchestrators.onboarding.dashboard_schema_models import UseCasesTab


@pytest.fixture
def valid_usecases():
    """Valid use cases tab with all business capabilities"""
    return {
        "detected_capabilities": [
            {
                "id": "cap-001",
                "business_capability": "User Authentication",
                "technical_name": "auth_service",
                "description": "Handle user login and session management",
                "business_value": "Enables secure access control",
                "actors": ["End User", "Admin"],
                "systems": ["auth_db", "ldap_provider"],
                "complexity": "medium",
                "maturity": "stable",
                "modernization_score": 85.0
            },
            {
                "id": "cap-002",
                "business_capability": "Data Analytics",
                "technical_name": "analytics_engine",
                "description": "Process and analyze business metrics",
                "business_value": "Provides business intelligence",
                "actors": ["Data Analyst", "Executive"],
                "systems": ["data_warehouse", "bi_tool"],
                "complexity": "high",
                "maturity": "emerging",
                "modernization_score": 65.5
            }
        ],
        "business_flows": [
            {
                "name": "User Onboarding",
                "description": "Complete onboarding workflow for new users",
                "steps": ["Sign up", "Email verification", "Profile setup", "First login"],
                "primary_actor": "End User",
                "preconditions": ["Email provided", "Password meets requirements"],
                "success_criteria": ["User logged in", "Profile created"]
            },
            {
                "name": "Data Export",
                "description": "Export analytics to Excel",
                "steps": ["Select date range", "Choose metrics", "Generate export", "Download"],
                "primary_actor": "Data Analyst",
                "preconditions": ["User has analytics permissions"],
                "success_criteria": ["File downloaded", "No errors in export"]
            }
        ],
        "integrations": [
            {
                "system": "Salesforce",
                "type": "API",
                "description": "CRM system integration for customer data"
            },
            {
                "system": "Stripe",
                "type": "API",
                "description": "Payment processing integration"
            },
            {
                "system": "Data Warehouse",
                "type": "Database",
                "description": "Central data repository"
            }
        ],
        "stakeholder_mapping": {
            "Executive": ["Report generation", "Budget planning", "Strategic planning"],
            "Product Owner": ["Feature prioritization", "Roadmap planning"],
            "Dev Manager": ["Sprint planning", "Performance monitoring"],
            "Engineer": ["Code implementation", "Bug fixes", "Documentation"]
        }
    }


@pytest.fixture
def minimal_usecases():
    """Minimal valid use cases (only required fields)"""
    return {
        "detected_capabilities": [],
        "business_flows": [],
        "integrations": [],
        "stakeholder_mapping": {}
    }


class TestBusinessCapabilities:
    """Test business capability detection and validation"""
    
    def test_valid_capability(self, valid_usecases):
        """Test valid business capability"""
        tab = UseCasesTab(**valid_usecases)
        assert len(tab.detected_capabilities) == 2
        assert tab.detected_capabilities[0].business_capability == "User Authentication"
        assert tab.detected_capabilities[0].complexity == "medium"
        assert tab.detected_capabilities[0].maturity == "stable"
    
    def test_capability_complexity_validation(self, valid_usecases):
        """Test capability complexity levels"""
        valid_usecases["detected_capabilities"] = [
            {
                "id": "cap-1",
                "business_capability": "Test",
                "technical_name": "test",
                "description": "desc",
                "business_value": "value",
                "complexity": "low",
                "maturity": "mature",
                "modernization_score": 75.0
            }
        ]
        tab = UseCasesTab(**valid_usecases)
        assert tab.detected_capabilities[0].complexity == "low"
    
    def test_capability_maturity_levels(self, valid_usecases):
        """Test all maturity levels"""
        valid_usecases["detected_capabilities"] = []
        for maturity in ["emerging", "stable", "mature"]:
            valid_usecases["detected_capabilities"].append({
                "id": f"cap-{maturity}",
                "business_capability": f"Capability {maturity}",
                "technical_name": f"tech_{maturity}",
                "description": "Test",
                "business_value": "Value",
                "complexity": "medium",
                "maturity": maturity,
                "modernization_score": 70.0
            })
        
        tab = UseCasesTab(**valid_usecases)
        assert len(tab.detected_capabilities) == 3
        maturities = [c.maturity for c in tab.detected_capabilities]
        assert "emerging" in maturities
        assert "stable" in maturities
        assert "mature" in maturities
    
    def test_modernization_score_range(self, valid_usecases):
        """Test modernization score validation (0-100)"""
        valid_usecases["detected_capabilities"][0]["modernization_score"] = 100.0
        tab = UseCasesTab(**valid_usecases)
        assert tab.detected_capabilities[0].modernization_score == 100.0
    
    def test_modernization_score_zero(self, valid_usecases):
        """Test modernization score at zero"""
        valid_usecases["detected_capabilities"] = [
            {
                "id": "cap-old",
                "business_capability": "Legacy System",
                "technical_name": "legacy",
                "description": "Old system",
                "business_value": "Still works",
                "complexity": "low",
                "maturity": "mature",
                "modernization_score": 0.0
            }
        ]
        tab = UseCasesTab(**valid_usecases)
        assert tab.detected_capabilities[0].modernization_score == 0.0
    
    def test_actors_and_systems(self, valid_usecases):
        """Test capability actors and systems"""
        tab = UseCasesTab(**valid_usecases)
        cap = tab.detected_capabilities[0]
        assert "End User" in cap.actors
        assert "Admin" in cap.actors
        assert "auth_db" in cap.systems
    
    def test_empty_capabilities_list(self, valid_usecases):
        """Test empty capabilities list is valid"""
        valid_usecases["detected_capabilities"] = []
        tab = UseCasesTab(**valid_usecases)
        assert tab.detected_capabilities == []
    
    def test_many_capabilities(self, valid_usecases):
        """Test many capabilities"""
        valid_usecases["detected_capabilities"] = [
            {
                "id": f"cap-{i}",
                "business_capability": f"Capability {i}",
                "technical_name": f"tech_{i}",
                "description": "Test",
                "business_value": "Value",
                "complexity": "medium",
                "maturity": "stable",
                "modernization_score": float(50 + i)
            }
            for i in range(10)
        ]
        tab = UseCasesTab(**valid_usecases)
        assert len(tab.detected_capabilities) == 10


class TestBusinessFlows:
    """Test business flow validation"""
    
    def test_valid_flow(self, valid_usecases):
        """Test valid business flow"""
        tab = UseCasesTab(**valid_usecases)
        assert len(tab.business_flows) == 2
        flow = tab.business_flows[0]
        assert flow.name == "User Onboarding"
        assert flow.primary_actor == "End User"
        assert len(flow.steps) == 4
    
    def test_flow_steps(self, valid_usecases):
        """Test flow steps"""
        tab = UseCasesTab(**valid_usecases)
        steps = tab.business_flows[0].steps
        assert "Sign up" in steps
        assert "Email verification" in steps
    
    def test_flow_preconditions(self, valid_usecases):
        """Test flow preconditions"""
        tab = UseCasesTab(**valid_usecases)
        flow = tab.business_flows[0]
        assert len(flow.preconditions) == 2
        assert "Email provided" in flow.preconditions
    
    def test_flow_success_criteria(self, valid_usecases):
        """Test flow success criteria"""
        tab = UseCasesTab(**valid_usecases)
        flow = tab.business_flows[0]
        assert len(flow.success_criteria) == 2
        assert "User logged in" in flow.success_criteria
    
    def test_empty_flows(self, valid_usecases):
        """Test empty flows list is valid"""
        valid_usecases["business_flows"] = []
        tab = UseCasesTab(**valid_usecases)
        assert tab.business_flows == []
    
    def test_flow_with_empty_collections(self, valid_usecases):
        """Test flow with empty steps/preconditions/criteria"""
        valid_usecases["business_flows"] = [
            {
                "name": "Simple Flow",
                "description": "Test",
                "steps": [],
                "primary_actor": "User",
                "preconditions": [],
                "success_criteria": []
            }
        ]
        tab = UseCasesTab(**valid_usecases)
        assert len(tab.business_flows[0].steps) == 0
        assert len(tab.business_flows[0].preconditions) == 0


class TestIntegrations:
    """Test external system integrations"""
    
    def test_valid_integrations(self, valid_usecases):
        """Test valid integrations"""
        tab = UseCasesTab(**valid_usecases)
        assert len(tab.integrations) == 3
        assert tab.integrations[0].system == "Salesforce"
        assert tab.integrations[0].type == "API"
    
    def test_integration_types(self, valid_usecases):
        """Test all integration types"""
        tab = UseCasesTab(**valid_usecases)
        types = {i.type for i in tab.integrations}
        assert "API" in types
        assert "Database" in types
    
    def test_integration_description(self, valid_usecases):
        """Test integration descriptions"""
        tab = UseCasesTab(**valid_usecases)
        desc = tab.integrations[0].description
        assert isinstance(desc, str)
        assert len(desc) > 0
    
    def test_empty_integrations(self, valid_usecases):
        """Test empty integrations list is valid"""
        valid_usecases["integrations"] = []
        tab = UseCasesTab(**valid_usecases)
        assert tab.integrations == []
    
    def test_many_integrations(self, valid_usecases):
        """Test many integrations"""
        valid_usecases["integrations"] = [
            {
                "system": f"System{i}",
                "type": "API" if i % 2 == 0 else "Database",
                "description": f"Integration {i}"
            }
            for i in range(15)
        ]
        tab = UseCasesTab(**valid_usecases)
        assert len(tab.integrations) == 15


class TestStakeholderMapping:
    """Test stakeholder to capability mapping"""
    
    def test_valid_mapping(self, valid_usecases):
        """Test valid stakeholder mapping"""
        tab = UseCasesTab(**valid_usecases)
        assert "Executive" in tab.stakeholder_mapping
        assert len(tab.stakeholder_mapping["Executive"]) == 3
        assert "Report generation" in tab.stakeholder_mapping["Executive"]
    
    def test_multiple_stakeholders(self, valid_usecases):
        """Test multiple stakeholder types"""
        tab = UseCasesTab(**valid_usecases)
        stakeholders = set(tab.stakeholder_mapping.keys())
        assert "Executive" in stakeholders
        assert "Product Owner" in stakeholders
        assert "Dev Manager" in stakeholders
        assert "Engineer" in stakeholders
    
    def test_empty_mapping(self, valid_usecases):
        """Test empty stakeholder mapping is valid"""
        valid_usecases["stakeholder_mapping"] = {}
        tab = UseCasesTab(**valid_usecases)
        assert tab.stakeholder_mapping == {}
    
    def test_stakeholder_capabilities(self, valid_usecases):
        """Test stakeholder capabilities list"""
        tab = UseCasesTab(**valid_usecases)
        engineer_caps = tab.stakeholder_mapping["Engineer"]
        assert isinstance(engineer_caps, list)
        assert len(engineer_caps) >= 2
    
    def test_dynamic_stakeholder_mapping(self, valid_usecases):
        """Test dynamic stakeholder mapping"""
        valid_usecases["stakeholder_mapping"] = {
            "Analyst": ["Data analysis", "Reporting"],
            "Manager": ["Oversight", "Planning"],
            "Support": ["Issue resolution", "Customer support"]
        }
        tab = UseCasesTab(**valid_usecases)
        assert "Analyst" in tab.stakeholder_mapping
        assert len(tab.stakeholder_mapping["Analyst"]) == 2


class TestUseCasesEdgeCases:
    """Test edge cases and validation"""
    
    def test_minimal_valid_usecases(self, minimal_usecases):
        """Test minimal valid use cases"""
        tab = UseCasesTab(**minimal_usecases)
        assert tab.detected_capabilities == []
        assert tab.business_flows == []
        assert tab.integrations == []
        assert tab.stakeholder_mapping == {}
    
    def test_all_empty_collections(self, valid_usecases):
        """Test all collections empty"""
        empty = {
            "detected_capabilities": [],
            "business_flows": [],
            "integrations": [],
            "stakeholder_mapping": {}
        }
        tab = UseCasesTab(**empty)
        assert len(tab.detected_capabilities) == 0
        assert len(tab.business_flows) == 0
        assert len(tab.integrations) == 0
        assert len(tab.stakeholder_mapping) == 0
    
    def test_complex_scenario(self, valid_usecases):
        """Test complex real-world scenario"""
        # Many capabilities, flows, integrations
        valid_usecases["detected_capabilities"] = [
            {
                "id": f"cap-{i}",
                "business_capability": f"Cap {i}",
                "technical_name": f"tech_{i}",
                "description": f"Description {i}",
                "business_value": f"Value {i}",
                "complexity": ["low", "medium", "high"][i % 3],
                "maturity": ["emerging", "stable", "mature"][i % 3],
                "modernization_score": (i * 10) % 100
            }
            for i in range(20)
        ]
        tab = UseCasesTab(**valid_usecases)
        assert len(tab.detected_capabilities) == 20
    
    def test_special_characters_in_descriptions(self, valid_usecases):
        """Test special characters in text fields"""
        valid_usecases["detected_capabilities"][0]["description"] = "Test with special chars: @#$%&*()"
        tab = UseCasesTab(**valid_usecases)
        assert "@#$%&*()" in tab.detected_capabilities[0].description
    
    def test_unicode_in_text_fields(self, valid_usecases):
        """Test unicode characters in text fields"""
        valid_usecases["business_flows"][0]["name"] = "用户入职 (User Onboarding)"
        tab = UseCasesTab(**valid_usecases)
        assert "用户入职" in tab.business_flows[0].name
    
    def test_long_text_fields(self, valid_usecases):
        """Test long text fields"""
        long_desc = "A" * 500
        valid_usecases["detected_capabilities"][0]["description"] = long_desc
        tab = UseCasesTab(**valid_usecases)
        assert len(tab.detected_capabilities[0].description) == 500
    
    def test_boundary_modernization_scores(self, valid_usecases):
        """Test boundary values for modernization scores"""
        valid_usecases["detected_capabilities"] = [
            {
                "id": "cap-0",
                "business_capability": "Legacy",
                "technical_name": "legacy",
                "description": "Test",
                "business_value": "Value",
                "complexity": "low",
                "maturity": "mature",
                "modernization_score": 0.0
            },
            {
                "id": "cap-100",
                "business_capability": "Modern",
                "technical_name": "modern",
                "description": "Test",
                "business_value": "Value",
                "complexity": "high",
                "maturity": "stable",
                "modernization_score": 100.0
            },
            {
                "id": "cap-50",
                "business_capability": "Mid",
                "technical_name": "mid",
                "description": "Test",
                "business_value": "Value",
                "complexity": "medium",
                "maturity": "emerging",
                "modernization_score": 50.5
            }
        ]
        tab = UseCasesTab(**valid_usecases)
        assert tab.detected_capabilities[0].modernization_score == 0.0
        assert tab.detected_capabilities[1].modernization_score == 100.0
        assert tab.detected_capabilities[2].modernization_score == 50.5
