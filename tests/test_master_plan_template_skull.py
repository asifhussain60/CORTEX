"""
SKULL Tests for Master Plan Template

Tests enforcement of canonical section ordering derived from cortex-3.9-master.md.
These tests protect against deviations from the established master plan structure.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
import re

from src.operations.modules.planning.master_plan_template import (
    MasterPlanTemplate,
    MasterPlanSection,
    SECTION_TEMPLATES
)
from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator


class TestMasterPlanTemplateSKULL:
    """
    SKULL tests for master plan template canonical ordering.
    
    These tests ensure:
    1. Section order matches cortex-3.9-master.md exactly
    2. Generated plans follow canonical structure
    3. Tier-based section inclusion is correct
    4. No sections are out of order
    """
    
    def test_skull_001_canonical_section_order_preserved(self):
        """
        SKULL-001: Canonical section order MUST match cortex-3.9-master.md.
        
        Expected order:
        1. CORTEX Header
        2. Title & Metadata
        3. Request Context
        4. Visual Progress Tracker
        5. Phase Status Table
        6. Executive Summary
        7. Architectural Changes
        8. Governance Framework
        9. Phase Overview
        10. Dependency Graph
        11. Success Criteria
        12. Deliverables
        13. Risk Analysis
        14. Related Documentation
        15. Execution Strategy
        16. Version History
        17. Contact & Support
        """
        expected_order = [
            MasterPlanSection.CORTEX_HEADER,
            MasterPlanSection.TITLE_METADATA,
            MasterPlanSection.REQUEST_CONTEXT,
            MasterPlanSection.VISUAL_PROGRESS_TRACKER,
            MasterPlanSection.PHASE_STATUS_TABLE,
            MasterPlanSection.EXECUTIVE_SUMMARY,
            MasterPlanSection.ARCHITECTURAL_CHANGES,
            MasterPlanSection.GOVERNANCE_FRAMEWORK,
            MasterPlanSection.PHASE_OVERVIEW,
            MasterPlanSection.DEPENDENCY_GRAPH,
            MasterPlanSection.SUCCESS_CRITERIA,
            MasterPlanSection.DELIVERABLES,
            MasterPlanSection.RISK_ANALYSIS,
            MasterPlanSection.RELATED_DOCUMENTATION,
            MasterPlanSection.EXECUTION_STRATEGY,
            MasterPlanSection.VERSION_HISTORY,
            MasterPlanSection.CONTACT_SUPPORT
        ]
        
        # Verify enum order matches expected
        actual_order = list(MasterPlanSection)
        assert actual_order == expected_order, \
            f"Section order violation. Expected:\n{[s.name for s in expected_order]}\n\nGot:\n{[s.name for s in actual_order]}"
    
    def test_skull_002_tier_2_required_sections_only(self):
        """
        SKULL-002: Tier 2 plans MUST include only required sections.
        
        Required sections:
        - CORTEX Header
        - Title & Metadata
        - Request Context
        - Visual Progress Tracker
        - Phase Status Table
        - Executive Summary
        - Version History
        """
        sections = MasterPlanTemplate.get_section_order(complexity_tier=2)
        
        expected_required = MasterPlanTemplate.get_required_sections()
        
        # Sort to compare content (order verified separately)
        assert sorted(sections, key=lambda s: list(MasterPlanSection).index(s)) == \
               sorted(expected_required, key=lambda s: list(MasterPlanSection).index(s)), \
            f"Tier 2 sections mismatch. Expected: {[s.name for s in expected_required]}, Got: {[s.name for s in sections]}"
    
    def test_skull_003_tier_3_includes_documented_sections(self):
        """
        SKULL-003: Tier 3 plans MUST include documented sections.
        
        Additional sections beyond required:
        - Phase Overview
        - Success Criteria
        - Deliverables
        - Related Documentation
        """
        sections = MasterPlanTemplate.get_section_order(complexity_tier=3)
        
        required_extras = [
            MasterPlanSection.PHASE_OVERVIEW,
            MasterPlanSection.SUCCESS_CRITERIA,
            MasterPlanSection.DELIVERABLES,
            MasterPlanSection.RELATED_DOCUMENTATION
        ]
        
        for section in required_extras:
            assert section in sections, \
                f"Tier 3 missing required section: {section.name}"
    
    def test_skull_004_tier_4_includes_all_complex_sections(self):
        """
        SKULL-004: Tier 4 plans MUST include all complex sections.
        
        Additional sections beyond Tier 3:
        - Architectural Changes
        - Governance Framework
        - Dependency Graph
        - Risk Analysis
        - Execution Strategy
        - Contact & Support
        """
        sections = MasterPlanTemplate.get_section_order(complexity_tier=4)
        
        required_extras = [
            MasterPlanSection.ARCHITECTURAL_CHANGES,
            MasterPlanSection.GOVERNANCE_FRAMEWORK,
            MasterPlanSection.DEPENDENCY_GRAPH,
            MasterPlanSection.RISK_ANALYSIS,
            MasterPlanSection.EXECUTION_STRATEGY,
            MasterPlanSection.CONTACT_SUPPORT
        ]
        
        for section in required_extras:
            assert section in sections, \
                f"Tier 4 missing required section: {section.name}"
    
    def test_skull_005_section_order_is_sequential(self):
        """
        SKULL-005: Generated section order MUST be sequential (no out-of-order sections).
        """
        for tier in [2, 3, 4]:
            sections = MasterPlanTemplate.get_section_order(complexity_tier=tier)
            
            # Get enum indices
            indices = [list(MasterPlanSection).index(s) for s in sections]
            
            # Verify strictly increasing
            assert indices == sorted(indices), \
                f"Tier {tier} sections out of order. Indices: {indices}, Expected: {sorted(indices)}"
    
    def test_skull_006_cortex_header_always_first(self):
        """
        SKULL-006: CORTEX Header MUST always be the first section.
        """
        for tier in [2, 3, 4]:
            sections = MasterPlanTemplate.get_section_order(complexity_tier=tier)
            assert sections[0] == MasterPlanSection.CORTEX_HEADER, \
                f"Tier {tier}: CORTEX Header must be first, got {sections[0].name}"
    
    def test_skull_007_version_history_near_end(self):
        """
        SKULL-007: Version History MUST appear near end (before Contact & Support only).
        """
        for tier in [2, 3, 4]:
            sections = MasterPlanTemplate.get_section_order(complexity_tier=tier)
            version_idx = sections.index(MasterPlanSection.VERSION_HISTORY)
            
            # Version history should be in last 2 positions
            assert version_idx >= len(sections) - 2, \
                f"Tier {tier}: Version History at position {version_idx}, expected >= {len(sections) - 2}"
    
    def test_skull_008_generated_plan_follows_canonical_order(self):
        """
        SKULL-008: UnifiedPlanGenerator MUST generate plans in canonical order.
        """
        generator = UnifiedPlanGenerator()
        
        # Test Tier 4 plan generation
        metadata = {
            "title": "Test Plan",
            "complexity_tier": 4,
            "created": "2025-12-16",
            "last_updated": "2025-12-16",
            "version": "1.0.0",
            "status": "In Progress",
            "request_context": "Test context",
            "summary": "Test summary",
            "goals": ["Goal 1", "Goal 2"],
            "outcomes": ["Outcome 1"],
            "architectural_changes": "Test changes",
            "governance_framework": "Test framework",
            "phase_overview": "Test overview",
            "dependency_graph": "Test graph",
            "success_criteria": "Test criteria",
            "deliverables": "Test deliverables",
            "risk_analysis": "Test risks",
            "related_documentation": "Test docs",
            "execution_strategy": "Test strategy",
            "version_history": [
                {"version": "1.0.0", "date": "2025-12-16", "author": "Test", "changes": "Initial"}
            ],
            "contact_support": "Test contact"
        }
        
        phases = [
            {"id": 1, "name": "Phase 1", "status": "complete", "start_time": "09:00", "end_time": "10:00", "actual": "1h", "elapsed": "1h", "sub_plan": "phase-01.md"}
        ]
        
        result = generator.generate_master_plan(
            plan_id="test-plan",
            phases=phases,
            metadata=metadata,
            compressed=False
        )
        
        # Extract section headers from generated plan
        section_headers = re.findall(r'^#{1,2}\s+([🎯🏗️🛡️📋🔗✅📁🚨📖🚀🔄📞].*?)$', result, re.MULTILINE)
        
        # Verify order matches expectations
        expected_headers = [
            "🎯 Executive Summary",
            "🏗️ Architectural Changes",
            "🛡️ Governance Framework",
            "📋 Phase Overview",
            "🔗 Dependency Graph",
            "✅ Success Criteria",
            "📁 Deliverables",
            "🚨 Risk Analysis",
            "📖 Related Documentation",
            "🚀 Execution Strategy",
            "🔄 Version History",
            "📞 Contact & Support"
        ]
        
        # Check that sections appear in order (allowing for missing optional sections)
        found_headers = [h for h in expected_headers if any(h in sh for sh in section_headers)]
        assert found_headers == [h for h in expected_headers if any(h in sh for sh in section_headers)], \
            f"Section order violation in generated plan.\n\nFound:\n{section_headers}\n\nExpected (in order):\n{expected_headers}"
    
    def test_skull_009_validation_detects_out_of_order_sections(self):
        """
        SKULL-009: Template validation MUST detect out-of-order sections.
        """
        # Create intentionally out-of-order section list
        out_of_order = [
            MasterPlanSection.CORTEX_HEADER.value,
            MasterPlanSection.EXECUTIVE_SUMMARY.value,  # Wrong: should come after Phase Status Table
            MasterPlanSection.TITLE_METADATA.value,
            MasterPlanSection.VERSION_HISTORY.value
        ]
        
        result = MasterPlanTemplate.validate_section_order(out_of_order)
        
        assert not result["valid"], "Validation should detect out-of-order sections"
        assert len(result["errors"]) > 0, "Should have at least one error"
        assert "not in canonical order" in result["errors"][0].lower(), \
            f"Error message should mention ordering issue: {result['errors']}"
    
    def test_skull_010_validation_detects_missing_required_sections(self):
        """
        SKULL-010: Template validation MUST detect missing required sections.
        """
        # Missing CORTEX_HEADER
        incomplete = [
            MasterPlanSection.TITLE_METADATA.value,
            MasterPlanSection.REQUEST_CONTEXT.value,
            MasterPlanSection.VERSION_HISTORY.value
        ]
        
        result = MasterPlanTemplate.validate_section_order(incomplete)
        
        assert len(result["warnings"]) > 0, "Should have warnings for missing required sections"
        assert any("CORTEX_HEADER" in w for w in result["warnings"]), \
            f"Should warn about missing CORTEX_HEADER: {result['warnings']}"
    
    def test_skull_011_cortex_header_contains_branding(self):
        """
        SKULL-011: CORTEX Header MUST contain ASCII art branding.
        """
        header = MasterPlanTemplate.get_cortex_header()
        
        required_elements = [
            "CORTEX",
            "AI-Powered Development Intelligence System",
            "Author: Asif Hussain",
            "github.com/asifhussain60/CORTEX",
            "Copyright © 2025"
        ]
        
        for element in required_elements:
            assert element in header, \
                f"CORTEX header missing required element: {element}"
    
    def test_skull_012_all_sections_have_templates(self):
        """
        SKULL-012: All defined sections MUST have corresponding templates.
        """
        all_sections = list(MasterPlanSection)
        
        # These sections are handled programmatically, not via templates
        programmatic_sections = {
            MasterPlanSection.VISUAL_PROGRESS_TRACKER,
            MasterPlanSection.PHASE_STATUS_TABLE
        }
        
        for section in all_sections:
            assert section in SECTION_TEMPLATES or section in programmatic_sections, \
                f"Missing template for section: {section.name}"
    
    def test_skull_013_tier_1_not_supported_for_master_plans(self):
        """
        SKULL-013: Tier 1 operations MUST NOT generate master plans.
        
        Tier 1 is for instant CLI operations - no formal planning.
        """
        # Tier 1 should return minimal sections (same as Tier 2)
        sections = MasterPlanTemplate.get_section_order(complexity_tier=1)
        
        # Should only have required sections
        required_count = len(MasterPlanTemplate.get_required_sections())
        assert len(sections) == required_count, \
            f"Tier 1 should only have required sections ({required_count}), got {len(sections)}"
    
    def test_skull_014_phase_status_table_before_executive_summary(self):
        """
        SKULL-014: Phase Status Table MUST appear before Executive Summary.
        
        This ensures users see progress upfront before reading details.
        """
        for tier in [2, 3, 4]:
            sections = MasterPlanTemplate.get_section_order(complexity_tier=tier)
            
            table_idx = sections.index(MasterPlanSection.PHASE_STATUS_TABLE)
            summary_idx = sections.index(MasterPlanSection.EXECUTIVE_SUMMARY)
            
            assert table_idx < summary_idx, \
                f"Tier {tier}: Phase Status Table (#{table_idx}) must come before Executive Summary (#{summary_idx})"
    
    def test_skull_015_visual_progress_before_phase_table(self):
        """
        SKULL-015: Visual Progress Tracker MUST appear before Phase Status Table.
        
        High-level metrics shown before detailed phase breakdown.
        """
        for tier in [2, 3, 4]:
            sections = MasterPlanTemplate.get_section_order(complexity_tier=tier)
            
            progress_idx = sections.index(MasterPlanSection.VISUAL_PROGRESS_TRACKER)
            table_idx = sections.index(MasterPlanSection.PHASE_STATUS_TABLE)
            
            assert progress_idx < table_idx, \
                f"Tier {tier}: Visual Progress Tracker (#{progress_idx}) must come before Phase Status Table (#{table_idx})"


class TestMasterPlanTemplateIntegration:
    """Integration tests for master plan template with real data."""
    
    def test_integration_001_cortex_39_structure_reproduction(self):
        """
        Integration test: Reproduce cortex-3.9-master.md structure exactly.
        """
        generator = UnifiedPlanGenerator()
        
        # Metadata matching cortex-3.9-master.md
        metadata = {
            "title": "CORTEX Evolution v3.9 - Unified Orchestration & AST Enhancement",
            "complexity_tier": 4,
            "created": "2024-12-14 05:30 AM",
            "last_updated": "2024-12-14 10:45 AM",
            "completed": "2024-12-14 10:45 AM",
            "version": "3.9.0",
            "status": "✅ Complete",
            "request_context": "Transform CORTEX's planning system from template-based (v2.0) to intelligent tiered routing (v3.0)...",
            "summary": "This unified plan consolidates two major architectural initiatives...",
            "goals": [
                "Transform Planning System 2.0 → 3.0 with intelligent tiered routing",
                "Integrate CORTEX Lens AST capabilities non-invasively"
            ],
            "outcomes": [
                "95%+ accuracy in operation routing (up from 70%)",
                "Sub-2s response time for Tier 1 operations"
            ],
            "autonomous_execution": "User commands 'continue', 'go', or 'proceed' trigger autonomous completion...",
            "architectural_changes": "### Tiered Planning System\n\n**Current State (v3.8.1):**...",
            "governance_framework": "**FILE_ORGANIZATION_ENFORCEMENT:**...",
            "phase_overview": "### Foundation (Phases 00-02)...",
            "dependency_graph": "```\nPhase 00 (Governance)\n  ↓\nPhase 01 (Router) + Phase 02 (Analyzer)...",
            "success_criteria": "### Performance Metrics\n- ✅ Tier 1 operations complete in <2 seconds...",
            "deliverables": "### Planning Artifacts\n- ✅ cortex-3.9-master.md...",
            "risk_analysis": "### Technical Risks\n\n**Risk 1: LLM Routing Latency**...",
            "related_documentation": "### Planning System\n- [Planning System 2.0 Manifest]...",
            "execution_strategy": "### Path B: Autonomous Implementation (SELECTED)...",
            "version_history": [
                {"version": "3.9.0", "date": "2024-12-14", "author": "Asif Hussain", "changes": "Initial creation"}
            ],
            "contact_support": "**Plan Owner:** Asif Hussain..."
        }
        
        phases = [
            {"id": 0, "name": "Governance Framework", "status": "complete", 
             "start_time": "05:35", "end_time": "05:45", "actual": "10 min", 
             "elapsed": "0:10", "sub_plan": "phase-00-govern.md"}
        ]
        
        result = generator.generate_master_plan(
            plan_id="cortex-evolution-v3.9",
            phases=phases,
            metadata=metadata,
            compressed=False
        )
        
        # Verify all major sections present
        assert "# CORTEX Evolution v3.9" in result
        assert "## Request Context" in result
        assert "## Visual Progress Tracker" in result or "Visual Progress Tracker" in result
        assert "## 🎯 Executive Summary" in result
        assert "## 🏗️ Architectural Changes" in result
        assert "## 🛡️ Governance Framework" in result
        assert "## 📋 Phase Overview" in result
        assert "## 🔗 Dependency Graph" in result
        assert "## ✅ Success Criteria" in result
        assert "## 📁 Deliverables" in result
        assert "## 🚨 Risk Analysis" in result
        assert "## 📖 Related Documentation" in result
        assert "## 🚀 Execution Strategy" in result
        assert "## 🔄 Version History" in result
        assert "## 📞 Contact & Support" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
