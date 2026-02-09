"""
Tests for ENH-064 Response Template Wiring Enforcement.

Validates ArchitectureIntegrityAgent enforces response template usage.
"""

import pytest
from cortex.orchestrators.core.enforcement_orchestrator import (
    ArchitectureIntegrityAgent,
    EnforcementResult,
)


class TestENH064Enforcement:
    """Test ENH-064: Response template wiring enforcement."""
    
    @pytest.fixture
    def agent(self):
        """Create ArchitectureIntegrityAgent instance."""
        return ArchitectureIntegrityAgent()
    
    def test_enh_064_blocks_unwired_orchestrator(self, agent):
        """ENH-064: Block orchestrator without template integration."""
        context = {
            "orchestrator_files": {
                "MyOrchestrator": """
                    class MyOrchestrator:
                        def process(self):
                            return "no template"
                """
            }
        }
        
        result = agent.validate(context)
        
        assert result.is_blocked() is True
        assert result.level.value == "blocked"
        assert len(result.violations) == 1
        assert "ENH-064" in result.violations[0]
        assert "MyOrchestrator" in result.violations[0]
        assert "BaseResponseTemplate" in result.violations[0]
    
    def test_enh_064_passes_base_template_inheritance(self, agent):
        """ENH-064: Pass orchestrator inheriting BaseResponseTemplate."""
        context = {
            "orchestrator_files": {
                "TDDOrchestrator": """
                    from cortex.orchestrators.core.base_response_template import BaseResponseTemplate
                    
                    class TDDOrchestrator(BaseResponseTemplate):
                        def process(self):
                            return self.render()
                """
            }
        }
        
        result = agent.validate(context)
        
        assert result.is_blocked() is False
        assert result.level.value == "pass"
        assert len(result.violations) == 0
    
    def test_enh_064_passes_template_integration_mixin(self, agent):
        """ENH-064: Pass orchestrator using TemplateIntegration mixin."""
        context = {
            "orchestrator_files": {
                "LENSSynthesis": """
                    from cortex.orchestrators.response.template_integration import TemplateIntegration
                    
                    class LENSSynthesis(TemplateIntegration):
                        def analyze(self):
                            return self.format_response()
                """
            }
        }
        
        result = agent.validate(context)
        
        assert result.is_blocked() is False
        assert result.level.value == "pass"
        assert len(result.violations) == 0
    
    def test_enh_064_passes_registry_usage(self, agent):
        """ENH-064: Pass orchestrator using template registry."""
        context = {
            "orchestrator_files": {
                "PlanOrchestrator": """
                    from cortex.orchestrators.response.orchestrator_templates import get_orchestrator_template
                    
                    class PlanOrchestrator:
                        def process(self):
                            template = get_orchestrator_template("plan")
                            return template.render()
                """
            }
        }
        
        result = agent.validate(context)
        
        assert result.is_blocked() is False
        assert result.level.value == "pass"
        assert len(result.violations) == 0
    
    def test_enh_064_blocks_multiple_unwired_orchestrators(self, agent):
        """ENH-064: Block multiple orchestrators without template integration."""
        context = {
            "orchestrator_files": {
                "Orchestrator1": "class Orchestrator1: pass",
                "Orchestrator2": "class Orchestrator2: pass",
                "Orchestrator3": "class Orchestrator3: pass",
            }
        }
        
        result = agent.validate(context)
        
        assert result.is_blocked() is True
        assert result.level.value == "blocked"
        assert len(result.violations) == 3
        for violation in result.violations:
            assert "ENH-064" in violation
    
    def test_enh_064_mixed_wired_unwired_orchestrators(self, agent):
        """ENH-064: Block when some orchestrators lack template integration."""
        context = {
            "orchestrator_files": {
                "WiredOrchestrator": "from cortex.orchestrators.core.base_response_template import BaseResponseTemplate",
                "UnwiredOrchestrator": "class UnwiredOrchestrator: pass",
            }
        }
        
        result = agent.validate(context)
        
        assert result.is_blocked() is True
        assert result.level.value == "blocked"
        assert len(result.violations) == 1
        assert "UnwiredOrchestrator" in result.violations[0]
        assert "WiredOrchestrator" not in result.violations[0]
    
    def test_enh_064_passes_empty_orchestrator_files(self, agent):
        """ENH-064: Pass when no orchestrator files provided (no validation needed)."""
        context = {"orchestrator_files": {}}
        
        result = agent.validate(context)
        
        assert result.is_blocked() is False
        assert result.level.value == "pass"
        assert len(result.violations) == 0
    
    def test_enh_064_passes_orchestrator_files_missing(self, agent):
        """ENH-064: Pass when orchestrator_files key absent (optional validation)."""
        context = {"output_files": ["some_file.py"]}
        
        result = agent.validate(context)
        
        assert result.is_blocked() is False
        assert result.level.value == "pass"
        assert len(result.violations) == 0
    
    def test_enh_064_violation_message_includes_options(self, agent):
        """ENH-064: Violation message provides clear resolution options."""
        context = {
            "orchestrator_files": {
                "BadOrchestrator": "class BadOrchestrator: pass"
            }
        }
        
        result = agent.validate(context)
        
        violation = result.violations[0]
        assert "Options:" in violation
        assert "BaseResponseTemplate" in violation
        assert "TemplateIntegration" in violation
        assert "get_orchestrator_template" in violation
    
    def test_enh_064_integration_with_core_035(self, agent):
        """ENH-064: Works alongside CORE-035 versioned filename check."""
        context = {
            "output_files": ["my_orchestrator_v2.py"],
            "orchestrator_files": {
                "MyOrchestrator": "class MyOrchestrator: pass"
            }
        }
        
        result = agent.validate(context)
        
        assert result.is_blocked() is True
        assert result.level.value == "blocked"
        assert len(result.violations) == 2  # Both ENH-064 and CORE-035
        
        enh_064_found = any("ENH-064" in v for v in result.violations)
        core_035_found = any("CORE-035" in v for v in result.violations)
        
        assert enh_064_found
        assert core_035_found
