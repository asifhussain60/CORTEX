"""
Tests for Phase 3: Interactive Clarification System

Tests the ambiguity detection, question generation, and multi-round
clarification conversation capabilities.

Author: Asif Hussain
Created: 2025-11-27
Version: 1.0
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.orchestrators.ado_work_item_orchestrator import (
    ADOWorkItemOrchestrator,
    WorkItemType,
    WorkItemMetadata,
    ClarificationChoice,
    ClarificationRound,
    ConversationState
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_cortex_dir():
    """Create temporary CORTEX directory structure."""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create required directory structure
    cortex_brain = temp_dir / "cortex-brain"
    cortex_brain.mkdir(parents=True)
    
    documents = cortex_brain / "documents"
    documents.mkdir()
    
    planning = documents / "planning"
    planning.mkdir()
    
    ado_dir = planning / "ado"
    ado_dir.mkdir()
    
    (ado_dir / "active").mkdir()
    (ado_dir / "completed").mkdir()
    (ado_dir / "blocked").mkdir()
    
    # Create config directory and clarification rules
    config_dir = cortex_brain / "config"
    config_dir.mkdir()
    
    rules_file = config_dir / "clarification-rules.yaml"
    rules_content = """
clarification_settings:
  max_rounds: 4
  min_rounds: 1
  auto_trigger_threshold: 6
  enabled: true

ambiguity_detection:
  vague_language_weight: 2.0
  missing_fields_weight: 3.0
  technical_ambiguity_weight: 2.5
  security_concerns_weight: 3.0
  
  vague_patterns:
    - '\\b(maybe|perhaps|possibly|might|could be|probably)\\b'
    - '\\b(some|few|several|various|multiple)\\b'
    - '\\b(approximately|around|about|roughly)\\b'
  
  required_fields:
    acceptance_criteria: "What are the success criteria?"
    technical_approach: "What is the technical implementation approach?"
  
  technical_ambiguity_indicators:
    - "no architecture specified"
    - "unclear API contract"
  
  security_concern_indicators:
    - "authentication"
    - "authorization"
    - "password"

question_categories:
  - id: scope
    name: "Scope Clarification"
    priority: 1
    questions:
      - id: scope_type
        text: "What is the primary scope of this work item?"
        choices:
          - letter: "a"
            text: "New feature"
            category: "scope"
          - letter: "b"
            text: "Enhancement"
            category: "scope"
          - letter: "c"
            text: "Bug fix"
            category: "scope"
  
  - id: technical
    name: "Technical Approach"
    priority: 2
    questions:
      - id: tech_components
        text: "Which components will be affected?"
        choices:
          - letter: "a"
            text: "Frontend only"
            category: "technical"
          - letter: "b"
            text: "Backend only"
            category: "technical"
          - letter: "c"
            text: "Both frontend and backend"
            category: "technical"
  
  - id: ui_ux
    name: "User Experience"
    priority: 3
    questions:
      - id: user_impact
        text: "What is the expected user impact?"
        choices:
          - letter: "a"
            text: "High impact"
            category: "ui_ux"
          - letter: "b"
            text: "Medium impact"
            category: "ui_ux"
          - letter: "c"
            text: "Low impact"
            category: "ui_ux"
  
  - id: quality
    name: "Quality Requirements"
    priority: 4
    questions:
      - id: test_coverage
        text: "What level of test coverage is required?"
        choices:
          - letter: "a"
            text: "High coverage (80%+)"
            category: "quality"
          - letter: "b"
            text: "Medium coverage (60%+)"
            category: "quality"
          - letter: "c"
            text: "Low coverage"
            category: "quality"

choice_format:
  pattern: "[round][letter]"
  multi_select_separator: ","
  case_sensitive: false
  allow_skip: true
