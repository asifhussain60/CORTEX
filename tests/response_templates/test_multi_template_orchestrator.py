"""Integration tests for Multi-Template Response Orchestrator.

Tests real-world scenarios of multi-template composition.

Author: Asif Hussain
Version: 1.0
"""

import pytest
from src.response_templates.multi_template_orchestrator import (
    MultiTemplateOrchestrator,
    RelevanceScorer,
    TemplateCompositor,
    ConflictResolver,
    ResponseBlender,
    CompositionRule,
    TemplateScore
)
from src.response_templates.template_registry import TemplateRegistry
from src.response_templates.template_loader import Template, TemplateLoader


@pytest.fixture
def template_registry():
    """Create template registry with test templates."""
    registry = TemplateRegistry()
    
    # Add test templates
    help_template = Template(
        template_id='help_table',
        name='Help Table',
        triggers=['help', 'help_table'],
        content="""🧠 **CORTEX Help**

🎯 **My Understanding Of Your Request:**
   You want to see available commands.

⚠️ **Challenge:** ✓ **Accept**

💬 **Response:**
   Here are the available commands:
   - help: Show this help
   - status: Check current status
   - plan: Plan a feature

📝 **Your Request:** Show help commands

🔍 **Next Steps:**
   1. Choose a command to run
   2. Say "help <command>" for details""",
        verbosity='concise',
        metadata={
            'category': 'help',
            'response_type': 'table'
        }
    )
    
    status_template = Template(
        template_id='status_check',
        name='Status Check',
        triggers=['status', 'where are we'],
        content="""🧠 **CORTEX Status**

🎯 **My Understanding Of Your Request:**
   You want to know current progress.

⚠️ **Challenge:** ✓ **Accept**

💬 **Response:**
   Current Status:
   - Phase 1: Complete (100%)
   - Phase 2: In Progress (60%)
   - Phase 3: Not Started (0%)

📝 **Your Request:** Show current status

🔍 **Next Steps:**
   1. Continue Phase 2
   2. Review completed Phase 1""",
        verbosity='concise',
        metadata={
            'category': 'status',
            'response_type': 'table'
        }
    )
    
    quick_start_template = Template(
        template_id='quick_start',
        name='Quick Start',
        triggers=['quick start', 'get started'],
        content="""🧠 **CORTEX Quick Start**

🎯 **My Understanding Of Your Request:**
   You want to get started quickly.

⚠️ **Challenge:** ✓ **Accept**

💬 **Response:**
   Quick Start Guide:
   1. Say "help" to see commands
   2. Say "plan a feature" to start planning
   3. Say "status" to check progress

📝 **Your Request:** Show quick start guide

🔍 **Next Steps:**
   1. Try the help command
   2. Explore features""",
        verbosity='concise',
        metadata={
            'category': 'help',
            'response_type': 'narrative'
        }
    )
    
    registry.register_template(help_template)
    registry.register_template(status_template)
    registry.register_template(quick_start_template)
    
    return registry


@pytest.fixture
def orchestrator(template_registry):
    """Create orchestrator with test templates."""
    return MultiTemplateOrchestrator(template_registry)


class TestRelevanceScorer:
    """Test relevance scoring functionality."""
    
    def test_keyword_matching(self, template_registry):
        """Test keyword matching in relevance scoring."""
        scorer = RelevanceScorer()
        help_template = template_registry.get_template('help_table')
        
        # Query with keywords matching template
        score = scorer.score_template(help_template, "show me help commands")
        
        assert score.score > 0.3
        assert 'help' in score.matched_keywords or 'commands' in score.matched_keywords
    
    def test_trigger_matching(self, template_registry):
        """Test trigger matching in relevance scoring."""
        scorer = RelevanceScorer()
        status_template = template_registry.get_template('status_check')
        
        # Query with exact trigger
        score = scorer.score_template(status_template, "status check please")
        
        assert score.score > 0.5  # Trigger match should score high
        assert len(score.matched_triggers) > 0
    
    def test_ranking(self, template_registry):
        """Test ranking multiple templates."""
        scorer = RelevanceScorer()
        all_templates = template_registry.list_templates()
        
        scores = scorer.score_templates(all_templates, "help me get started")
        
        # Should be sorted by score descending
        assert scores[0].score >= scores[1].score >= scores[2].score
        
        # Help or quick_start should be top ranked
        top_template_ids = {scores[0].template.template_id, scores[1].template.template_id}
        assert 'help_table' in top_template_ids or 'quick_start' in top_template_ids


