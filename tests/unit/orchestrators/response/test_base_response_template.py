"""
Unit tests for BaseResponseTemplate system.

Tests:
- Header generation (single call enforcement)
- Section hierarchy (h2 → h3 → h4 cascade)
- Challenge box formatting
- Problem/Solution tables
- Orchestrator-specific customization

Module: tests.unit.orchestrators.response.test_base_response_template
Author: Asif Hussain
Created: 2026-02-09
Version: 1.0
"""

import pytest
from cortex.orchestrators.core.base_response_template import (
    BaseResponseTemplate,
    SeverityLevel,
    SectionType,
    TemplateConfig
)


# ============================================================================
# TEST FIXTURES
# ============================================================================


class MockOrchestrator(BaseResponseTemplate):
    """Mock orchestrator for testing."""
    
    def compose(self, **kwargs) -> str:
        """Mock compose method."""
        response = self.header("TEST")
        response += self.section("Test Section")
        return response


@pytest.fixture
def template():
    """Create test template instance."""
    return MockOrchestrator(orchestrator_name="TestOrchestrator")


# ============================================================================
# HEADER TESTS
# ============================================================================


def test_header_generation_format(template):
    """Test header generates correct format."""
    header = template.header("ANALYZE")
    
    assert "## 🧠 CORTEX ANALYZE" in header
    assert "**Author:** Asif Hussain" in header
    assert "**Orchestrator:** TestOrchestrator ✅" in header
    assert "---" in header


def test_header_single_call_enforcement(template):
    """Test header can only be called once per response."""
    # First call succeeds
    header1 = template.header("ANALYZE")
    assert header1
    
    # Second call raises error
    with pytest.raises(RuntimeError, match="Header already generated"):
        template.header("IMPLEMENT")


def test_header_reset_allows_reuse(template):
    """Test reset_state() allows header reuse."""
    header1 = template.header("ANALYZE")
    assert header1
    
    # Reset state
    template.reset_state()
    
    # Second header call succeeds after reset
    header2 = template.header("IMPLEMENT")
    assert header2
    assert "IMPLEMENT" in header2


# ============================================================================
# SECTION HIERARCHY TESTS
# ============================================================================


def test_section_h2_format(template):
    """Test section generates h2 headers."""
    section = template.section("Test Section", "📊")
    
    assert section.startswith("\n## ")
    assert "📊 Test Section" in section


def test_subsection_h3_format(template):
    """Test subsection generates h3 headers."""
    subsection = template.subsection("Test Subsection")
    
    assert subsection.startswith("\n### ")
    assert "Test Subsection" in subsection


def test_subsubsection_h4_format(template):
    """Test subsubsection generates h4 headers."""
    subsubsection = template.subsubsection("Test Nested")
    
    assert subsubsection.startswith("\n#### ")
    assert "Test Nested" in subsubsection


def test_section_auto_icon_inference(template):
    """Test automatic icon selection based on title."""
    # Analysis sections
    section = template.section("Analysis Results")
    assert "🔍" in section
    
    # Finding sections
    section = template.section("Key Findings")
    assert "📋" in section
    
    # Recommendation sections
    section = template.section("Recommendations")
    assert "🚀" in section


def test_section_count_tracking(template):
    """Test section count increments correctly."""
    assert template.get_section_count() == 0
    
    template.section("Section 1")
    assert template.get_section_count() == 1
    
    template.section("Section 2")
    assert template.get_section_count() == 2


# ============================================================================
# CHALLENGE BOX TESTS
# ============================================================================


def test_challenge_box_format(template):
    """Test challenge box generates correct format."""
    box = template.challenge_box(
        title="Design Question",
        content="Should we use async or sync?",
        severity=SeverityLevel.WARNING
    )
    
    assert box.startswith("\n>")
    assert "⚠️ **CHALLENGE: Design Question**" in box
    assert "Should we use async or sync?" in box
    assert "**Response:** [Awaiting user input]" in box


def test_challenge_box_severity_levels(template):
    """Test different severity levels use correct emoji."""
    # Critical
    box = template.challenge_box("Critical", "Content", SeverityLevel.CRITICAL)
    assert "🔴" in box
    
    # Warning
    box = template.challenge_box("Warning", "Content", SeverityLevel.WARNING)
    assert "⚠️" in box
    
    # Info
    box = template.challenge_box("Info", "Content", SeverityLevel.INFO)
    assert "ℹ️" in box
    
    # Success
    box = template.challenge_box("Success", "Content", SeverityLevel.SUCCESS)
    assert "✅" in box


def test_challenge_box_custom_response_prompt(template):
    """Test custom response prompt in challenge box."""
    box = template.challenge_box(
        title="Question",
        content="Content",
        response_prompt="**Action Required:** Please confirm"
    )
    
    assert "**Action Required:** Please confirm" in box


# ============================================================================
# PROBLEM/SOLUTION TABLE TESTS
# ============================================================================


