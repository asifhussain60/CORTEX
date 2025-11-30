"""
Test Git Checkpoint Integration with CortexEntry

Validates that git checkpoint enforcement is properly wired into
the main request processing flow.

Author: Asif Hussain
Date: November 30, 2025
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.entry_point.cortex_entry import CortexEntry
from src.tier0.brain_protector import ProtectionResult, Severity, Violation, ProtectionLayer


class TestGitCheckpointIntegration:
    """Test git checkpoint enforcement in main request flow."""
    
    @pytest.fixture
    def temp_brain_path(self):
        """Create temporary brain directory for testing."""
        temp_dir = tempfile.mkdtemp(prefix="cortex_test_brain_")
        brain_path = Path(temp_dir)
        
        # Create required subdirectories
        (brain_path / "tier1").mkdir(parents=True)
        (brain_path / "tier2").mkdir(parents=True)
        (brain_path / "tier3").mkdir(parents=True)
        (brain_path / "corpus-callosum").mkdir(parents=True)
        
        # Create minimal brain-protection-rules.yaml
        rules_content = """
tier0_instincts:
  - TDD_ENFORCEMENT
  - GIT_CHECKPOINT_ENFORCEMENT
  - PREVENT_DIRTY_STATE_WORK

protection_layers:
  - layer_id: instinct_immutability
    name: Instinct Immutability
    rules:
      - rule_id: GIT_CHECKPOINT_ENFORCEMENT
        severity: BLOCKED
        description: Git checkpoint required before development
