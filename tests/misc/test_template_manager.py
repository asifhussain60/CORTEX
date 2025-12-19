"""
Tests for Template Manager (CORTEX 4.0)

Integration tests for complete response template system v4.0.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.core.template_manager import TemplateManager, ResponseMetadata
from src.core.response_tier_selector import ResponseTier


class TestTemplateManager:
    """Test suite for TemplateManager."""
    
    @pytest.fixture
    def manager(self):
        """Fixture for template manager."""
        templates_path = Path("cortex-brain/response-templates-v4.yaml")
        return TemplateManager(str(templates_path))
    
    # ============================================================================
    # Initialization Tests
    # ============================================================================
    
    def test_initialization(self, manager):
        """Test template manager initializes successfully."""
        assert manager is not None
        assert manager.tier_selector is not None
        assert manager.section_selector is not None
    
    def test_config_loaded(self, manager):
        """Test configuration loaded from YAML."""
        assert manager.config is not None
        assert "schema_version" in manager.config
    
    def test_validate_config(self, manager):
        """Test configuration validation."""
        is_valid = manager.validate_config()
        assert is_valid is True
    
    # ============================================================================
    # TIER 1 (INSTANT) Rendering Tests
    # ============================================================================
    
    def test_render_tier1_direct(self, manager):
        """Test TIER1 renders direct answer without formatting."""
        request = "what's 5 + 5?"
        content = {"response": "10"}
        
        response = manager.render(request, content)
        assert response == "10"
        assert "##" not in response  # No headers
        assert "Author:" not in response  # No branding
    
    # ============================================================================
    # TIER 2 (FOCUSED) Rendering Tests
    # ============================================================================
    
    def test_render_tier2_minimal(self, manager):
        """Test TIER2 renders with minimal structure."""
        request = "explain lazy loading"
        content = {
            "response": "Lazy loading defers initialization until first access."
        }
        
        response = manager.render(request, content)
        assert "## 🧠 CORTEX" in response
        assert "Author:" in response
        assert "💬" in response  # Response section emoji
    
    def test_render_tier2_with_actions(self, manager):
        """Test TIER2 with actions section."""
        request = "explain X"
        content = {
            "response": "X is a concept.",
            "actions": "Use X in your code."
        }
        context = {"user_action_required": True}
        
        response = manager.render(request, content, context)
        assert "🔍" in response  # Actions section emoji
    
    # ============================================================================
    # TIER 3 (STRUCTURED) Rendering Tests
    # ============================================================================
    
    def test_render_tier3_5_part(self, manager):
        """Test TIER3 renders complete 5-part structure."""
        request = "implement feature X"
        content = {
            "understanding": "Implementing feature X with validation",
            "approach": "No significant challenges",
            "response": "Feature implemented successfully",
            "changes": "Created src/feature_x.py (150 LOC)",
            "next_steps": "1. Test in staging\n2. Deploy"
        }
        context = {
            "has_technical_challenge": False,
            "files_modified": True,
            "user_action_required": True
        }
        
        response = manager.render(request, content, context)
        
        # Check all 5 parts present
        assert "🎯" in response  # Understanding
        assert "💬" in response  # Response
        assert "📊" in response  # Changes
        assert "🔍" in response  # Next steps
        assert "---" in response  # Separator
    
    def test_render_tier3_with_separator(self, manager):
        """Test TIER3 includes separator after header."""
        request = "implement X"
        content = {"understanding": "Test", "response": "Done"}
        
        response = manager.render(request, content)
        lines = response.split("\n")
        
        # Find separator
        separator_found = False
        for line in lines:
            if line.strip() == "---":
                separator_found = True
                break
        
        assert separator_found is True
    
    # ============================================================================
    # TIER 4 (COMPREHENSIVE) Rendering Tests
    # ============================================================================
    
    def test_render_tier4_comprehensive(self, manager):
        """Test TIER4 renders comprehensive structure."""
        request = "system maintenance workflow"
        content = {
            "understanding": "Running system maintenance",
            "approach": "7-phase workflow",
            "response": "Maintenance completed",
            "changes": "All systems operational",
            "next_steps": "Monitor for 24 hours"
        }
        context = {"multi_phase": True}
        
        response = manager.render(request, content, context)
        
        # Should have all 5 parts
        assert "🎯" in response
        assert "⚡" in response
        assert "💬" in response
        assert "📊" in response
        assert "🔍" in response
    
    def test_render_tier4_with_architecture(self, manager):
        """Test TIER4 includes architecture section."""
        request = "design system X"
        content = {
            "understanding": "Designing system X",
            "architecture": "4-tier architecture",
            "approach": "Microservices pattern",
            "response": "Design complete",
            "changes": "Created design docs",
            "next_steps": "Begin implementation"
        }
        context = {"system_design": True, "multi_phase": True}
        
        response = manager.render(request, content, context)
        assert "🏗️" in response  # Architecture emoji
    
    # ============================================================================
    # Success Template Tests
    # ============================================================================
    
    def test_render_success(self, manager):
        """Test success completion template."""
        operation = "Phase 1 Day 2"
        content = {
            "understanding": "Validated brain tiers",
            "response": "All 22 tests passing",
            "changes": "Brain tiers operational"
        }
        
        response = manager.render_success(operation, content)
        
        assert "# 🎉 CONGRATULATIONS" in response
        assert "## 🧠 CORTEX Phase 1 Day 2" in response
        assert "No Challenge - All work completed successfully" in response
        assert "✅ **Work Complete!**" in response
    
    def test_render_success_with_next_actions(self, manager):
        """Test success template with optional next actions."""
        content = {
            "understanding": "Test",
            "response": "Done",
            "changes": "Changes made",
            "next_actions": "Optional: Review documentation"
        }
        
        response = manager.render_success("Operation", content)
        assert "Optional: Review documentation" in response
    
    # ============================================================================
    # Error Template Tests
    # ============================================================================
    
    def test_render_error(self, manager):
        """Test error template rendering."""
        error = "File not found: config.json"
        solutions = [
            "Check file path",
            "Verify file exists",
            "Check permissions"
        ]
        
        response = manager.render_error(error, solutions)
        
        assert "## 🧠 CORTEX Error" in response
        assert "⚠️ Error" in response
        assert error in response
        assert "🔍 Possible Solutions" in response
        assert all(sol in response for sol in solutions)
    
    def test_render_error_without_solutions(self, manager):
        """Test error template without solutions."""
        error = "Unknown error occurred"
        
        response = manager.render_error(error)
        
        assert "⚠️ Error" in response
        assert error in response
        assert "Possible Solutions" not in response
    
    # ============================================================================
    # Metadata Tests
    # ============================================================================
    
    def test_get_metadata_tier1(self, manager):
        """Test metadata for TIER1 request."""
        request = "what's 5 + 5?"
        
        metadata = manager.get_metadata(request)
        
        assert metadata.tier == ResponseTier.TIER1_INSTANT
        assert len(metadata.sections) == 0
        assert metadata.estimated_tokens < 50
        assert metadata.has_header is False
    
    def test_get_metadata_tier3(self, manager):
        """Test metadata for TIER3 request."""
        request = "implement feature X"
        context = {"files_modified": True, "user_action_required": True}
        
        metadata = manager.get_metadata(request, context)
        
        assert metadata.tier in [ResponseTier.TIER3_STRUCTURED, ResponseTier.TIER4_COMPREHENSIVE]
        assert len(metadata.sections) >= 2
        assert metadata.has_header is True
        assert metadata.has_branding is True
    
    # ============================================================================
    # Title Extraction Tests
    # ============================================================================
    
    def test_extract_title_simple(self, manager):
        """Test title extraction from simple request."""
        title = manager._extract_title("implement feature X")
        assert title == "Implement feature X"
    
    def test_extract_title_question(self, manager):
        """Test title extraction removes question mark."""
        title = manager._extract_title("what is lazy loading?")
        assert title == "What is lazy loading"
        assert "?" not in title
    
    def test_extract_title_long(self, manager):
        """Test title extraction truncates long requests."""
        long_request = "a" * 100
        title = manager._extract_title(long_request)
        assert len(title) <= 60
        assert title.endswith("...")
    
    # ============================================================================
    # Integration Tests
    # ============================================================================
    
    def test_end_to_end_tier3(self, manager):
        """Test complete end-to-end TIER3 rendering."""
        request = "analyze test results"
        content = {
            "understanding": "Analyzing 47 test results",
            "approach": "No significant challenges",
            "response": "All tests passing",
            "changes": "0 failures, 47 passing",
            "next_steps": "Continue to next phase"
        }
        context = {
            "has_technical_challenge": False,
            "files_modified": True,
            "user_action_required": True
        }
        
        response = manager.render(request, content, context)
        
        # Validate structure
        assert response.startswith("## 🧠 CORTEX")
        assert "Author:" in response
        assert "github.com/asifhussain60/CORTEX" in response
        assert "---" in response
        
        # Validate core content present (not all sections may render if context doesn't require them)
        assert content["understanding"] in response
        assert content["response"] in response
        assert content["changes"] in response
        assert content["next_steps"] in response
        # Approach may or may not be included depending on has_technical_challenge flag
    
    def test_token_estimation_accuracy(self, manager):
        """Test token estimation is reasonable."""
        requests = [
            ("what's 5+5?", 10, 50),  # TIER1: 10-50 tokens
            ("explain X", 80, 200),  # TIER2: 80-200 tokens
            ("implement X", 200, 400),  # TIER3: 200-400 tokens
            ("system maintenance", 400, 800)  # TIER4: 400-800 tokens
        ]
        
        for request, min_tokens, max_tokens in requests:
            metadata = manager.get_metadata(request)
            assert min_tokens <= metadata.estimated_tokens <= max_tokens, \
                f"Request '{request}' estimated {metadata.estimated_tokens} tokens"
