"""Tests for Phase 48 S5 Prompt Enhancement orchestrator.

Minimal prompt/agent adjustments based on validation insights.
"""

import pytest
from cortex.orchestrators.holistic.prompt_enhancement import (
    PromptEnhancementOrchestrator,
    PromptEnhancement,
    AgentEnhancement,
    EnhancementType,
)


class TestEnhancementType:
    """Tests for EnhancementType enum."""

    def test_all_enhancement_types(self):
        """Test all enhancement type values exist."""
        types = [
            EnhancementType.EXAMPLE,
            EnhancementType.RULE,
            EnhancementType.CLARIFICATION,
            EnhancementType.BEHAVIORAL_GUIDE,
            EnhancementType.EDGE_CASE,
        ]

        assert len(types) == 5

    def test_enhancement_type_values(self):
        """Test enhancement type string values."""
        assert EnhancementType.RULE.value == "rule"
        assert EnhancementType.EXAMPLE.value == "example"
        assert EnhancementType.CLARIFICATION.value == "clarification"


class TestPromptEnhancement:
    """Tests for PromptEnhancement dataclass."""

    def test_create_enhancement(self):
        """Test creating a prompt enhancement."""
        enhancement = PromptEnhancement(
            type=EnhancementType.RULE,
            section="TEST SECTION",
            current_text="Current approach",
            enhanced_text="Enhanced approach",
            rationale="This is why",
            impact="high",
        )

        assert enhancement.type == EnhancementType.RULE
        assert enhancement.section == "TEST SECTION"
        assert enhancement.impact == "high"

    def test_enhancement_impact_levels(self):
        """Test different impact levels."""
        for impact in ["low", "medium", "high"]:
            enhancement = PromptEnhancement(
                type=EnhancementType.RULE,
                section="Test",
                current_text="current",
                enhanced_text="enhanced",
                rationale="test",
                impact=impact,
            )
            assert enhancement.impact == impact


class TestAgentEnhancement:
    """Tests for AgentEnhancement dataclass."""

    def test_create_agent_enhancement(self):
        """Test creating an agent enhancement."""
        enhancement = AgentEnhancement(
            agent_name="TestAgent",
            agent_file="agents/test/test_agent.yaml",
            enhancement="Add capability X",
            rationale="Needed for Phase 48",
            impact="medium",
        )

        assert enhancement.agent_name == "TestAgent"
        assert "agents/" in enhancement.agent_file
        assert enhancement.impact == "medium"

    def test_agent_enhancement_completeness(self):
        """Test agent enhancement has all fields."""
        enhancement = AgentEnhancement(
            agent_name="Agent",
            agent_file="file.yaml",
            enhancement="Enhancement description",
            rationale="Rationale text",
            impact="high",
        )

        assert enhancement.agent_name is not None
        assert enhancement.agent_file is not None
        assert enhancement.enhancement is not None
        assert enhancement.rationale is not None
        assert enhancement.impact is not None