"""
        (brain_path / "brain-protection-rules.yaml").write_text(rules_content)
        
        yield brain_path
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @patch('src.entry_point.cortex_entry.config')
    def test_brain_protector_initialized(self, mock_config, temp_brain_path):
        """Test that BrainProtector is initialized on CortexEntry creation."""
        mock_config.brain_path = str(temp_brain_path)
        mock_config.ensure_paths_exist = Mock()
        
        with patch('src.entry_point.cortex_entry.Tier1API'), \
             patch('src.entry_point.cortex_entry.KnowledgeGraph'), \
             patch('src.entry_point.cortex_entry.ContextIntelligence'), \
             patch('src.entry_point.cortex_entry.SessionManager'), \
             patch('src.entry_point.cortex_entry.TemplateLoader'):
            
            entry = CortexEntry(brain_path=str(temp_brain_path), skip_setup_check=True)
            
            # Verify brain protector was initialized
            assert hasattr(entry, 'brain_protector')
            assert entry.brain_protector is not None
    
    @patch('src.entry_point.cortex_entry.config')
    def test_development_request_triggers_validation(self, mock_config, temp_brain_path):
        """Test that development keywords trigger brain protector validation."""
        mock_config.brain_path = str(temp_brain_path)
        mock_config.ensure_paths_exist = Mock()
        
        with patch('src.entry_point.cortex_entry.Tier1API'), \
             patch('src.entry_point.cortex_entry.KnowledgeGraph'), \
             patch('src.entry_point.cortex_entry.ContextIntelligence'), \
             patch('src.entry_point.cortex_entry.SessionManager'), \
             patch('src.entry_point.cortex_entry.TemplateLoader'):
            
            entry = CortexEntry(brain_path=str(temp_brain_path), skip_setup_check=True)
            
            # Mock brain protector to return BLOCKED result
            mock_violation = Violation(
                layer=ProtectionLayer.INSTINCT_IMMUTABILITY,
                rule="GIT_CHECKPOINT_ENFORCEMENT",
                severity=Severity.BLOCKED,
                description="Git checkpoint required before starting development work",
                evidence="Starting development: implement authentication"
            )
            
            mock_result = ProtectionResult(
                severity=Severity.BLOCKED,
                violations=[mock_violation],
                decision="BLOCK",
                message="Git checkpoint required",
                alternatives=[
                    "Create commit checkpoint: git commit -m 'checkpoint: before auth'",
                    "Create tag checkpoint: git tag checkpoint-$(date +%Y%m%d-%H%M%S)",
                    "Stash changes: git stash save 'checkpoint: before auth'"
                ],
                override_required=True
            )
            
            entry.brain_protector.analyze_request = Mock(return_value=mock_result)
            
            # Mock other components
            entry.tier1.process_message = Mock()
            entry.context_manager.build_context = Mock(return_value={
                'token_usage': {'total': 100, 'budget': 500, 'within_budget': True},
                'relevance_scores': {'tier1': 0.8, 'tier2': 0.7, 'tier3': 0.6}
            })
            
            # Process development request
            response = entry.process("implement authentication feature", resume_session=False)
            
            # Verify brain protector was called
            assert entry.brain_protector.analyze_request.called
            
            # Verify request was blocked
            assert "Request Blocked" in response or "BLOCKED" in response
            assert "Git checkpoint required" in response
            assert "alternatives" in response.lower() or "required actions" in response.lower()
    
    @patch('src.entry_point.cortex_entry.config')
    def test_non_development_request_passes_through(self, mock_config, temp_brain_path):
        """Test that non-development requests pass brain protector validation."""
        mock_config.brain_path = str(temp_brain_path)
        mock_config.ensure_paths_exist = Mock()
        
        with patch('src.entry_point.cortex_entry.Tier1API'), \
             patch('src.entry_point.cortex_entry.KnowledgeGraph'), \
             patch('src.entry_point.cortex_entry.ContextIntelligence'), \
             patch('src.entry_point.cortex_entry.SessionManager'), \
             patch('src.entry_point.cortex_entry.TemplateLoader'):
            
            entry = CortexEntry(brain_path=str(temp_brain_path), skip_setup_check=True)
            
            # Mock brain protector to return ALLOW result
            mock_result = ProtectionResult(
                severity=Severity.SAFE,
                violations=[],
                decision="ALLOW",
                message="No violations detected",
                alternatives=[],
                override_required=False
            )
            
            entry.brain_protector.analyze_request = Mock(return_value=mock_result)
            
            # Mock other components
            entry.tier1.process_message = Mock()
            entry.context_manager.build_context = Mock(return_value={
                'token_usage': {'total': 100, 'budget': 500, 'within_budget': True},
                'relevance_scores': {'tier1': 0.8, 'tier2': 0.7, 'tier3': 0.6}
            })
            entry.router.execute = Mock(return_value=Mock(success=True, result={}))
            entry.agent_executor.execute_routing_decision = Mock(return_value=Mock(
                success=True,
                message="Query successful",
                duration_ms=100
            ))
            entry.formatter.format = Mock(return_value="Formatted response")
            
            # Process non-development request
            response = entry.process("what files are in src/?", resume_session=False)
            
            # Verify brain protector was called
            assert entry.brain_protector.analyze_request.called
            
            # Verify request was NOT blocked
            assert "Request Blocked" not in response
            assert "BLOCKED" not in response
    
    @patch('src.entry_point.cortex_entry.config')
    def test_modification_request_conversion(self, mock_config, temp_brain_path):
        """Test AgentRequest to ModificationRequest conversion."""
        mock_config.brain_path = str(temp_brain_path)
        mock_config.ensure_paths_exist = Mock()
        
        with patch('src.entry_point.cortex_entry.Tier1API'), \
             patch('src.entry_point.cortex_entry.KnowledgeGraph'), \
             patch('src.entry_point.cortex_entry.ContextIntelligence'), \
             patch('src.entry_point.cortex_entry.SessionManager'), \
             patch('src.entry_point.cortex_entry.TemplateLoader'):
            
            entry = CortexEntry(brain_path=str(temp_brain_path), skip_setup_check=True)
            
            # Create mock AgentRequest
            from src.cortex_agents.base_agent import AgentRequest
            agent_request = AgentRequest(
                intent="implement",
                user_message="implement authentication in src/auth.py",
                context={"justification": "security requirement"},
                conversation_id="test-conv-123"
            )
            
            # Convert to ModificationRequest
            mod_request = entry._create_modification_request(agent_request)
            
            # Verify conversion
            assert mod_request.intent == "implement"
            assert mod_request.description == "implement authentication in src/auth.py"
            assert "src/auth.py" in mod_request.files
            assert mod_request.justification == "security requirement"
            assert mod_request.metadata["conversation_id"] == "test-conv-123"
    
    @patch('src.entry_point.cortex_entry.config')
    def test_brain_protector_error_does_not_block(self, mock_config, temp_brain_path):
        """Test that brain protector errors don't block request processing."""
        mock_config.brain_path = str(temp_brain_path)
        mock_config.ensure_paths_exist = Mock()
        
        with patch('src.entry_point.cortex_entry.Tier1API'), \
             patch('src.entry_point.cortex_entry.KnowledgeGraph'), \
             patch('src.entry_point.cortex_entry.ContextIntelligence'), \
             patch('src.entry_point.cortex_entry.SessionManager'), \
             patch('src.entry_point.cortex_entry.TemplateLoader'):
            
            entry = CortexEntry(brain_path=str(temp_brain_path), skip_setup_check=True)
            
            # Mock brain protector to raise exception
            entry.brain_protector.analyze_request = Mock(side_effect=Exception("Test error"))
            
            # Mock other components
            entry.tier1.process_message = Mock()
            entry.context_manager.build_context = Mock(return_value={
                'token_usage': {'total': 100, 'budget': 500, 'within_budget': True},
                'relevance_scores': {'tier1': 0.8, 'tier2': 0.7, 'tier3': 0.6}
            })
            entry.router.execute = Mock(return_value=Mock(success=True, result={}))
            entry.agent_executor.execute_routing_decision = Mock(return_value=Mock(
                success=True,
                message="Completed",
                duration_ms=100
            ))
            entry.formatter.format = Mock(return_value="Formatted response")
            
            # Process request - should not raise exception
            response = entry.process("implement feature", resume_session=False)
            
            # Verify request was not blocked despite error
            assert response is not None
            assert "Formatted response" in response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