"""
    rules_file.write_text(rules_content)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def orchestrator(temp_cortex_dir):
    """Create ADOWorkItemOrchestrator instance."""
    return ADOWorkItemOrchestrator(cortex_root=str(temp_cortex_dir))


# ============================================================================
# TEST AMBIGUITY DETECTION
# ============================================================================

class TestAmbiguityDetection:
    """Test ambiguity detection engine."""
    
    def test_detect_vague_language(self, orchestrator):
        """Test detection of vague language patterns."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Authentication",
            description="Maybe add authentication. Possibly use JWT. This might work."
        )
        
        score, issues = orchestrator.detect_ambiguities(metadata)
        
        assert score > 0, "Should detect vague language"
        assert any("vague language" in issue.lower() for issue in issues), \
            "Issues should mention vague language"
    
    def test_detect_missing_acceptance_criteria(self, orchestrator):
        """Test detection of missing acceptance criteria."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Dashboard",
            description="Build a user dashboard",
            acceptance_criteria=[]  # Empty
        )
        
        score, issues = orchestrator.detect_ambiguities(metadata)
        
        assert score > 0, "Should detect missing acceptance criteria"
        assert any("missing information" in issue.lower() for issue in issues), \
            "Issues should mention missing information"
    
    def test_detect_technical_ambiguity(self, orchestrator):
        """Test detection of technical ambiguity indicators."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.FEATURE,
            title="API Integration",
            description="Integrate with API. No architecture specified. Unclear API contract."
        )
        
        score, issues = orchestrator.detect_ambiguities(metadata)
        
        assert score > 0, "Should detect technical ambiguity"
        assert any("technical ambiguity" in issue.lower() for issue in issues), \
            "Issues should mention technical ambiguity"
    
    def test_detect_security_concerns(self, orchestrator):
        """Test detection of security-sensitive work without security consideration."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Login",
            description="Add user authentication with password storage"
        )
        
        score, issues = orchestrator.detect_ambiguities(metadata)
        
        assert score > 0, "Should detect security concerns"
        assert any("security" in issue.lower() for issue in issues), \
            "Issues should mention security"
    
    def test_no_ambiguities(self, orchestrator):
        """Test that clean work items have low ambiguity scores."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Dashboard Implementation",
            description="""
            Implement user dashboard with clear technical approach.
            
            Technical implementation will use React for frontend.
            User flow: Login -> Dashboard -> View Data.
            
            Security: Standard authentication patterns, no sensitive data.
            """,
            acceptance_criteria=[
                "Dashboard loads in <2 seconds",
                "User can view all data",
                "Responsive design works on mobile"
            ]
        )
        
        score, issues = orchestrator.detect_ambiguities(metadata)
        
        # Should have very low score (maybe not zero, but low)
        assert score < 5, f"Should have low ambiguity score, got {score}"


# ============================================================================
# TEST QUESTION GENERATION
# ============================================================================

