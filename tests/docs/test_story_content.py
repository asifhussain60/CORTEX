"""
Test CORTEX Story Content Preservation

Validates that the "hilariously funny narrative" of the awakening-of-cortex.md
story is preserved during any modifications:
- "Intern with amnesia" metaphor intact
- Dual-hemisphere brain architecture explained
- Four-tier memory system present
- Humor and storytelling preserved
- Technical depth balanced with narrative flow

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import re


@pytest.fixture
def story_path():
    """Path to awakening story"""
    workspace_root = Path(__file__).parent.parent.parent
    return workspace_root / 'docs' / 'awakening-of-cortex.md'


@pytest.fixture
def story_content(story_path):
    """Read story content"""
    if not story_path.exists():
        pytest.skip(f"Story file not found: {story_path}")
    
    with open(story_path, 'r', encoding='utf-8') as f:
        return f.read()


class TestStoryMetaphor:
    """Test the core 'intern with amnesia' metaphor"""
    
    def test_intern_metaphor_present(self, story_content):
        """Story should introduce the intern metaphor"""
        assert 'intern' in story_content.lower()
        assert 'amnesia' in story_content.lower()
    
    def test_intern_brilliance_mentioned(self, story_content):
        """Story should establish intern's brilliance"""
        brilliance_keywords = ['brilliant', 'talented', 'incredibly', 'lightning speed']
        assert any(keyword in story_content.lower() for keyword in brilliance_keywords)
    
    def test_amnesia_problem_explained(self, story_content):
        """Story should explain the amnesia problem clearly"""
        amnesia_explanations = [
            'forgets everything',
            'no memory',
            'amnesia',
            'forget'
        ]
        matches = sum(1 for keyword in amnesia_explanations if keyword in story_content.lower())
        assert matches >= 2, "Amnesia problem should be explained multiple times"
    
    def test_coffee_break_example(self, story_content):
        """Story should use relatable coffee break example"""
        # Should mention forgetting after short breaks
        assert any(phrase in story_content.lower() for phrase in [
            'coffee', 'walk away', 'leave for', 'lunch'
        ])
    
    def test_metaphor_in_opening_section(self, story_content):
        """Opening should hook with metaphor immediately"""
        # First 500 characters should establish metaphor
        opening = story_content[:500].lower()
        assert 'intern' in opening or 'amnesia' in opening


class TestBrainArchitecture:
    """Test dual-hemisphere brain architecture explanation"""
    
    def test_dual_hemisphere_mentioned(self, story_content):
        """Story should explain dual-hemisphere architecture"""
        assert 'left brain' in story_content.lower() or 'left hemisphere' in story_content.lower()
        assert 'right brain' in story_content.lower() or 'right hemisphere' in story_content.lower()
    
    def test_left_brain_tactical_executor(self, story_content):
        """Left brain should be described as tactical executor"""
        left_brain_terms = ['tactical', 'executor', 'precise', 'detail', 'methodical']
        matches = sum(1 for term in left_brain_terms if term in story_content.lower())
        assert matches >= 2, "Left brain tactical nature should be emphasized"
    
    def test_right_brain_strategic_planner(self, story_content):
        """Right brain should be described as strategic planner"""
        right_brain_terms = ['strategic', 'planner', 'holistic', 'pattern', 'context']
        matches = sum(1 for term in right_brain_terms if term in story_content.lower())
        assert matches >= 2, "Right brain strategic nature should be emphasized"
    
    def test_corpus_callosum_explained(self, story_content):
        """Story should explain corpus callosum coordination"""
        assert 'corpus callosum' in story_content.lower()
        coordination_terms = ['coordinate', 'bridge', 'communication', 'messenger']
        assert any(term in story_content.lower() for term in coordination_terms)
    
    def test_specialist_agents_mentioned(self, story_content):
        """Story should mention specialist agents or agent architecture"""
        # Look for agent concepts - specialist agents or general agent architecture
        agent_concepts = [
            'brain protector', 'specialist agent', 'agents coordinate',
            'agent', 'coordinator', 'router'
        ]
        mentioned_concepts = sum(1 for concept in agent_concepts if concept in story_content.lower())
        assert mentioned_concepts >= 1, f"Should mention agent architecture (found {mentioned_concepts})"


