"""
Tests for Post-Installation Handler

Tests user choice detection and routing to demo/onboarding orchestrators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.setup.post_installation_handler import (
    PostInstallationHandler,
    handle_post_installation_choice
)


class TestPostInstallationHandler:
    """Test post-installation handler functionality"""
    
    @pytest.fixture
    def sample_context(self):
        """Sample setup context"""
        return {
            'project_root': Path('/path/to/cortex'),
            'user_project_root': Path('/path/to/user/repo'),
            'brain_initialized': True,
            'setup_complete': True,
            'awaiting_user_choice': True
        }
    
    @pytest.fixture
    def handler(self, sample_context):
        """Create handler instance"""
        return PostInstallationHandler(sample_context)
    
    # ========== Choice Detection Tests ==========
    
    def test_detect_demo_choice_explicit(self, handler):
        """Test detecting explicit demo request"""
        assert handler.detect_user_choice("demo") == 'demo'
        assert handler.detect_user_choice("show me a demo") == 'demo'
        assert handler.detect_user_choice("demo cortex") == 'demo'
    
    def test_detect_demo_choice_variations(self, handler):
        """Test detecting demo choice variations"""
        variations = [
            "what can you do",
            "show me features",
            "demonstrate capabilities",
            "give me a tour",
            "see demo"
        ]
        for variation in variations:
            assert handler.detect_user_choice(variation) == 'demo'
    
    def test_detect_analyze_choice_explicit(self, handler):
        """Test detecting explicit analyze request"""
        assert handler.detect_user_choice("analyze") == 'analyze'
        assert handler.detect_user_choice("analyze this repo") == 'analyze'
        assert handler.detect_user_choice("onboard") == 'analyze'
    
    def test_detect_analyze_choice_variations(self, handler):
        """Test detecting analyze choice variations"""
        variations = [
            "analyze repository",
            "scan my code",
            "review this project",
            "inspect the codebase",
            "check repo"
        ]
        for variation in variations:
            assert handler.detect_user_choice(variation) == 'analyze'
    
    def test_detect_skip_choice_explicit(self, handler):
        """Test detecting explicit skip request"""
        assert handler.detect_user_choice("skip") == 'skip'
        assert handler.detect_user_choice("no") == 'skip'
        assert handler.detect_user_choice("later") == 'skip'
    
    def test_detect_skip_choice_variations(self, handler):
        """Test detecting skip choice variations"""
        variations = [
            "start working",
            "get started",
            "jump in",
            "begin",
            "help"
        ]
        for variation in variations:
            assert handler.detect_user_choice(variation) == 'skip'
    
    def test_detect_choice_case_insensitive(self, handler):
        """Test choice detection is case insensitive"""
        assert handler.detect_user_choice("DEMO") == 'demo'
        assert handler.detect_user_choice("Analyze") == 'analyze'
        assert handler.detect_user_choice("SKIP") == 'skip'
    
    def test_detect_choice_default_to_demo(self, handler):
        """Test unclear input defaults to demo"""
        assert handler.detect_user_choice("unknown request") == 'demo'
        assert handler.detect_user_choice("something else") == 'demo'
    
    # ========== Handler Tests ==========
    
    def test_handle_demo_choice(self, handler):
        """Test handling demo choice"""
        result = handler.handle_demo_choice()
        
        assert result['action'] == 'demo'
        assert result['orchestrator'] == 'demo'
        assert result['template_id'] == 'introduction_discovery'
        assert result['context']['post_installation'] == True
        assert result['context']['source'] == 'post_installation_handler'
    
    def test_handle_analyze_choice(self, handler):
        """Test handling analyze choice"""
        result = handler.handle_analyze_choice()
        
        assert result['action'] == 'analyze'
        assert result['orchestrator'] == 'onboarding'
        assert result['module'] == 'onboarding_module'
        assert result['context']['post_installation'] == True
        assert 'user_project_root' in result['context']
        assert 'brain_initialized' in result['context']
    
    def test_handle_skip_choice(self, handler):
        """Test handling skip choice"""
        result = handler.handle_skip_choice()
        
        assert result['action'] == 'skip'
        assert result['template_id'] == 'general_help'
        assert result['context']['post_installation'] == True
        assert 'message' in result['context']
    
    def test_process_user_choice_demo(self, handler):
        """Test processing demo choice end-to-end"""
        result = handler.process_user_choice("show me a demo")
        
        assert result['action'] == 'demo'
        assert result['orchestrator'] == 'demo'
    
    def test_process_user_choice_analyze(self, handler):
        """Test processing analyze choice end-to-end"""
        result = handler.process_user_choice("analyze this repo")
        
        assert result['action'] == 'analyze'
        assert result['orchestrator'] == 'onboarding'
    
    def test_process_user_choice_skip(self, handler):
        """Test processing skip choice end-to-end"""
        result = handler.process_user_choice("skip")
        
        assert result['action'] == 'skip'
        assert result['template_id'] == 'general_help'
    
    # ========== Context Tests ==========
    
    def test_handler_uses_context_paths(self, sample_context):
        """Test handler extracts paths from context"""
        handler = PostInstallationHandler(sample_context)
        
        assert handler.project_root == Path('/path/to/cortex')
        assert handler.user_project_root == Path('/path/to/user/repo')
    
    def test_handler_defaults_user_project_root(self):
        """Test handler defaults user_project_root if missing"""
        context = {
            'project_root': Path('/path/to/cortex')
        }
        handler = PostInstallationHandler(context)
        
        # Should default to parent of project_root
        assert handler.user_project_root == Path('/path/to/cortex').parent
    
    def test_handler_passes_brain_status(self, sample_context):
        """Test handler passes brain_initialized status"""
        handler = PostInstallationHandler(sample_context)
        result = handler.handle_analyze_choice()
        
        assert result['context']['brain_initialized'] == True
    
    # ========== Convenience Function Tests ==========
    
    def test_convenience_function_demo(self, sample_context):
        """Test convenience function for demo"""
        result = handle_post_installation_choice(sample_context, "demo")
        
        assert result['action'] == 'demo'
        assert result['orchestrator'] == 'demo'
    
    def test_convenience_function_analyze(self, sample_context):
        """Test convenience function for analyze"""
        result = handle_post_installation_choice(sample_context, "analyze repo")
        
        assert result['action'] == 'analyze'
        assert result['orchestrator'] == 'onboarding'
    
    def test_convenience_function_skip(self, sample_context):
        """Test convenience function for skip"""
        result = handle_post_installation_choice(sample_context, "skip")
        
        assert result['action'] == 'skip'


class TestPostInstallationIntegration:
    """Integration tests for post-installation workflow"""
    
    def test_demo_choice_includes_required_context(self):
        """Test demo choice includes all required context"""
        context = {
            'project_root': Path('/cortex'),
            'user_project_root': Path('/user/repo'),
            'brain_initialized': True
        }
        
        result = handle_post_installation_choice(context, "demo")
        
        # Check required fields for demo orchestrator
        assert 'post_installation' in result['context']
        assert 'user_request' in result['context']
        assert 'source' in result['context']
    
    def test_analyze_choice_includes_required_context(self):
        """Test analyze choice includes all required context"""
        context = {
            'project_root': Path('/cortex'),
            'user_project_root': Path('/user/repo'),
            'brain_initialized': True
        }
        
        result = handle_post_installation_choice(context, "analyze")
        
        # Check required fields for onboarding module
        assert 'user_project_root' in result['context']
        assert 'project_root' in result['context']
        assert 'brain_initialized' in result['context']
        assert 'post_installation' in result['context']
    
    def test_skip_choice_includes_help_message(self):
        """Test skip choice includes help message"""
        context = {
            'project_root': Path('/cortex')
        }
        
        result = handle_post_installation_choice(context, "skip")
        
        assert 'message' in result['context']
        assert 'help' in result['context']['message'].lower()
