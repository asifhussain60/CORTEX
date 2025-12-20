"""
Test FeedbackAgent integration with FeedbackCollector and Gist upload

Validates that feedback commands properly trigger Gist upload.
"""

import sys
import pytest
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestFeedbackAgentGistIntegration:
    """Validate FeedbackAgent properly wires to FeedbackCollector and Gist upload"""
    
    def test_feedback_agent_has_auto_upload_parameter(self):
        """FeedbackAgent.create_feedback_report accepts auto_upload parameter"""
        from agents.feedback_agent import FeedbackAgent
        import inspect
        
        agent = FeedbackAgent()
        sig = inspect.signature(agent.create_feedback_report)
        params = sig.parameters
        
        assert 'auto_upload' in params, "create_feedback_report missing auto_upload parameter"
        assert params['auto_upload'].default == True, "auto_upload should default to True"
    
    def test_feedback_agent_imports_feedback_collector(self):
        """FeedbackAgent can import FeedbackCollector"""
        from agents.feedback_agent import FeedbackAgent
        
        agent = FeedbackAgent()
        
        # Create feedback with auto_upload disabled (to avoid requiring token)
        result = agent.create_feedback_report(
            user_input="Test feedback",
            feedback_type="bug",
            severity="medium",
            auto_upload=False
        )
        
        assert result['success'] == True
        assert 'file_path' in result
        assert result['feedback_type'] == 'bug'
    
    def test_feedback_agent_returns_gist_url_field(self):
        """FeedbackAgent result includes gist_url field"""
        from agents.feedback_agent import FeedbackAgent
        
        agent = FeedbackAgent()
        
        result = agent.create_feedback_report(
            user_input="Test feedback",
            auto_upload=False  # Disable upload for test
        )
        
        assert 'gist_url' in result, "Result should include gist_url field"
    
    def test_feedback_agent_graceful_upload_failure(self):
        """FeedbackAgent handles upload failures gracefully"""
        from agents.feedback_agent import FeedbackAgent
        
        agent = FeedbackAgent()
        
        # This will attempt upload but fail (no token configured)
        # Should not raise exception
        result = agent.create_feedback_report(
            user_input="Test feedback for upload failure",
            feedback_type="bug",
            auto_upload=True  # Enable upload (will fail gracefully)
        )
        
        # Should still succeed (file saved locally)
        assert result['success'] == True
        assert 'file_path' in result
        # gist_url will be None if upload failed
        assert result.get('gist_url') is None or isinstance(result.get('gist_url'), str)


class TestDocumentationComplete:
    """Validate feedback documentation is complete and accurate"""
    
    def test_cortex_prompt_documents_gist_upload(self):
        """CORTEX.prompt.md documents automatic Gist upload"""
        prompt_path = Path(__file__).parent.parent / '.github' / 'prompts' / 'CORTEX.prompt.md'
        content = prompt_path.read_text(encoding='utf-8')
        
        # Check for Gist upload documentation
        assert 'Auto-Upload' in content or 'Gist' in content, "Documentation missing Gist upload info"
        assert 'github' in content.lower(), "Documentation missing GitHub config info"
        assert 'token' in content.lower(), "Documentation missing token setup info"
        assert 'consent' in content.lower(), "Documentation missing consent info"
    
    def test_cortex_prompt_documents_setup(self):
        """CORTEX.prompt.md documents GitHub token setup"""
        prompt_path = Path(__file__).parent.parent / '.github' / 'prompts' / 'CORTEX.prompt.md'
        content = prompt_path.read_text(encoding='utf-8')
        
        # Check for setup instructions
        assert 'Setup' in content or 'setup' in content, "Documentation missing setup section"
        assert 'cortex.config.json' in content, "Documentation missing config file reference"
        assert 'Personal access token' in content or 'personal access token' in content, "Documentation missing token generation instructions"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
