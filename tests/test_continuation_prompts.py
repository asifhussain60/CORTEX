"""
Test suite for continuation prompt generation in ResponseRenderer.

Validates that concise, accurate continuation prompts are added to every
response to enable cross-session resume capability.
"""

import pytest
from unittest.mock import Mock
from pathlib import Path

from src.orchestrators.response_renderer import ResponseRenderer
from src.orchestrators.base.base_orchestrator import OrchestratorResult, OrchestratorStatus


class TestContinuationPrompts:
    """Test continuation prompt generation for all orchestrator types."""
    
    @pytest.fixture
    def renderer(self):
        """Create ResponseRenderer instance."""
        return ResponseRenderer(
            template_path="cortex-brain/response-templates-v4.yaml"
        )
    
    def test_planning_continuation_prompt(self, renderer):
        """Test continuation prompt for Planning orchestrator."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Plan created successfully",
            data={
                'plan_id': 'user-authentication-plan',
                'current_phase': 3
            }
        )
        
        context = {
            'orchestrator_type': 'planning_v5',
            'orchestrator_name': 'Planning System v5'
        }
        
        markdown = renderer.render(result, context=context)
        
        # Should contain continuation prompt
        assert "📋 **Resume Work:**" in markdown
        assert "continue plan user-authentication-plan from phase 3" in markdown
        assert "CONTINUATION-PROMPT.md" in markdown
    
    def test_ado_continuation_prompt(self, renderer):
        """Test continuation prompt for ADO orchestrator."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="ADO work items generated",
            data={
                'feature_name': 'oauth2-integration',
                'work_items_dir': 'cortex-brain/documents/ado/work-items/oauth2-integration'
            }
        )
        
        context = {
            'orchestrator_type': 'ado_orchestrator_v2',
            'orchestrator_name': 'ADO v2'
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "📋 **Resume Work:**" in markdown
        assert "continue ado oauth2-integration" in markdown
        assert "README.md" in markdown
    
    def test_tdd_continuation_prompt(self, renderer):
        """Test continuation prompt for TDD orchestrator."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Tests created and passing",
            data={
                'module_name': 'user_validator',
                'test_file': 'tests/test_user_validator.py'
            }
        )
        
        context = {
            'orchestrator_type': 'tdd_orchestrator',
            'orchestrator_name': 'TDD Mastery v4'
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "📋 **Resume Work:**" in markdown
        assert "tdd continue user_validator" in markdown
        assert "test_user_validator.py" in markdown
    
    def test_investigation_continuation_prompt(self, renderer):
        """Test continuation prompt for Investigation orchestrator."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Root cause identified",
            data={
                'issue_name': 'routing-failures',
                'report_dir': 'cortex-brain/documents/investigations/routing-failures/'
            }
        )
        
        context = {
            'orchestrator_type': 'investigation_orchestrator',
            'orchestrator_name': 'Investigation v2'
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "📋 **Resume Work:**" in markdown
        assert "investigate continue routing-failures" in markdown
        assert "00-investigation-report.md" in markdown
    
    def test_cleanup_continuation_prompt(self, renderer):
        """Test continuation prompt for Cleanup orchestrator."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Cleanup complete",
            data={
                'report_file': 'reports/cleanup-cache-2026-01-05/cleanup-log.md'
            }
        )
        
        context = {
            'orchestrator_type': 'cleanup_orchestrator',
            'orchestrator_name': 'Cleanup v2',
            'operation_type': 'cleanup cache'
        }
        
        markdown = renderer.render(result, context=context)
        
        assert "📋 **Resume Work:**" in markdown
        assert "cleanup continue" in markdown or "cleanup cache continue" in markdown
        assert "cleanup-log.md" in markdown
    
    def test_generic_continuation_prompt(self, renderer):
        """Test generic continuation prompt for unknown orchestrators."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Operation completed"
        )
        
        context = {
            'orchestrator_type': 'unknown_orchestrator',
            'orchestrator_name': 'Custom Orchestrator'
        }
        
        markdown = renderer.render(result, context=context)
        
        # Should still have continuation prompt (generic fallback)
        assert "📋 **Resume Work:**" in markdown
        assert "cortex-brain/documents/" in markdown
    
    def test_continuation_prompt_always_present(self, renderer):
        """Test that continuation prompt is ALWAYS added (even without next_steps)."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Simple operation completed",
            data={}
        )
        
        context = {
            'orchestrator_type': 'planning_v5',
            'next_steps': []  # Empty next_steps
        }
        
        markdown = renderer.render(result, context=context)
        
        # Continuation prompt should STILL be present (either full or fallback format)
        assert ("📋 **Resume Work:**" in markdown or "📋 **Resume:**" in markdown)
    
    def test_continuation_prompt_with_next_steps(self, renderer):
        """Test that continuation prompt works alongside traditional next_steps."""
        result = OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Operation completed",
            data={'plan_id': 'test-plan'}
        )
        
        context = {
            'orchestrator_type': 'planning_v5',
            'next_steps': [
                "Review generated plan",
                "Execute phase 1",
                "Validate results"
            ]
        }
        
        markdown = renderer.render(result, context=context)
        
        # Should have BOTH next_steps AND continuation prompt
        assert "**Next Steps:**" in markdown
        assert "1. Review generated plan" in markdown
        assert "2. Execute phase 1" in markdown
        assert "3. Validate results" in markdown
        assert "📋 **Resume Work:**" in markdown
        assert "continue plan test-plan" in markdown
    
    def test_continuation_prompt_format_consistency(self, renderer):
        """Test that all continuation prompts follow consistent format."""
        orchestrators = [
            ('planning_v5', {'plan_id': 'test'}),
            ('ado_orchestrator_v2', {'feature_name': 'test'}),
            ('tdd_orchestrator', {'module_name': 'test'}),
            ('investigation_orchestrator', {'issue_name': 'test'}),
        ]
        
        for orch_type, data in orchestrators:
            result = OrchestratorResult(
                status=OrchestratorStatus.COMPLETED,
                success=True,
                message="Test",
                data=data
            )
            
            context = {'orchestrator_type': orch_type}
            markdown = renderer.render(result, context=context)
            
            # All should follow format: "📋 **Resume Work:** `command` *(see `file`)*"
            assert "📋 **Resume Work:**" in markdown
            assert "`continue" in markdown or "`tdd continue" in markdown or "`investigate continue" in markdown
            assert "*(see" in markdown or "*(check" in markdown or "*(current" in markdown


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
