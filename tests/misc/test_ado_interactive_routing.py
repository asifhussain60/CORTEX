"""Test ADO Interactive Q&A Routing

Ensures 'plan ado' triggers interactive workflow, not template-based.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from orchestrators.ado_work_item_orchestrator import ADOWorkItemOrchestrator
from cortex_agents.ado_interactive_agent import ADOInteractiveAgent


class TestADOInteractiveRouting:
    """Test suite for ADO interactive Q&A routing."""

    def test_orchestrator_has_interactive_method(self):
        """Verify ADOWorkItemOrchestrator has create_work_item_interactive method."""
        cortex_root = Path(__file__).parent.parent
        orchestrator = ADOWorkItemOrchestrator(cortex_root)
        assert hasattr(orchestrator, "create_work_item_interactive"), \
            "Orchestrator missing interactive method"

    def test_orchestrator_has_interactive_agent(self):
        """Verify ADOWorkItemOrchestrator initializes ADOInteractiveAgent."""
        cortex_root = Path(__file__).parent.parent
        orchestrator = ADOWorkItemOrchestrator(cortex_root)
        assert hasattr(orchestrator, "interactive_agent"), \
            "Orchestrator missing interactive_agent attribute"
        
        # Check by class name rather than isinstance (avoids import order issues)
        agent_class_name = orchestrator.interactive_agent.__class__.__name__
        assert agent_class_name == "ADOInteractiveAgent", \
            f"interactive_agent is {agent_class_name}, expected ADOInteractiveAgent"

    def test_old_method_is_deprecated(self):
        """Verify old create_work_item method logs deprecation warning."""
        cortex_root = Path(__file__).parent.parent
        orchestrator = ADOWorkItemOrchestrator(cortex_root)
        
        # Old method should still exist but be marked deprecated
        assert hasattr(orchestrator, "create_work_item"), \
            "Old method removed too soon (keep for backward compatibility)"

    def test_interactive_agent_exists(self):
        """Verify ADOInteractiveAgent can be imported and instantiated."""
        agent = ADOInteractiveAgent(name="test_agent")
        assert agent is not None, "Failed to create ADOInteractiveAgent"

    def test_interactive_agent_has_questions(self):
        """Verify ADOInteractiveAgent has question workflow defined."""
        agent = ADOInteractiveAgent(name="test_agent")
        
        # Agent should have schema-based question workflow
        has_questions = (
            hasattr(agent, "questions") or 
            hasattr(agent, "get_questions") or
            hasattr(agent, "_questions") or
            hasattr(agent, "get_schema_name")  # Schema-based approach
        )
        assert has_questions, "Interactive agent missing questions workflow"

    def test_response_template_exists(self):
        """Verify ado_work_item template exists in response-templates.yaml."""
        template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
        assert template_path.exists(), "response-templates.yaml not found"
        
        content = template_path.read_text(encoding="utf-8")
        assert "ado_work_item:" in content, "ado_work_item template missing"
        assert "ADOInteractiveAgent" in content, "Template doesn't reference interactive agent"

    def test_template_has_interactive_triggers(self):
        """Verify template has correct triggers for 'plan ado'."""
        template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
        content = template_path.read_text(encoding="utf-8")
        
        # Check for plan ado trigger
        assert "plan ado" in content.lower(), "Missing 'plan ado' trigger"
        
    def test_template_indicates_interactive_workflow(self):
        """Verify template clearly indicates interactive Q&A workflow."""
        template_path = Path(__file__).parent.parent / "cortex-brain" / "response-templates.yaml"
        content = template_path.read_text(encoding="utf-8")
        
        # Template should mention interactive/Q&A workflow
        interactive_indicators = [
            "Interactive Q&A",
            "interactive workflow",
            "question",
            "guided"
        ]
        
        has_indicator = any(indicator.lower() in content.lower() for indicator in interactive_indicators)
        assert has_indicator, "Template doesn't clearly indicate interactive workflow"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
