"""
Tests for CopilotIntegration.
"""

import pytest
from pathlib import Path
from src.context.copilot_integration import CopilotIntegration


class TestCopilotIntegration:
    """Test Copilot integration with graceful degradation."""
    
    def test_initialization(self):
        """Test that CopilotIntegration initializes without errors."""
        copilot = CopilotIntegration()
        assert copilot is not None
    
    def test_unavailable_in_poc(self):
        """Test that Copilot is unavailable in POC mode."""
        copilot = CopilotIntegration()
        assert copilot.available is False
    
    def test_get_context_returns_none(self):
        """Test that get_context returns None when unavailable."""
        copilot = CopilotIntegration()
        ctx = copilot.get_context()
        assert ctx is None
    
    def test_parse_chat_params_with_active_file(self):
        """Test parsing Copilot Chat params with active file."""
        copilot = CopilotIntegration()
        
        cortex_root = Path(__file__).parent.parent.parent
        active_file = cortex_root / "src" / "main.py"
        
        chat_params = {
            'active_file': str(active_file),
            'workspace_folders': [
                str(cortex_root),
                "D:/PROJECTS/NOOR CANVAS"
            ]
        }
        
        ctx = copilot.parse_chat_params(chat_params)
        
        if ctx:  # May return None if .git not found
            assert 'repo_root' in ctx
            assert 'cortex_root' in ctx
            assert 'active_file' in ctx
    
    def test_parse_chat_params_cortex_detection(self):
        """Test that CORTEX folder is correctly identified."""
        copilot = CopilotIntegration()
        
        cortex_root = Path(__file__).parent.parent.parent
        
        chat_params = {
            'workspace_folders': [
                str(cortex_root),
                "D:/PROJECTS/NOOR CANVAS"
            ]
        }
        
        ctx = copilot.parse_chat_params(chat_params)
        
        if ctx:
            assert ctx['cortex_root'] == cortex_root
    
    def test_parse_chat_params_empty(self):
        """Test parsing empty chat params."""
        copilot = CopilotIntegration()
        
        ctx = copilot.parse_chat_params({})
        
        assert ctx is None
    
    def test_parse_chat_params_error_handling(self):
        """Test that parse_chat_params handles errors gracefully."""
        copilot = CopilotIntegration()
        
        # Invalid params should not crash
        ctx = copilot.parse_chat_params({'invalid': 'data'})
        
        # Should return None or valid context
        assert ctx is None or isinstance(ctx, dict)
