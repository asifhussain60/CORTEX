"""
Tests for CORTEX Story Generator

Validates:
- Story structure (chapters, sections)
- Content completeness (all features covered)
- Humor tone (Codenstein-Copilot dialogue)
- Feature showcase (individual + team capabilities)
- Word count and quality metrics

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from epm.modules.story_generator_enhanced import StoryGeneratorEnhanced


@pytest.fixture
def root_path():
    """Get CORTEX root path"""
    return Path(__file__).parent.parent


@pytest.fixture
def generator(root_path):
    """Create story generator instance"""
    return StoryGeneratorEnhanced(root_path, dry_run=True)


@pytest.fixture
def story_data(generator):
    """Collect story data"""
    return generator._collect_story_data()


@pytest.fixture
def story_content(generator, story_data):
    """Generate story content"""
    return generator._generate_hilarious_story(story_data)


class TestStoryStructure:
    """Test story structure and organization"""
    
    def test_has_prologue(self, story_content):
        """Story should have a prologue"""
        assert "## Prologue:" in story_content
        assert "Codenstein" in story_content
        assert "Copilot" in story_content
    
    def test_has_chapter_1(self, story_content):
        """Story should have Chapter 1: Amnesia Problem"""
        assert "## Chapter 1:" in story_content
        assert "Amnesia" in story_content
        assert "Make It Purple" in story_content
    
    def test_has_chapter_2(self, story_content):
        """Story should have Chapter 2: Brain Building"""
        assert "## Chapter 2:" in story_content
        assert "Four-Tier Brain" in story_content or "Brain Transplant" in story_content
    
    def test_has_chapter_3_tier_system(self, story_content):
        """Story should have Chapter 3: Tier System"""
        assert "## Chapter 3:" in story_content
        assert "Tier 0" in story_content
        assert "Tier 1" in story_content
        assert "Tier 2" in story_content
        assert "Tier 3" in story_content
    
    def test_has_chapter_4_agents(self, story_content):
        """Story should have Chapter 4: 10 Agents"""
        assert "## Chapter 4:" in story_content
        assert "10 Agents" in story_content or "Specialist Agents" in story_content
        assert "LEFT BRAIN" in story_content
        assert "RIGHT BRAIN" in story_content
    
    def test_has_chapter_5_tdd(self, story_content):
        """Story should have Chapter 5: TDD Enforcement"""
        assert "## Chapter 5:" in story_content
        assert "TDD" in story_content
        assert "RED" in story_content
        assert "GREEN" in story_content
        assert "REFACTOR" in story_content
    
    def test_has_chapter_6_planning(self, story_content):
        """Story should have Chapter 6: Planning System"""
        assert "## Chapter 6:" in story_content
        assert "Planning" in story_content
        assert "Phase" in story_content or "PHASE" in story_content
    
    def test_has_chapter_7_team(self, story_content):
        """Story should have Chapter 7: Team Collaboration"""
        assert "## Chapter 7:" in story_content
        assert "Team" in story_content or "Collaboration" in story_content
        assert "Pull Request" in story_content or "PR" in story_content
    
    def test_has_chapter_8_advanced(self, story_content):
        """Story should have Chapter 8: Advanced Features"""
        assert "## Chapter 8:" in story_content
        assert "Advanced" in story_content or "Sorcery" in story_content
        assert "Hotspot" in story_content
    
    def test_has_epilogue(self, story_content):
        """Story should have an epilogue"""
        assert "## Epilogue:" in story_content
        assert "Brain Lives" in story_content
        assert "Your Turn" in story_content


class TestContentCompleteness:
    """Test that all features are covered"""
    
    def test_covers_tier_0_features(self, story_content):
        """Story should cover all Tier 0 features"""
        assert "TDD enforcement" in story_content or "Tests first" in story_content
        assert "Definition of Done" in story_content or "DoD" in story_content
        assert "Brain Protection" in story_content
        assert "Rule #22" in story_content
    
    def test_covers_tier_1_features(self, story_content):
        """Story should cover Tier 1 working memory"""
        assert "Working Memory" in story_content
        assert "20 conversations" in story_content
        assert "Context" in story_content
        assert "purple button" in story_content.lower() or "make it purple" in story_content.lower()
    
    def test_covers_tier_2_features(self, story_content):
        """Story should cover Tier 2 knowledge graph"""
        assert "Knowledge Graph" in story_content
        assert "Pattern" in story_content
        assert "learn" in story_content.lower() or "reuse" in story_content.lower()
    
    def test_covers_tier_3_features(self, story_content):
        """Story should cover Tier 3 context intelligence"""
        assert "Context Intelligence" in story_content or "Hotspot" in story_content
        assert "git" in story_content.lower() or "commit" in story_content.lower()
        assert "warn" in story_content.lower()
    
    def test_covers_all_10_agents(self, story_content):
        """Story should mention all 10 agents"""
        # Left brain agents
        assert "Builder" in story_content or "code-executor" in story_content
        assert "Tester" in story_content or "test-generator" in story_content
        assert "Fixer" in story_content or "error-corrector" in story_content
        assert "Inspector" in story_content or "health-validator" in story_content
        assert "Archivist" in story_content or "commit-handler" in story_content
        
        # Right brain agents
        assert "Dispatcher" in story_content or "intent-router" in story_content
        assert "Planner" in story_content or "work-planner" in story_content
        assert "Analyst" in story_content or "screenshot-analyzer" in story_content
        assert "Governor" in story_content or "change-governor" in story_content
        assert "Brain Protector" in story_content or "brain-protector" in story_content
    
    def test_covers_tdd_workflow(self, story_content):
        """Story should explain TDD workflow"""
        assert "RED" in story_content
        assert "GREEN" in story_content
        assert "REFACTOR" in story_content
        assert "tests first" in story_content.lower() or "test-first" in story_content.lower()
    
    def test_covers_planning_system(self, story_content):
        """Story should explain planning system"""
        assert "plan" in story_content.lower()
        assert "Phase" in story_content or "PHASE" in story_content
        assert "roadmap" in story_content.lower() or "estimate" in story_content.lower()
    
    def test_covers_team_features(self, story_content):
        """Story should cover team collaboration features"""
        assert "Pull Request" in story_content or "PR" in story_content
        assert "review" in story_content.lower()
        assert "team" in story_content.lower()
        assert "onboard" in story_content.lower() or "new developer" in story_content.lower()
    
    def test_covers_individual_developer_features(self, story_content):
        """Story should cover individual developer features"""
        assert "context continuity" in story_content.lower() or "remember" in story_content.lower()
        assert "pattern reuse" in story_content.lower()
        assert "warning" in story_content.lower() or "warn" in story_content.lower()


class TestHumorTone:
    """Test that story maintains humorous Codenstein-Copilot dialogue"""
    
    def test_has_dialogue_format(self, story_content):
        """Story should use dialogue format"""
        assert "Codenstein:" in story_content or "**Codenstein:**" in story_content
        assert "Copilot:" in story_content or "**Copilot:**" in story_content
    
    def test_has_humorous_elements(self, story_content):
        """Story should contain humorous elements"""
        # Check for humor indicators
        humor_indicators = [
            "lol",
            "🎉",
            "😐",
            "coffee mug",
            "Roomba",
            "cat",
            "mustache quivered",
            "tea went cold",
            "terrifying",
            "basement"
        ]
        
        found_indicators = sum(1 for indicator in humor_indicators if indicator.lower() in story_content.lower())
        assert found_indicators >= 5, f"Only found {found_indicators} humor indicators, expected at least 5"
    
    def test_has_character_interactions(self, story_content):
        """Story should have character interactions"""
        # Should have multiple exchanges
        codenstein_count = story_content.count("Codenstein:")
        copilot_count = story_content.count("Copilot:")
        
        assert codenstein_count >= 20, f"Only {codenstein_count} Codenstein lines"
        assert copilot_count >= 20, f"Only {copilot_count} Copilot lines"
    
    def test_maintains_narrative_voice(self, story_content):
        """Story should maintain narrative voice"""
        assert "scientist" in story_content.lower()
        assert "madman" in story_content.lower()
        assert "New Jersey" in story_content or "basement" in story_content.lower()


class TestQualityMetrics:
    """Test story quality metrics"""
    
    def test_minimum_word_count(self, story_content):
        """Story should meet minimum word count"""
        word_count = len(story_content.split())
        assert word_count >= 5000, f"Story only has {word_count} words, expected at least 5000"
    
    def test_has_proper_markdown_formatting(self, story_content):
        """Story should use proper markdown"""
        assert story_content.startswith("# The CORTEX Story:")
        assert "## Prologue:" in story_content
        assert "---" in story_content  # Section dividers
    
    def test_has_code_examples(self, story_content):
        """Story should include code examples (either fenced or indented)"""
        # Check for indented code blocks (at least 4 spaces or a tab)
        has_indented_code = any(
            line.startswith("    ") and len(line.strip()) > 0
            for line in story_content.split("\n")
        )
        # Or check for traditional code fences
        has_fenced_code = "```" in story_content
        
        assert has_indented_code or has_fenced_code, "Story should include code examples"
    
    def test_has_proper_copyright(self, story_content):
        """Story should have copyright notice"""
        assert "© 2024-2025 Asif Hussain" in story_content
        assert "All rights reserved" in story_content
    
    def test_has_call_to_action(self, story_content):
        """Story should have call to action"""
        assert "Your Turn" in story_content or "Ready to" in story_content
        assert "Setup Guide" in story_content or "Quick Start" in story_content


class TestFeatureShowcase:
    """Test that story showcases specific features through examples"""
    
    def test_showcases_memory_continuity(self, story_content):
        """Story should show memory continuity in action"""
        # Should have example of remembering previous context
        assert "purple" in story_content.lower()
        assert "button" in story_content.lower()
        assert "remember" in story_content.lower()
    
    def test_showcases_pattern_learning(self, story_content):
        """Story should show pattern learning"""
        assert "authentication" in story_content.lower() or "auth" in story_content.lower()
        assert "pattern" in story_content.lower()
        assert "reuse" in story_content.lower() or "learned" in story_content.lower()
    
    def test_showcases_hotspot_detection(self, story_content):
        """Story should show hotspot detection"""
        assert "hotspot" in story_content.lower()
        assert "commit" in story_content.lower()
        assert "Friday" in story_content or "weekend" in story_content.lower()
    
    def test_showcases_rule_22(self, story_content):
        """Story should show Rule #22 brain protection"""
        assert "Rule #22" in story_content or "rule 22" in story_content.lower()
        assert "delete" in story_content.lower()
        assert "brain" in story_content.lower()
        assert "lol no" in story_content.lower() or "blocked" in story_content.lower()
    
    def test_showcases_pr_review(self, story_content):
        """Story should show PR review feature"""
        assert "Pull Request" in story_content or "PR" in story_content
        assert "review" in story_content.lower()
        assert "APPROVED" in story_content or "approved" in story_content.lower()


def test_story_generation_success(root_path):
    """Test that story generation completes successfully"""
    generator = StoryGeneratorEnhanced(root_path, dry_run=True)
    result = generator.generate_story()
    
    assert result["success"] == True
    assert result["word_count"] >= 5000
    assert result["content_length"] > 0


def test_story_data_collection(generator):
    """Test that story data collection works"""
    data = generator._collect_story_data()
    
    assert "timestamp" in data
    assert "version" in data
    assert "agents" in data
    assert "tiers" in data
    assert "left_brain" in data["agents"]
    assert "right_brain" in data["agents"]
    assert len(data["agents"]["left_brain"]) == 5
    assert len(data["agents"]["right_brain"]) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
