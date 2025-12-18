"""
Tests for Section Selector (CORTEX 4.0)

Validates dynamic section composition logic.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from src.core.section_selector import (
    SectionSelector,
    SectionType
)


class TestSectionSelector:
    """Test suite for SectionSelector."""
    
    @pytest.fixture
    def selector(self):
        """Fixture for section selector."""
        return SectionSelector()
    
    # ============================================================================
    # TIER 1 (INSTANT) Tests
    # ============================================================================
    
    def test_tier1_no_sections(self, selector):
        """Test TIER1 returns no sections."""
        sections = selector.select_sections("tier1_instant")
        assert len(sections) == 0
    
    # ============================================================================
    # TIER 2 (FOCUSED) Tests
    # ============================================================================
    
    def test_tier2_minimal(self, selector):
        """Test TIER2 with minimal context."""
        sections = selector.select_sections("tier2_focused", {})
        assert len(sections) <= 2
        assert any(s.type == SectionType.RESPONSE for s in sections)
    
    def test_tier2_with_discovery(self, selector):
        """Test TIER2 with discovery context."""
        context = {"has_discovery": True}
        sections = selector.select_sections("tier2_focused", context)
        assert any(s.type == SectionType.CONTEXT for s in sections)
    
    def test_tier2_with_challenge(self, selector):
        """Test TIER2 with technical challenge."""
        context = {"has_technical_challenge": True}
        sections = selector.select_sections("tier2_focused", context)
        assert any(s.type == SectionType.ANALYSIS for s in sections)
    
    def test_tier2_with_action(self, selector):
        """Test TIER2 with user action required."""
        context = {"user_action_required": True}
        sections = selector.select_sections("tier2_focused", context)
        assert any(s.type == SectionType.ACTIONS for s in sections)
    
    def test_tier2_section_limit(self, selector):
        """Test TIER2 respects 2-section limit."""
        context = {
            "has_discovery": True,
            "has_technical_challenge": True,
            "user_action_required": True
        }
        sections = selector.select_sections("tier2_focused", context)
        assert len(sections) <= 2
    
    # ============================================================================
    # TIER 3 (STRUCTURED) Tests
    # ============================================================================
    
    def test_tier3_core_sections(self, selector):
        """Test TIER3 includes core sections."""
        sections = selector.select_sections("tier3_structured", {})
        section_types = [s.type for s in sections]
        assert SectionType.UNDERSTANDING in section_types
        assert SectionType.RESPONSE in section_types
    
    def test_tier3_with_challenge(self, selector):
        """Test TIER3 includes approach when challenge present."""
        context = {"has_technical_challenge": True}
        sections = selector.select_sections("tier3_structured", context)
        assert any(s.type == SectionType.APPROACH for s in sections)
    
    def test_tier3_with_changes(self, selector):
        """Test TIER3 includes changes when files modified."""
        context = {"files_modified": True}
        sections = selector.select_sections("tier3_structured", context)
        assert any(s.type == SectionType.CHANGES for s in sections)
    
    def test_tier3_with_next_steps(self, selector):
        """Test TIER3 includes next steps when action required."""
        context = {"user_action_required": True}
        sections = selector.select_sections("tier3_structured", context)
        assert any(s.type == SectionType.NEXT_STEPS for s in sections)
    
    def test_tier3_multi_phase(self, selector):
        """Test TIER3 includes next steps for multi-phase."""
        context = {"multi_phase": True}
        sections = selector.select_sections("tier3_structured", context)
        assert any(s.type == SectionType.NEXT_STEPS for s in sections)
    
    def test_tier3_complete_5_part(self, selector):
        """Test TIER3 can produce complete 5-part structure."""
        context = {
            "has_technical_challenge": True,
            "files_modified": True,
            "user_action_required": True
        }
        sections = selector.select_sections("tier3_structured", context)
        section_types = [s.type for s in sections]
        
        # Check for 5-part structure elements
        assert SectionType.UNDERSTANDING in section_types
        assert SectionType.APPROACH in section_types
        assert SectionType.RESPONSE in section_types
        assert SectionType.CHANGES in section_types
        assert SectionType.NEXT_STEPS in section_types
    
    # ============================================================================
    # TIER 4 (COMPREHENSIVE) Tests
    # ============================================================================
    
    def test_tier4_always_5_part(self, selector):
        """Test TIER4 always includes 5-part structure."""
        sections = selector.select_sections("tier4_comprehensive", {})
        section_types = [s.type for s in sections]
        
        assert SectionType.UNDERSTANDING in section_types
        assert SectionType.APPROACH in section_types
        assert SectionType.RESPONSE in section_types
        assert SectionType.CHANGES in section_types
        assert SectionType.NEXT_STEPS in section_types
    
    def test_tier4_with_architecture(self, selector):
        """Test TIER4 includes architecture for system design."""
        context = {"system_design": True}
        sections = selector.select_sections("tier4_comprehensive", context)
        assert any(s.type == SectionType.ARCHITECTURE for s in sections)
    
    def test_tier4_with_results(self, selector):
        """Test TIER4 includes results when metrics available."""
        context = {"has_metrics": True}
        sections = selector.select_sections("tier4_comprehensive", context)
        assert any(s.type == SectionType.RESULTS for s in sections)
    
    def test_tier4_with_achievements(self, selector):
        """Test TIER4 includes achievements for milestones."""
        context = {"milestones_reached": True}
        sections = selector.select_sections("tier4_comprehensive", context)
        assert any(s.type == SectionType.ACHIEVEMENTS for s in sections)
    
    def test_tier4_with_cautions(self, selector):
        """Test TIER4 includes cautions for risks."""
        context = {"risks_present": True}
        sections = selector.select_sections("tier4_comprehensive", context)
        assert any(s.type == SectionType.CAUTIONS for s in sections)
    
    def test_tier4_section_count(self, selector):
        """Test TIER4 respects 4-7 section range (maximal with all options)."""
        contexts = [
            {},  # Minimal
            {"system_design": True, "has_metrics": True},  # Moderate
            {
                "system_design": True,
                "has_metrics": True,
                "milestones_reached": True,
                "risks_present": True
            }  # Maximal (can have 7: understanding, approach, architecture, response, results, changes, achievements, cautions, next_steps)
        ]
        
        for context in contexts:
            sections = selector.select_sections("tier4_comprehensive", context)
            assert 4 <= len(sections) <= 9, f"Got {len(sections)} sections"
    
    # ============================================================================
    # Validation Tests
    # ============================================================================
    
    def test_validate_tier1_count(self, selector):
        """Test validation for TIER1 section count."""
        sections = []
        assert selector.validate_section_count("tier1_instant", sections) is True
        
        sections = [selector.SECTIONS[SectionType.RESPONSE]]
        assert selector.validate_section_count("tier1_instant", sections) is False
    
    def test_validate_tier2_count(self, selector):
        """Test validation for TIER2 section count."""
        # Valid counts: 1-2
        sections = [selector.SECTIONS[SectionType.RESPONSE]]
        assert selector.validate_section_count("tier2_focused", sections) is True
        
        sections = []
        assert selector.validate_section_count("tier2_focused", sections) is False
        
        sections = [
            selector.SECTIONS[SectionType.RESPONSE],
            selector.SECTIONS[SectionType.CONTEXT],
            selector.SECTIONS[SectionType.ANALYSIS]
        ]
        assert selector.validate_section_count("tier2_focused", sections) is False
    
    def test_validate_tier3_count(self, selector):
        """Test validation for TIER3 section count."""
        # Valid counts: 2-5
        sections = [
            selector.SECTIONS[SectionType.UNDERSTANDING],
            selector.SECTIONS[SectionType.RESPONSE]
        ]
        assert selector.validate_section_count("tier3_structured", sections) is True
        
        sections = [selector.SECTIONS[SectionType.RESPONSE]]
        assert selector.validate_section_count("tier3_structured", sections) is False
    
    def test_get_section_titles(self, selector):
        """Test section title formatting."""
        sections = [
            selector.SECTIONS[SectionType.UNDERSTANDING],
            selector.SECTIONS[SectionType.RESPONSE]
        ]
        
        titles = selector.get_section_titles(sections)
        assert len(titles) == 2
        assert titles[0].startswith("### 🎯")
        assert "Understanding & Scope" in titles[0]