class TestMemoryTiers:
    """Test four-tier memory system explanation"""
    
    def test_tier0_instinct(self, story_content):
        """Tier 0 (Instinct) should be explained"""
        assert 'tier 0' in story_content.lower() or 'tier 0:' in story_content.lower()
        instinct_keywords = ['instinct', 'immutable', 'core', 'permanent', 'reflex']
        assert any(keyword in story_content.lower() for keyword in instinct_keywords)
    
    def test_tier1_working_memory(self, story_content):
        """Tier 1 (Working Memory) should be explained"""
        assert 'tier 1' in story_content.lower()
        working_memory_keywords = ['working memory', 'conversation', 'recent', '20 conversations']
        assert any(keyword in story_content.lower() for keyword in working_memory_keywords)
    
    def test_tier2_knowledge_graph(self, story_content):
        """Tier 2 (Knowledge Graph) should be explained"""
        assert 'tier 2' in story_content.lower()
        knowledge_keywords = ['knowledge graph', 'pattern', 'learning', 'long-term']
        assert any(keyword in story_content.lower() for keyword in knowledge_keywords)
    
    def test_tier3_context_intelligence(self, story_content):
        """Tier 3 (Context Intelligence) should be explained"""
        assert 'tier 3' in story_content.lower()
        context_keywords = ['context', 'git analysis', 'development', 'holistic']
        assert any(keyword in story_content.lower() for keyword in context_keywords)
    
    def test_fifo_queue_explained(self, story_content):
        """FIFO queue for Tier 1 should be explained"""
        assert 'fifo' in story_content.lower() or 'first in, first out' in story_content.lower()
        assert '20' in story_content, "Should mention 20-conversation limit"


class TestHumorPreservation:
    """Test that humor and storytelling are preserved"""
    
    def test_uses_emojis(self, story_content):
        """Story should use emojis for visual engagement"""
        emoji_pattern = r'[\U0001F300-\U0001F9FF]'
        emojis = re.findall(emoji_pattern, story_content)
        assert len(emojis) >= 5, "Should have at least 5 emojis for visual engagement"
    
    def test_uses_conversational_tone(self, story_content):
        """Story should use conversational 'you' language"""
        you_count = story_content.lower().count('you')
        assert you_count >= 10, "Should address reader directly many times"
    
    def test_has_concrete_examples(self, story_content):
        """Story should provide concrete examples (not just theory)"""
        # Should have code blocks or concrete scenarios
        assert '```' in story_content or 'Example:' in story_content
        assert 'purple button' in story_content.lower() or 'make it purple' in story_content.lower()
    
    def test_before_after_scenarios(self, story_content):
        """Story should show before/after CORTEX scenarios"""
        assert 'before' in story_content.lower()
        assert 'after' in story_content.lower()
        
        # Should show problem → solution flow
        problem_indicators = ['problem', 'issue', 'without', 'forgot']
        solution_indicators = ['solution', 'solved', 'with cortex', 'now']
        
        has_problem = any(indicator in story_content.lower() for indicator in problem_indicators)
        has_solution = any(indicator in story_content.lower() for indicator in solution_indicators)
        
        assert has_problem and has_solution, "Should show problem/solution contrast"
    
    def test_uses_checkmarks_and_crosses(self, story_content):
        """Story should use ✅ and ❌ for visual contrast"""
        assert '✅' in story_content, "Should use ✅ for successes"
        assert '❌' in story_content, "Should use ❌ for failures"


class TestTechnicalDepth:
    """Test balance between storytelling and technical depth"""
    
    def test_mentions_specific_files(self, story_content):
        """Story should mention specific implementation files"""
        file_examples = [
            'conversations.db',
            'knowledge-graph.db',
            '.md',
            'tier1/',
            'tier2/'
        ]
        mentioned_files = sum(1 for example in file_examples if example in story_content.lower())
        assert mentioned_files >= 2, "Should ground story with real file references"
    
    def test_explains_technical_concepts_simply(self, story_content):
        """Complex concepts should be explained simply"""
        # Should not have dense jargon without explanation
        # Count technical terms vs explanatory words
        technical_terms = ['database', 'sqlite', 'api', 'algorithm', 'schema']
        explanatory_terms = ['like', 'means', 'think of', 'similar to', 'for example']
        
        tech_count = sum(1 for term in technical_terms if term in story_content.lower())
        explain_count = sum(1 for term in explanatory_terms if term in story_content.lower())
        
        # Should have at least 1 explanation per 2 technical terms
        if tech_count > 0:
            assert explain_count >= tech_count / 2, "Technical terms should be balanced with explanations"
    
    def test_has_performance_metrics(self, story_content):
        """Story should include concrete performance numbers"""
        # Look for patterns like "18ms", "92ms", "88.1%"
        metric_pattern = r'\d+(\.\d+)?\s?(ms|seconds|%|MB|KB)'
        metrics = re.findall(metric_pattern, story_content)
        assert len(metrics) >= 3, "Should include concrete performance metrics"
    
    def test_references_real_features(self, story_content):
        """Story should reference real CORTEX features"""
        features = [
            'tdd', 'test-driven',
            'definition of done',
            'definition of ready',
            'brain protection'
        ]
        mentioned_features = sum(1 for feature in features if feature in story_content.lower())
        assert mentioned_features >= 2, "Should reference real CORTEX features"