class TestQuestionGeneration:
    """Test clarification question generation."""
    
    def test_generate_scope_questions(self, orchestrator):
        """Test generation of scope clarification questions."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Feature",
            description="Maybe add feature"
        )
        
        issues = ["Vague language detected"]
        rounds = orchestrator.generate_clarification_questions(metadata, issues)
        
        assert len(rounds) > 0, "Should generate at least one round"
        assert rounds[0].category == "scope", "First round should be scope"
        assert len(rounds[0].choices) > 0, "Should have multiple choices"
    
    def test_generate_technical_questions(self, orchestrator):
        """Test generation of technical clarification questions."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.FEATURE,
            title="API Integration",
            description="No architecture specified"
        )
        
        issues = ["Technical ambiguity detected", "Missing information"]
        rounds = orchestrator.generate_clarification_questions(metadata, issues)
        
        # Should have scope + technical rounds
        assert len(rounds) >= 2, "Should generate scope and technical rounds"
        assert any(r.category == "technical" for r in rounds), \
            "Should include technical questions"
    
    def test_generate_uiux_questions_for_stories(self, orchestrator):
        """Test that UI/UX questions are generated for Stories."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="User Story",
            description="Add feature"
        )
        
        issues = ["Missing information"]
        rounds = orchestrator.generate_clarification_questions(metadata, issues)
        
        # Should include UI/UX questions for stories
        assert any(r.category == "ui_ux" for r in rounds), \
            "Should include UI/UX questions for user stories"
    
    def test_generate_quality_questions(self, orchestrator):
        """Test generation of quality/security questions."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Login Feature",
            description="Add authentication"
        )
        
        issues = ["Security-sensitive work"]
        rounds = orchestrator.generate_clarification_questions(metadata, issues)
        
        # Should include quality questions for security concerns
        assert any(r.category == "quality" for r in rounds), \
            "Should include quality questions for security work"
    
    def test_respect_max_rounds(self, orchestrator):
        """Test that max rounds limit is respected."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.FEATURE,
            title="Complex Feature",
            description="Many issues"
        )
        
        issues = [
            "Vague language",
            "Missing information",
            "Technical ambiguity",
            "Security concerns"
        ]
        rounds = orchestrator.generate_clarification_questions(metadata, issues)
        
        # Should not exceed max_rounds (4 in test config)
        assert len(rounds) <= 4, "Should not exceed max_rounds configuration"


# ============================================================================
# TEST PROMPT FORMATTING
# ============================================================================

class TestPromptFormatting:
    """Test clarification prompt formatting."""
    
    def test_format_prompt_structure(self, orchestrator):
        """Test that formatted prompt has correct structure."""
        round = ClarificationRound(
            round_number=1,
            question="What is the scope?",
            category="scope",
            choices=[
                ClarificationChoice(letter="a", text="New feature", category="scope"),
                ClarificationChoice(letter="b", text="Enhancement", category="scope")
            ]
        )
        
        prompt = orchestrator.format_clarification_prompt(round, total_rounds=4)
        
        assert "Round 1 of 4" in prompt, "Should show round progress"
        assert "What is the scope?" in prompt, "Should include question"
        assert "1a. New feature" in prompt, "Should include choice 1a"
        assert "1b. Enhancement" in prompt, "Should include choice 1b"
        assert "skip" in prompt.lower(), "Should mention skip option"
        assert "done" in prompt.lower(), "Should mention done option"
    
    def test_format_prompt_letter_ids(self, orchestrator):
        """Test that choice IDs combine round number and letter."""
        round = ClarificationRound(
            round_number=3,
            question="Test question?",
            category="technical",
            choices=[
                ClarificationChoice(letter="a", text="Choice A", category="technical"),
                ClarificationChoice(letter="c", text="Choice C", category="technical")
            ]
        )
        
        prompt = orchestrator.format_clarification_prompt(round, total_rounds=4)
        
        assert "3a." in prompt, "Should have 3a choice ID"
        assert "3c." in prompt, "Should have 3c choice ID"


# ============================================================================
# TEST RESPONSE PARSING
# ============================================================================

class TestResponseParsing:
    """Test user response parsing."""
    
    def test_parse_single_choice(self, orchestrator):
        """Test parsing single choice response."""
        round = ClarificationRound(
            round_number=1,
            question="Test?",
            category="scope",
            choices=[
                ClarificationChoice(letter="a", text="Choice A", category="scope"),
                ClarificationChoice(letter="b", text="Choice B", category="scope")
            ]
        )
        
        is_valid, selected, error = orchestrator.parse_clarification_response("1a", round)
        
        assert is_valid, f"Should be valid: {error}"
        assert "a" in selected, "Should select choice 'a'"
    
    def test_parse_multiple_choices(self, orchestrator):
        """Test parsing multiple choice response."""
        round = ClarificationRound(
            round_number=2,
            question="Test?",
            category="technical",
            choices=[
                ClarificationChoice(letter="a", text="Choice A", category="technical"),
                ClarificationChoice(letter="b", text="Choice B", category="technical"),
                ClarificationChoice(letter="c", text="Choice C", category="technical")
            ]
        )
        
        is_valid, selected, error = orchestrator.parse_clarification_response("2a, 2c", round)
        
        assert is_valid, f"Should be valid: {error}"
        assert "a" in selected, "Should select choice 'a'"
        assert "c" in selected, "Should select choice 'c'"
        assert len(selected) == 2, "Should have exactly 2 selections"
    
    def test_parse_skip_command(self, orchestrator):
        """Test parsing 'skip' command."""
        round = ClarificationRound(
            round_number=1,
            question="Test?",
            category="scope",
            choices=[
                ClarificationChoice(letter="a", text="Choice A", category="scope")
            ]
        )
        
        is_valid, selected, error = orchestrator.parse_clarification_response("skip", round)
        
        assert is_valid, "Skip should be valid"
        assert len(selected) == 0, "Skip should have no selections"
    
    def test_parse_done_command(self, orchestrator):
        """Test parsing 'done' command."""
        round = ClarificationRound(
            round_number=1,
            question="Test?",
            category="scope",
            choices=[
                ClarificationChoice(letter="a", text="Choice A", category="scope")
            ]
        )
        
        is_valid, selected, error = orchestrator.parse_clarification_response("done", round)
        
        assert is_valid, "Done should be valid"
        assert len(selected) == 0, "Done should have no selections"
    
    def test_parse_invalid_choice(self, orchestrator):
        """Test parsing invalid choice."""
        round = ClarificationRound(
            round_number=1,
            question="Test?",
            category="scope",
            choices=[
                ClarificationChoice(letter="a", text="Choice A", category="scope"),
                ClarificationChoice(letter="b", text="Choice B", category="scope")
            ]
        )
        
        is_valid, selected, error = orchestrator.parse_clarification_response("1z", round)
        
        assert not is_valid, "Invalid choice should fail"
        assert "invalid" in error.lower(), "Error should mention invalid choice"
    
    def test_parse_case_insensitive(self, orchestrator):
        """Test that parsing is case-insensitive."""
        round = ClarificationRound(
            round_number=1,
            question="Test?",
            category="scope",
            choices=[
                ClarificationChoice(letter="a", text="Choice A", category="scope")
            ]
        )
        
        is_valid, selected, error = orchestrator.parse_clarification_response("1A", round)
        
        assert is_valid, "Should accept uppercase"
        assert "a" in selected, "Should normalize to lowercase"


# ============================================================================
# TEST CONTEXT INTEGRATION
# ============================================================================

class TestContextIntegration:
    """Test integration of clarification results into work item."""
    
    def test_integrate_single_round(self, orchestrator):
        """Test integrating clarifications from single round."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Test Story",
            description="Original description"
        )
        
        state = ConversationState(
            work_item_id="ADO-123",
            rounds=[
                ClarificationRound(
                    round_number=1,
                    question="What is the scope?",
                    category="scope",
                    choices=[
                        ClarificationChoice(letter="a", text="New feature", category="scope"),
                        ClarificationChoice(letter="b", text="Enhancement", category="scope")
                    ],
                    selected_choices=["b"]
                )
            ],
            context={"scope": {"type": "enhancement"}}
        )
        
        updated = orchestrator.integrate_clarification_context(metadata, state)
        
        assert "Clarified Requirements" in updated.description, \
            "Should add clarification section"
        assert "Enhancement" in updated.description, \
            "Should include selected choice text"
    
    def test_integrate_multiple_rounds(self, orchestrator):
        """Test integrating clarifications from multiple rounds."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Test Story",
            description="Original description"
        )
        
        state = ConversationState(
            work_item_id="ADO-123",
            rounds=[
                ClarificationRound(
                    round_number=1,
                    question="What is the scope?",
                    category="scope",
                    choices=[
                        ClarificationChoice(letter="a", text="New feature", category="scope"),
                        ClarificationChoice(letter="b", text="Enhancement", category="scope")
                    ],
                    selected_choices=["b"]
                ),
                ClarificationRound(
                    round_number=2,
                    question="Which components?",
                    category="technical",
                    choices=[
                        ClarificationChoice(letter="a", text="Frontend", category="technical"),
                        ClarificationChoice(letter="b", text="Backend", category="technical")
                    ],
                    selected_choices=["a", "b"]
                )
            ],
            context={
                "scope": {"type": "enhancement"},
                "technical": {"components": ["frontend", "backend"]}
            }
        )
        
        updated = orchestrator.integrate_clarification_context(metadata, state)
        
        assert "Scope (Round 1)" in updated.description, "Should have Round 1 section"
        assert "Technical (Round 2)" in updated.description, "Should have Round 2 section"
        assert "Frontend" in updated.description, "Should include frontend choice"
        assert "Backend" in updated.description, "Should include backend choice"
    
    def test_integrate_with_multi_select(self, orchestrator):
        """Test integration with multiple selections in one round."""
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.FEATURE,
            title="Test Feature",
            description="Original"
        )
        
        state = ConversationState(
            work_item_id="ADO-456",
            rounds=[
                ClarificationRound(
                    round_number=1,
                    question="Which components?",
                    category="technical",
                    choices=[
                        ClarificationChoice(letter="a", text="Component A", category="technical"),
                        ClarificationChoice(letter="b", text="Component B", category="technical"),
                        ClarificationChoice(letter="c", text="Component C", category="technical")
                    ],
                    selected_choices=["a", "c"]
                )
            ],
            context={}
        )
        
        updated = orchestrator.integrate_clarification_context(metadata, state)
        
        assert "Component A" in updated.description, "Should include choice A"
        assert "Component C" in updated.description, "Should include choice C"
        assert "Component B" not in updated.description, "Should not include unselected choice B"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