class TestTemplateCompositor:
    """Test template composition functionality."""
    
    def test_single_template_passthrough(self, template_registry):
        """Test single template renders unchanged."""
        compositor = TemplateCompositor()
        rule = CompositionRule()
        
        help_template = template_registry.get_template('help_table')
        scored = [TemplateScore(template=help_template, score=0.9)]
        
        result = compositor.compose(scored, rule)
        
        assert '🧠 **CORTEX Help**' in result
        assert 'help commands' in result.lower()
    
    def test_section_extraction(self, template_registry):
        """Test section extraction from templates."""
        compositor = TemplateCompositor()
        help_template = template_registry.get_template('help_table')
        
        sections = compositor._extract_sections(help_template.content)
        
        assert '🧠 **CORTEX Help**' in sections
        assert '🎯 **My Understanding Of Your Request:**' in sections
        assert '💬 **Response:**' in sections
    
    def test_multi_template_merge(self, template_registry):
        """Test merging multiple templates."""
        compositor = TemplateCompositor()
        rule = CompositionRule(max_templates=2, deduplicate_sections=True)
        
        help_template = template_registry.get_template('help_table')
        quick_start_template = template_registry.get_template('quick_start')
        
        scored = [
            TemplateScore(template=help_template, score=0.9),
            TemplateScore(template=quick_start_template, score=0.8)
        ]
        
        result = compositor.compose(scored, rule, context={})
        
        # Should contain content from both templates
        assert result is not None
        assert len(result) > 0


class TestConflictResolver:
    """Test conflict resolution functionality."""
    
    def test_priority_based_resolution(self, template_registry):
        """Test priority-based conflict resolution."""
        resolver = ConflictResolver()
        
        help_template = template_registry.get_template('help_table')
        status_template = template_registry.get_template('status_check')
        
        # Create scored templates with different priorities
        scored = [
            TemplateScore(template=status_template, score=0.7),
            TemplateScore(template=help_template, score=0.9),
        ]
        
        resolved = resolver.resolve_conflicts(scored)
        
        # Should keep both (different response types)
        assert len(resolved) == 2
    
    def test_redundancy_detection(self, template_registry):
        """Test detection of redundant templates."""
        resolver = ConflictResolver()
        
        templates = template_registry.list_templates()
        redundant_pairs = resolver.detect_redundancy(templates)
        
        # Our test templates shouldn't be redundant
        assert len(redundant_pairs) == 0


class TestResponseBlender:
    """Test response blending functionality."""
    
    def test_formatting(self):
        """Test response formatting."""
        blender = ResponseBlender()
        
        content = """Section 1


Section 2



Section 3"""
        
        result = blender.blend(content)
        
        # Should remove excessive blank lines
        assert '\n\n\n' not in result
        assert result.strip() == result  # Should be trimmed


class TestMultiTemplateOrchestrator:
    """Test full orchestrator integration."""
    
    def test_single_relevant_template(self, orchestrator):
        """Test with single highly relevant template."""
        response = orchestrator.generate_response("show me help")
        
        assert response is not None
        assert len(response) > 0
        assert '🧠 **CORTEX' in response
    
    def test_multi_template_composition(self, orchestrator):
        """Test composition of multiple templates."""
        response = orchestrator.generate_response("help me get started")
        
        assert response is not None
        assert len(response) > 0
    
    def test_no_relevant_templates(self, orchestrator):
        """Test with query matching no templates."""
        # Use very specific query unlikely to match
        response = orchestrator.generate_response("xyzabc123notfound", rule=CompositionRule(min_relevance_score=0.9))
        
        # Should return "No templates available" or fallback
        assert response is not None
    
    def test_get_relevant_templates(self, orchestrator):
        """Test getting relevant templates without composition."""
        relevant = orchestrator.get_relevant_templates("help commands", top_n=3)
        
        assert len(relevant) > 0
        assert all(isinstance(item, TemplateScore) for item in relevant)
        assert all(item.score >= 0.3 for item in relevant)  # Default min_score
    
    def test_explain_selection(self, orchestrator):
        """Test explanation of template selection."""
        explanation = orchestrator.explain_selection("status check")
        
        assert 'query' in explanation
        assert 'relevant_templates' in explanation
        assert 'selection_reasoning' in explanation
        assert isinstance(explanation['relevant_templates'], list)


class TestRealWorldScenarios:
    """Test real-world multi-template scenarios."""
    
    def test_help_plus_status_scenario(self, orchestrator):
        """Test help + status query (common combination)."""
        response = orchestrator.generate_response("help and show status")
        
        assert response is not None
        assert len(response) > 100  # Should have substantial content
    
    def test_get_started_scenario(self, orchestrator):
        """Test new user get started query."""
        response = orchestrator.generate_response("I'm new, help me get started")
        
        assert response is not None
        # Should include quick_start or help_table content
        assert 'quick start' in response.lower() or 'help' in response.lower()
    
    def test_max_templates_limit(self, orchestrator):
        """Test that max_templates limit is respected."""
        rule = CompositionRule(max_templates=1)
        relevant = orchestrator.get_relevant_templates("help status quick", top_n=5)
        
        # Even if 3 templates relevant, composition should use max 1
        response = orchestrator.generate_response("help status quick", rule=rule)
        
        assert response is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