class TestPromptEnhancementOrchestrator:
    """Tests for PromptEnhancementOrchestrator."""

    def test_initialize(self):
        """Test initializing orchestrator."""
        orchestrator = PromptEnhancementOrchestrator()
        assert orchestrator is not None
        assert len(orchestrator.enhancements) == 0
        assert len(orchestrator.agent_enhancements) == 0

    def test_identify_enhancements(self):
        """Test identifying prompt enhancements."""
        orchestrator = PromptEnhancementOrchestrator()
        enhancements = orchestrator.identify_enhancements()

        assert isinstance(enhancements, list)
        assert len(enhancements) > 0
        assert all(isinstance(e, PromptEnhancement) for e in enhancements)

    def test_identify_enhancements_covers_key_areas(self):
        """Test enhancements cover all key areas from S1-S4."""
        orchestrator = PromptEnhancementOrchestrator()
        enhancements = orchestrator.identify_enhancements()

        sections = [e.section for e in enhancements]
        sections_upper = [s.upper() for s in sections]

        # Should cover areas from each stage
        assert any("PHASE DISCOVERY" in s for s in sections_upper)  # S1
        assert any("ORCHESTRATOR" in s for s in sections_upper)  # S2
        assert any("CHALLENGE" in s for s in sections_upper)  # S3
        assert any("VALIDATION" in s or "CORTEX" in s for s in sections_upper)  # S4
        assert any("SECURITY" in s or "ARCHITECTURE" in s for s in sections_upper)  # S4

    def test_identify_agent_enhancements(self):
        """Test identifying agent enhancements."""
        orchestrator = PromptEnhancementOrchestrator()
        enhancements = orchestrator.identify_agent_enhancements()

        assert isinstance(enhancements, list)
        assert len(enhancements) > 0
        assert all(isinstance(e, AgentEnhancement) for e in enhancements)

    def test_agent_enhancements_completeness(self):
        """Test agent enhancements are well-formed."""
        orchestrator = PromptEnhancementOrchestrator()
        enhancements = orchestrator.identify_agent_enhancements()

        for enhancement in enhancements:
            assert enhancement.agent_name
            assert ".yaml" in enhancement.agent_file
            assert enhancement.enhancement
            assert enhancement.rationale
            assert enhancement.impact in ["low", "medium", "high"]

    def test_generate_enhancement_report(self):
        """Test generating comprehensive enhancement report."""
        orchestrator = PromptEnhancementOrchestrator()
        report = orchestrator.generate_enhancement_report()

        assert report is not None
        assert "2026" in report.timestamp
        assert report.phase == "Phase 48 S5"
        assert len(report.prompt_enhancements) > 0
        assert len(report.agent_enhancements) > 0

    def test_enhancement_report_impact_calculation(self):
        """Test report correctly calculates total impact."""
        orchestrator = PromptEnhancementOrchestrator()
        report = orchestrator.generate_enhancement_report()

        assert report.total_impact in ["low", "medium", "high"]
        # Most enhancements are high impact
        assert report.total_impact in ["medium", "high"]

    def test_enhancement_report_recommendations(self):
        """Test report includes actionable recommendations."""
        orchestrator = PromptEnhancementOrchestrator()
        report = orchestrator.generate_enhancement_report()

        assert len(report.recommendations) > 0
        assert any("regression" in rec.lower() for rec in report.recommendations)
        assert any("enhancement" in rec.lower() or "apply" in rec.lower() for rec in report.recommendations)

    def test_format_enhancement_for_documentation(self):
        """Test formatting enhancement for docs."""
        orchestrator = PromptEnhancementOrchestrator()

        enhancement = PromptEnhancement(
            type=EnhancementType.RULE,
            section="TEST SECTION",
            current_text="Current text",
            enhanced_text="Enhanced text",
            rationale="Test rationale",
            impact="high",
        )

        formatted = orchestrator.format_enhancement_for_documentation(enhancement)

        assert "TEST SECTION" in formatted
        assert "Current text" in formatted
        assert "Enhanced text" in formatted
        assert "Test rationale" in formatted
        assert "high" in formatted.lower()

    def test_format_report_for_documentation(self):
        """Test formatting report for documentation."""
        orchestrator = PromptEnhancementOrchestrator()
        report = orchestrator.generate_enhancement_report()

        formatted = orchestrator.format_report_for_documentation(report)

        assert "Phase 48 S5" in formatted
        assert "Prompt Enhancement" in formatted
        assert "Agent Enhancement" in formatted
        assert str(len(report.prompt_enhancements)) in formatted
        assert str(len(report.agent_enhancements)) in formatted

    def test_enhancement_types_variety(self):
        """Test enhancements use variety of types."""
        orchestrator = PromptEnhancementOrchestrator()
        enhancements = orchestrator.identify_enhancements()

        types = [e.type for e in enhancements]

        # Should have multiple enhancement types
        unique_types = set(types)
        assert len(unique_types) >= 2

    def test_all_enhancements_have_impact(self):
        """Test all enhancements specify impact level."""
        orchestrator = PromptEnhancementOrchestrator()

        prompt_enhancements = orchestrator.identify_enhancements()
        agent_enhancements = orchestrator.identify_agent_enhancements()

        for e in prompt_enhancements:
            assert e.impact in ["low", "medium", "high"]

        for e in agent_enhancements:
            assert e.impact in ["low", "medium", "high"]

    def test_enhancement_rationale_quality(self):
        """Test enhancements have clear rationale."""
        orchestrator = PromptEnhancementOrchestrator()
        enhancements = orchestrator.identify_enhancements()

        for enhancement in enhancements:
            # Rationale should reference phase/stage learnings
            assert len(enhancement.rationale) > 10
            assert any(
                phrase in enhancement.rationale.lower()
                for phrase in ["s1", "s2", "s3", "s4", "phase 48", "showed"]
            )

    def test_orchestrator_api_completeness(self):
        """Test orchestrator has all required methods."""
        orchestrator = PromptEnhancementOrchestrator()

        assert hasattr(orchestrator, "identify_enhancements")
        assert callable(orchestrator.identify_enhancements)
        assert hasattr(orchestrator, "identify_agent_enhancements")
        assert callable(orchestrator.identify_agent_enhancements)
        assert hasattr(orchestrator, "generate_enhancement_report")
        assert callable(orchestrator.generate_enhancement_report)
        assert hasattr(orchestrator, "format_enhancement_for_documentation")
        assert callable(orchestrator.format_enhancement_for_documentation)
        assert hasattr(orchestrator, "format_report_for_documentation")
        assert callable(orchestrator.format_report_for_documentation)

    def test_enhancements_are_actionable(self):
        """Test enhancements are specific and actionable."""
        orchestrator = PromptEnhancementOrchestrator()
        enhancements = orchestrator.identify_enhancements()

        for enhancement in enhancements:
            # Should have clear before/after
            assert len(enhancement.current_text) > 0
            assert len(enhancement.enhanced_text) > 0
            assert enhancement.enhanced_text != enhancement.current_text

    def test_agent_enhancements_reference_files(self):
        """Test agent enhancements reference existing agent files."""
        orchestrator = PromptEnhancementOrchestrator()
        agent_enhancements = orchestrator.identify_agent_enhancements()

        for enh in agent_enhancements:
            # Should have valid agent file path
            assert enh.agent_file.startswith("agents/")
            assert enh.agent_file.endswith(".yaml")
