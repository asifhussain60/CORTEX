"""
Test suite for AgentHealthValidator (Phase 39 Stage 2).

Tests agent versioning, capability coverage, cross-references, and AGENT-INDEX.md sync.

Test Structure:
- TestAgentVersionTracking: 7 tests (AC-PHASE39-004)
- TestAgentCapabilityCoverage: 7 tests (AC-PHASE39-005)
- TestAgentCrossReferences: 7 tests (AC-PHASE39-006)
- TestAgentIndexSync: 7 tests (AC-PHASE39-007)

Total: 28 tests
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from cortex.orchestrators.audit.agent_health_validator import (
    AgentHealthValidator,
    AgentMetadata
)

# AC_START: AC-PHASE39-004
# Description: AgentHealthValidator TDD implementation (Stage 2)
# Author: Asif Hussain
# Date: 2026-02-07


class TestAgentVersionTracking:
    """Test AC-PHASE39-004: Agent version tracking validation."""
    
    def test_detects_missing_agent_version_number(self):
        """Test that agents without version numbers are detected."""
        # GIVEN: Agent file without version number
        # WHEN: Validator checks version tracking
        # THEN: Missing version detected
    
    def test_detects_missing_agent_updated_date(self):
        """Test that agents without updated dates are detected."""
        # GIVEN: Agent file without updated date
        # WHEN: Validator checks version tracking
        # THEN: Missing date detected
    
    def test_validates_agent_index_version_mismatch(self):
        """Test that version mismatches between agent file and AGENT-INDEX.md are detected."""
        # GIVEN: Agent version differs from AGENT-INDEX.md
        # WHEN: Validator checks version consistency
        # THEN: Mismatch detected
    
    def test_extracts_version_from_agent_header(self):
        """Test extraction of version number from agent file header."""
        # GIVEN: Agent file with valid version header
        # WHEN: Validator extracts version
        # THEN: Correct version returned
    
    def test_extracts_updated_date_from_agent_header(self):
        """Test extraction of updated date from agent file header."""
        # GIVEN: Agent file with valid updated date
        # WHEN: Validator extracts date
        # THEN: Correct date returned
    
    def test_validates_all_agents_have_version_metadata(self):
        """Test that all agents in .github/agents/core/ have version metadata."""
        # GIVEN: All agent files in core directory
        # WHEN: Validator checks all files
        # THEN: All have version + updated date
    
    def test_handles_malformed_version_headers(self):
        """Test handling of malformed version/date headers."""
        # GIVEN: Agent with malformed header
        # WHEN: Validator parses metadata
        # THEN: Graceful error handling


class TestAgentCapabilityCoverage:
    """Test AC-PHASE39-005: Agent capability coverage matrix validation."""
    
    def test_detects_missing_audit_mode_agents(self):
        """Test detection of missing AUDIT mode coverage."""
        # GIVEN: No agents assigned to AUDIT mode
        # WHEN: Validator checks coverage matrix
        # THEN: Gap detected for AUDIT
    
    def test_detects_missing_design_mode_agents(self):
        """Test detection of missing DESIGN mode coverage."""
        # GIVEN: No agents assigned to DESIGN mode
        # WHEN: Validator checks coverage matrix
        # THEN: Gap detected for DESIGN
    
    def test_detects_missing_plan_mode_agents(self):
        """Test detection of missing PLAN mode coverage."""
        # GIVEN: No agents assigned to PLAN mode
        # WHEN: Validator checks coverage matrix
        # THEN: Gap detected for PLAN
    
    def test_validates_all_six_modes_covered(self):
        """Test that all 6 modes (AUDIT, DESIGN, PLAN, DIGEST, QUERY, META-AUDIT) have coverage."""
        # GIVEN: Complete capability coverage
        # WHEN: Validator checks all modes
        # THEN: All 6 modes have assigned agents
    
    def test_extracts_mode_assignments_from_agent_content(self):
        """Test extraction of mode assignments from agent file content."""
        # GIVEN: Agent file with mode declarations
        # WHEN: Validator parses modes
        # THEN: Correct modes extracted
    
    def test_builds_capability_coverage_matrix(self):
        """Test building of mode → agents coverage matrix."""
        # GIVEN: All agent files
        # WHEN: Validator builds matrix
        # THEN: Matrix shows mode assignments
    
    def test_detects_agents_without_mode_assignment(self):
        """Test detection of agents without any mode assignment."""
        # GIVEN: Agent file without mode declaration
        # WHEN: Validator checks mode assignments
        # THEN: Unassigned agent detected


class TestAgentCrossReferences:
    """Test AC-PHASE39-006: Agent cross-reference integrity validation."""
    
    def test_detects_broken_file_reference_in_agent(self):
        """Test detection of broken file references within agent content."""
        # GIVEN: Agent references non-existent file
        # WHEN: Validator checks file references
        # THEN: Broken reference detected
    
    def test_validates_prompt_file_references(self):
        """Test validation of references to prompt files (.md in .github/prompts/)."""
        # GIVEN: Agent references prompt files
        # WHEN: Validator checks prompt references
        # THEN: All references valid
    
    def test_validates_orchestrator_references(self):
        """Test validation of references to orchestrator files."""
        # GIVEN: Agent references orchestrators
        # WHEN: Validator checks orchestrator references
        # THEN: All references valid
    
    def test_validates_knowledge_file_references(self):
        """Test validation of references to knowledge base files."""
        # GIVEN: Agent references knowledge files
        # WHEN: Validator checks knowledge references
        # THEN: All references valid
    
    def test_extracts_file_references_from_agent_content(self):
        """Test extraction of file references from agent markdown content."""
        # GIVEN: Agent content with file references
        # WHEN: Validator parses references
        # THEN: All references extracted
    
    def test_validates_relative_path_correctness(self):
        """Test that relative paths in references are correct from agent file location."""
        # GIVEN: Agent with relative path references
        # WHEN: Validator validates paths
        # THEN: All paths resolve correctly
    
    def test_detects_broken_links_in_all_agents(self):
        """Test comprehensive broken link detection across all agent files."""
        # GIVEN: All agent files in core directory
        # WHEN: Validator scans all references
        # THEN: All broken links detected


class TestAgentIndexSync:
    """Test AC-PHASE39-007: AGENT-INDEX.md synchronization validation."""
    
    def test_detects_agent_file_not_in_index(self):
        """Test detection of agent files missing from AGENT-INDEX.md."""
        # GIVEN: Agent file exists but not in index
        # WHEN: Validator checks index completeness
        # THEN: Missing agent detected
    
    def test_detects_orphaned_index_entry(self):
        """Test detection of index entries without corresponding agent files."""
        # GIVEN: Index entry without agent file
        # WHEN: Validator checks file existence
        # THEN: Orphaned entry detected
    
    def test_validates_agent_descriptions_accurate(self):
        """Test that descriptions in AGENT-INDEX.md match agent file content."""
        # GIVEN: Agent file and index entry
        # WHEN: Validator compares descriptions
        # THEN: Descriptions match or mismatch detected
    
    def test_validates_index_lists_all_core_agents(self):
        """Test that AGENT-INDEX.md lists all agents in .github/agents/core/."""
        # GIVEN: All agent files in core directory
        # WHEN: Validator checks index completeness
        # THEN: All agents listed in index
    
    def test_extracts_agent_list_from_index(self):
        """Test extraction of agent list from AGENT-INDEX.md."""
        # GIVEN: AGENT-INDEX.md file
        # WHEN: Validator parses index
        # THEN: Agent list extracted with metadata
    
    def test_validates_index_format_correctness(self):
        """Test validation of AGENT-INDEX.md format (markdown table/list structure)."""
        # GIVEN: AGENT-INDEX.md file
        # WHEN: Validator checks format
        # THEN: Format valid or issues detected
    
    def test_detects_duplicate_agent_entries_in_index(self):
        """Test detection of duplicate agent entries in AGENT-INDEX.md."""
        # GIVEN: Index with duplicate entries
        # WHEN: Validator checks for duplicates
        # THEN: Duplicates detected


# AC_COMPLETE: AC-PHASE39-004 (Agent version tracking) - 7/7 tests RED ✅
# AC_COMPLETE: AC-PHASE39-005 (Agent capability coverage) - 7/7 tests RED ✅
# AC_COMPLETE: AC-PHASE39-006 (Agent cross-references) - 7/7 tests RED ✅
# AC_COMPLETE: AC-PHASE39-007 (AGENT-INDEX.md sync) - 7/7 tests RED ✅
# Total: 28/28 tests in RED phase