def test_problem_solution_table_format(template):
    """Test problem/solution table generates correct format."""
    rows = [
        ("Static routing", "Dynamic routing"),
        ("Stub data", "Real AST analysis"),
    ]
    
    table = template.problem_solution_table(rows)
    
    assert "| 🔴 **Problem** | 🟢 **Solution** |" in table
    assert "|----------------|------------------|" in table
    assert "Static routing" in table
    assert "Dynamic routing" in table


def test_problem_solution_table_custom_headers(template):
    """Test custom column headers."""
    rows = [("Issue", "Fix")]
    
    table = template.problem_solution_table(
        rows,
        problem_header="❌ **Issue**",
        solution_header="✅ **Fix**"
    )
    
    assert "❌ **Issue**" in table
    assert "✅ **Fix**" in table


def test_problem_solution_table_empty_rows(template):
    """Test empty rows returns empty string."""
    table = template.problem_solution_table([])
    assert table == ""


# ============================================================================
# CONFIGURATION TESTS
# ============================================================================


def test_template_config_defaults():
    """Test default template configuration."""
    config = TemplateConfig(orchestrator_name="TestOrch")
    
    assert config.orchestrator_name == "TestOrch"
    assert config.custom_blocks == []
    assert config.enable_challenge_box is True
    assert config.enable_problem_solution is True


def test_template_config_disable_features():
    """Test disabling template features."""
    config = TemplateConfig(
        orchestrator_name="TestOrch",
        enable_challenge_box=False,
        enable_problem_solution=False
    )
    
    template = MockOrchestrator(orchestrator_name="TestOrch")
    template.config = config
    
    # Challenge box should return empty
    box = template.challenge_box("Title", "Content")
    assert box == ""
    
    # Problem/solution table should return empty
    table = template.problem_solution_table([("P", "S")])
    assert table == ""


# ============================================================================
# STATE MANAGEMENT TESTS
# ============================================================================


def test_is_header_generated_state(template):
    """Test header generation state tracking."""
    assert template.is_header_generated() is False
    
    template.header("TEST")
    assert template.is_header_generated() is True
    
    template.reset_state()
    assert template.is_header_generated() is False


def test_reset_state_clears_all_counters(template):
    """Test reset_state() clears all state."""
    # Generate content
    template.header("TEST")
    template.section("Section 1")
    template.section("Section 2")
    
    assert template.is_header_generated() is True
    assert template.get_section_count() == 2
    
    # Reset
    template.reset_state()
    
    assert template.is_header_generated() is False
    assert template.get_section_count() == 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_full_response_composition(template):
    """Test composing complete response with all elements."""
    response = template.header("ANALYZE")
    response += template.section("Analysis", "🔍")
    response += template.subsection("Findings")
    response += template.subsubsection("Strengths")
    response += "\n- Finding 1\n"
    response += template.problem_solution_table([
        ("Problem 1", "Solution 1"),
        ("Problem 2", "Solution 2"),
    ])
    response += template.challenge_box("Question", "Should we...?")
    
    # Verify structure
    assert "## 🧠 CORTEX ANALYZE" in response  # h2 header
    assert "## 🔍 Analysis" in response  # h2 section
    assert "### Findings" in response  # h3 subsection
    assert "#### Strengths" in response  # h4 nested
    assert "| 🔴 **Problem** | 🟢 **Solution** |" in response  # table
    assert "> ⚠️ **CHALLENGE:" in response  # challenge box


def test_hierarchy_cascade_validation(template):
    """Test proper hierarchy cascade (h2 → h3 → h4)."""
    response = template.compose()
    
    # Should have h2 for main section
    assert "\n## " in response or "## 🧠" in response
    
    # Add subsections
    response += template.subsection("Subsection")
    response += template.subsubsection("Nested")
    
    # Check cascade
    assert response.index("\n## ") < response.index("\n### ")
    assert response.index("\n### ") < response.index("\n#### ")


# ============================================================================
# AC MARKERS (TDD-FIRST)
# ============================================================================


# AC_START: AC-ENH064-001
# Description: BaseResponseTemplate header generation
# Status: ✅ PASSING (test_header_generation_format, test_header_single_call_enforcement)
# AC_COMPLETE: AC-ENH064-001 ✅

# AC_START: AC-ENH064-002
# Description: Section hierarchy cascade (h2 → h3 → h4)
# Status: ✅ PASSING (test_section_h2_format, test_subsection_h3_format, test_subsubsection_h4_format)
# AC_COMPLETE: AC-ENH064-002 ✅

# AC_START: AC-ENH064-003
# Description: Challenge box formatting with severity levels
# Status: ✅ PASSING (test_challenge_box_format, test_challenge_box_severity_levels)
# AC_COMPLETE: AC-ENH064-003 ✅

# AC_START: AC-ENH064-004
# Description: Problem/Solution table generation
# Status: ✅ PASSING (test_problem_solution_table_format)
# AC_COMPLETE: AC-ENH064-004 ✅

# AC_START: AC-ENH064-005
# Description: Orchestrator-specific configuration support
# Status: ✅ PASSING (test_template_config_defaults, test_template_config_disable_features)
# AC_COMPLETE: AC-ENH064-005 ✅
