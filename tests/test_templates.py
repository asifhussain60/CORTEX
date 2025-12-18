"""
Tests for Response Templates v4.0

Test coverage:
- TemplateManager initialization and config loading
- Tier selection logic (TIER 1-4)
- Section selection based on tier and context
- Template rendering output format
- Success template generation
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.templates import (
    TemplateManager,
    ResponseTier,
    TemplateContext,
    TierSelector,
    SectionSelector,
    TemplateRenderer,
    get_template_manager
)


class TestTemplateManager:
    """Test suite for TemplateManager"""
    
    def test_template_manager_initialization(self, mock_config):
        """Test that TemplateManager initializes correctly"""
        with patch('src.templates.template_manager.get_config_manager', return_value=mock_config):
            with patch('src.templates.template_manager.setup_logger'):
                with patch('builtins.open', create=True):
                    with patch('src.templates.template_manager.yaml.safe_load', return_value={'schema_version': '4.0'}):
                        manager = TemplateManager()
                        
                        assert manager is not None
                        assert isinstance(manager.tier_selector, TierSelector)
                        assert isinstance(manager.section_selector, SectionSelector)
                        assert isinstance(manager.renderer, TemplateRenderer)
    
    def test_template_manager_singleton(self):
        """Test that get_template_manager returns singleton"""
        with patch('src.templates.template_manager.get_config_manager'):
            with patch('src.templates.template_manager.setup_logger'):
                with patch('builtins.open', create=True):
                    with patch('src.templates.template_manager.yaml.safe_load', return_value={'schema_version': '4.0'}):
                        manager1 = get_template_manager()
                        manager2 = get_template_manager()
                        
                        assert manager1 is manager2
    
    def test_generate_response_tier1_instant(self, mock_config):
        """Test generating TIER 1 (INSTANT) response"""
        with patch('src.templates.template_manager.get_config_manager', return_value=mock_config):
            with patch('src.templates.template_manager.setup_logger'):
                with patch('builtins.open', create=True):
                    with patch('src.templates.template_manager.yaml.safe_load', return_value={'schema_version': '4.0', 'routing': {}}):
                        manager = TemplateManager()
                        
                        context = TemplateContext(
                            operation="Answer",
                            request="What's the square root of 144?",
                            is_factual_query=True,
                            estimated_tokens=5
                        )
                        
                        content = {
                            "response": "12"
                        }
                        
                        response = manager.generate_response(context, content)
                        
                        assert response == "12"
                        assert "##" not in response  # No headers for TIER 1
    
    def test_generate_response_tier3_structured(self, mock_config):
        """Test generating TIER 3 (STRUCTURED) response"""
        with patch('src.templates.template_manager.get_config_manager', return_value=mock_config):
            with patch('src.templates.template_manager.setup_logger'):
                with patch('builtins.open', create=True):
                    with patch('src.templates.template_manager.yaml.safe_load', return_value={'schema_version': '4.0', 'routing': {}, 'section_emojis': {}}):
                        manager = TemplateManager()
                        
                        context = TemplateContext(
                            operation="Implementation",
                            request="Implement user authentication",
                            requires_multiple_aspects=True,
                            has_modifications=True,
                            estimated_tokens=400
                        )
                        
                        content = {
                            "understanding_scope": "Implement secure user authentication",
                            "approach_considerations": "Use JWT tokens with refresh mechanism",
                            "response": "Implementation complete",
                            "impact_changes": "3 files modified",
                            "next_steps": "1. Test authentication flow\n2. Deploy to staging"
                        }
                        
                        response = manager.generate_response(context, content)
                        
                        assert "## 🧠 CORTEX Implementation" in response
                        assert "### 🎯 Understanding & Scope" in response
                        assert "### ⚡ Approach & Considerations" in response
                        assert "### 💬 Response" in response
                        assert "### 📊 Impact & Changes" in response
                        assert "### 🔍 Next Steps" in response
    
    def test_generate_success_response(self, mock_config):
        """Test generating success/completion response"""
        with patch('src.templates.template_manager.get_config_manager', return_value=mock_config):
            with patch('src.templates.template_manager.setup_logger'):
                with patch('builtins.open', create=True):
                    with patch('src.templates.template_manager.yaml.safe_load', return_value={'schema_version': '4.0', 'routing': {}, 'section_emojis': {}}):
                        manager = TemplateManager()
                        
                        response = manager.generate_success_response(
                            operation="System Maintenance",
                            completion_summary="All 7 phases completed successfully",
                            changes="10 files modified, 5 tests passing",
                            optional_next_actions=""
                        )
                        
                        assert "# 🎉 CONGRATULATIONS" in response
                        assert "## 🧠 CORTEX System Maintenance" in response
                        assert "No Challenge - All work completed successfully" in response
                        assert "✅ **Work Complete!**" in response


class TestTierSelector:
    """Test suite for TierSelector"""
    
    def test_tier_selection_instant(self):
        """Test TIER 1 (INSTANT) selection logic"""
        config = {
            "routing": {
                "tier1_instant": {
                    "triggers": {
                        "question_words": ["what", "where", "when"],
                        "factual_lookup": True,
                        "estimated_tokens": "< 50"
                    }
                }
            }
        }
        
        selector = TierSelector(config)
        
        context = TemplateContext(
            operation="Query",
            request="What's the command for planning?",
            is_factual_query=True,
            estimated_tokens=10,
            requires_explanation=False
        )
        
        tier = selector.select_tier(context)
        
        assert tier == ResponseTier.INSTANT
    
    def test_tier_selection_focused(self):
        """Test TIER 2 (FOCUSED) selection logic"""
        config = {
            "routing": {
                "tier2_focused": {
                    "triggers": {
                        "single_concept": True,
                        "estimated_tokens": [50, 200]
                    }
                }
            }
        }
        
        selector = TierSelector(config)
        
        context = TemplateContext(
            operation="Explanation",
            request="Explain lazy loading",
            is_single_concept=True,
            estimated_tokens=120
        )
        
        tier = selector.select_tier(context)
        
        assert tier == ResponseTier.FOCUSED
    
    def test_tier_selection_structured(self):
        """Test TIER 3 (STRUCTURED) selection logic"""
        config = {
            "routing": {
                "tier3_structured": {
                    "triggers": {
                        "multi_faceted": True,
                        "estimated_tokens": [200, 600]
                    }
                }
            }
        }
        
        selector = TierSelector(config)
        
        context = TemplateContext(
            operation="Implementation",
            request="Implement feature X",
            requires_multiple_aspects=True,
            has_modifications=True,
            estimated_tokens=400
        )
        
        tier = selector.select_tier(context)
        
        assert tier == ResponseTier.STRUCTURED
    
    def test_tier_selection_comprehensive_default(self):
        """Test TIER 4 (COMPREHENSIVE) as default"""
        config = {"routing": {}}
        
        selector = TierSelector(config)
        
        context = TemplateContext(
            operation="Complex Operation",
            request="Perform system maintenance with TDD",
            estimated_tokens=800
        )
        
        tier = selector.select_tier(context)
        
        assert tier == ResponseTier.COMPREHENSIVE


class TestSectionSelector:
    """Test suite for SectionSelector"""
    
    def test_section_selection_tier1_instant(self):
        """Test that TIER 1 has no sections"""
        config = {"section_library": []}
        selector = SectionSelector(config)
        
        context = TemplateContext(operation="Query", request="test")
        sections = selector.select_sections(ResponseTier.INSTANT, context)
        
        assert sections == []
    
    def test_section_selection_tier2_focused(self):
        """Test TIER 2 section selection (1-2 sections)"""
        config = {"section_library": []}
        selector = SectionSelector(config)
        
        context = TemplateContext(
            operation="Explanation",
            request="test",
            has_modifications=True
        )
        sections = selector.select_sections(ResponseTier.FOCUSED, context)
        
        assert len(sections) <= 2
        assert "response" in sections
        assert "next_steps" in sections
    
    def test_section_selection_tier3_structured(self):
        """Test TIER 3 section selection (2-5 sections)"""
        config = {"section_library": []}
        selector = SectionSelector(config)
        
        context = TemplateContext(
            operation="Implementation",
            request="test",
            has_modifications=True
        )
        sections = selector.select_sections(ResponseTier.STRUCTURED, context)
        
        assert 2 <= len(sections) <= 5  # Core (3) + impact (1) + next_steps (1) = 5 max
        assert "understanding_scope" in sections
        assert "approach_considerations" in sections
        assert "response" in sections
        assert "next_steps" in sections
    
    def test_section_selection_tier4_comprehensive(self):
        """Test TIER 4 section selection (4-7 sections)"""
        config = {"section_library": []}
        selector = SectionSelector(config)
        
        context = TemplateContext(
            operation="Complex Operation",
            request="test",
            has_modifications=True,
            has_architecture=True,
            has_technical_depth=True
        )
        sections = selector.select_sections(ResponseTier.COMPREHENSIVE, context)
        
        assert 4 <= len(sections) <= 7  # Core (3) + impact (1) + arch (1) + tech (1) + next (1) = 7 max
        assert "understanding_scope" in sections
        assert "approach_considerations" in sections
        assert "response" in sections
        assert "architecture" in sections
        assert "technical_details" in sections
        assert "next_steps" in sections


class TestTemplateRenderer:
    """Test suite for TemplateRenderer"""
    
    def test_render_tier1_instant(self):
        """Test TIER 1 rendering (direct answer only)"""
        config = {"section_emojis": {}, "components": {}}
        renderer = TemplateRenderer(config)
        
        context = TemplateContext(operation="Answer", request="test")
        content = {"response": "12"}
        
        result = renderer.render(ResponseTier.INSTANT, [], content, context)
        
        assert result == "12"
        assert "##" not in result
    
    def test_render_tier3_structured(self):
        """Test TIER 3 rendering with sections"""
        config = {
            "section_emojis": {
                "understanding": "🎯",
                "approach": "⚡",
                "response": "💬",
                "next": "🔍"
            },
            "components": {}
        }
        renderer = TemplateRenderer(config)
        
        context = TemplateContext(operation="Implementation", request="test")
        sections = ["understanding_scope", "approach_considerations", "response", "next_steps"]
        content = {
            "understanding_scope": "Test understanding",
            "approach_considerations": "Test approach",
            "response": "Test response",
            "next_steps": "1. Test\n2. Deploy"
        }
        
        result = renderer.render(ResponseTier.STRUCTURED, sections, content, context)
        
        assert "## 🧠 CORTEX Implementation" in result
        assert "---" in result
        assert "### 🎯 Understanding & Scope" in result
        assert "### ⚡ Approach & Considerations" in result
        assert "### 💬 Response" in result
        assert "### 🔍 Next Steps" in result
    
    def test_render_success_template(self):
        """Test success template rendering"""
        config = {
            "section_emojis": {
                "understanding": "🎯",
                "approach": "⚡",
                "response": "💬",
                "impact": "📊",
                "next": "🔍"
            },
            "components": {}
        }
        renderer = TemplateRenderer(config)
        
        context = TemplateContext(
            operation="System Maintenance",
            request="test",
            all_work_complete=True,
            no_errors=True,
            no_user_action_required=True
        )
        content = {
            "understanding_scope": "Completed maintenance",
            "approach_considerations": "No Challenge - All work completed successfully",
            "response": "All phases complete",
            "impact_changes": "10 files modified",
            "next_steps": "✅ **Work Complete!** No further action required."
        }
        
        result = renderer.render_success(content, context)
        
        assert "# 🎉 CONGRATULATIONS" in result
        assert "## 🧠 CORTEX System Maintenance" in result
        assert "No Challenge - All work completed successfully" in result
        assert "✅ **Work Complete!**" in result