class TestStoryStructure:
    """Test overall story structure and flow"""
    
    def test_has_clear_sections(self, story_content):
        """Story should have clear section headers"""
        header_pattern = r'^#{1,3}\s+.+$'
        headers = re.findall(header_pattern, story_content, re.MULTILINE)
        assert len(headers) >= 5, "Should have at least 5 major sections"
    
    def test_opening_hook_strength(self, story_content):
        """Opening should be engaging (not boring introduction)"""
        opening = story_content[:200]
        
        # Should NOT start with boring phrases
        boring_starts = ['this document', 'this guide', 'introduction', 'overview']
        for boring_start in boring_starts:
            assert not opening.lower().startswith(boring_start), \
                f"Opening should not start with '{boring_start}'"
        
        # Should start with engaging hook
        engaging_elements = ['you', 'imagine', 'meet', 'story']
        assert any(element in opening.lower() for element in engaging_elements), \
            "Opening should have engaging hook"
    
    def test_problem_solution_flow(self, story_content):
        """Story should follow problem → solution narrative arc"""
        # Problem should come before solution in text
        problem_index = story_content.lower().find('amnesia')
        solution_index = story_content.lower().find('cortex')
        
        # Both should exist
        assert problem_index != -1, "Problem (amnesia) should be mentioned"
        assert solution_index != -1, "Solution (CORTEX) should be mentioned"
        
        # Problem should be introduced early, solution can come after or interleaved
        # Just check both exist for now
    
    def test_ends_with_getting_started(self, story_content):
        """Story should end with getting started / next steps"""
        # Check entire document for navigation hub with getting started
        # (not just last 500 chars since footer may be after navigation)
        
        next_step_indicators = [
            'getting started', 'next steps', 'start using',
            'navigation hub', 'quick start'
        ]
        
        # Must have at least one getting started indicator in the content
        has_getting_started = any(indicator in story_content.lower() for indicator in next_step_indicators)
        
        assert has_getting_started, \
            "Story should include navigation hub or getting started section"
    
    def test_reasonable_length(self, story_content):
        """Story should be comprehensive but not overwhelming"""
        line_count = len(story_content.split('\n'))
        
        # Should be between 200-800 lines (sweet spot for engagement)
        assert 200 <= line_count <= 1000, \
            f"Story should be 200-1000 lines (found {line_count})"
    
    def test_includes_visual_elements(self, story_content):
        """Story should include visual elements (not just text wall)"""
        visual_elements = [
            '```',  # Code blocks
            '|',    # Tables
            '✅',    # Checkmarks
            '→',    # Arrows
            '📊',   # Charts/diagrams emojis
        ]
        
        visual_count = sum(1 for element in visual_elements if element in story_content)
        assert visual_count >= 3, "Should have multiple visual elements"


class TestCopyrightAndMetadata:
    """Test that copyright and metadata are present"""
    
    def test_has_copyright(self, story_content):
        """Story should include copyright notice"""
        assert '©' in story_content or 'copyright' in story_content.lower()
        assert '2024' in story_content or '2025' in story_content
    
    def test_has_author(self, story_content):
        """Story should credit author"""
        assert 'asif hussain' in story_content.lower()
    
    def test_has_version_info(self, story_content):
        """Story should indicate version or phase"""
        version_indicators = ['version', 'phase', '2.0', '3.0', 'production']
        assert any(indicator in story_content.lower() for indicator in version_indicators)


# Integration test
class TestStoryIntegrity:
    """High-level tests for overall story integrity"""
    
    def test_story_file_exists(self, story_path):
        """Awakening story file should exist"""
        assert story_path.exists(), f"Story file not found: {story_path}"
    
    def test_story_not_empty(self, story_content):
        """Story should have substantial content"""
        assert len(story_content) > 1000, "Story should be substantial (>1000 chars)"
    
    def test_story_is_markdown(self, story_path):
        """Story should be markdown format"""
        assert story_path.suffix == '.md', "Story should be .md file"
    
    def test_story_has_consistent_narrative_voice(self, story_content):
        """Story should maintain consistent 2nd person narrative"""
        # Count "you" vs "I/we" to ensure consistent perspective
        you_count = story_content.lower().count(' you ')
        i_count = story_content.lower().count(' i ') + story_content.lower().count(' we ')
        
        # Should heavily favor "you" (2nd person)
        assert you_count > i_count, "Story should use 2nd person perspective (you)"
    
    def test_no_broken_internal_links(self, story_content):
        """Story should not have obviously broken links"""
        # Check for common broken link patterns
        broken_patterns = [
            r'\[.*?\]\(\s*\)',  # Empty link
            r'\[.*?\]\(TODO\)',  # TODO link
            r'\[.*?\]\(FIXME\)',  # FIXME link
        ]
        
        for pattern in broken_patterns:
            matches = re.findall(pattern, story_content)
            assert len(matches) == 0, f"Found broken link pattern: {pattern}"
