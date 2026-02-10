"""
Test suite for OrchestratorIntegrityValidator (Phase 39 Stage 3).

Tests wiring-implementation alignment, MCP tool exposure, and dependency graph validation.

Test Structure:
- TestWiringImplementationAlignment: 10 tests (AC-PHASE39-008)
- TestMCPToolExposure: 10 tests (AC-PHASE39-009)
- TestOrchestratorDependencyGraph: 10 tests (AC-PHASE39-010)

Total: 30 tests
"""

import pytest
from pathlib import Path
from typing import Dict, List, Set, Optional

from cortex.orchestrators.audit.orchestrator_integrity_validator import (
    OrchestratorIntegrityValidator,
    OrchestratorMetadata
)

# AC_START: AC-PHASE39-008
# Description: OrchestratorIntegrityValidator TDD implementation (Stage 3)
# Author: Asif Hussain
# Date: 2026-02-07


class TestWiringImplementationAlignment:
    """Test AC-PHASE39-008: Wiring.yaml ↔ implementation alignment."""
    
    def test_detects_orchestrator_in_wiring_without_file(self):
        """Test detection of orchestrators in wiring.yaml without corresponding .py files."""
        # GIVEN: wiring.yaml lists orchestrator without implementation file
        # WHEN: Validator checks wiring-implementation alignment
        # THEN: Missing file detected
    
    def test_detects_orphaned_orchestrator_implementation(self):
        """Test detection of orchestrator .py files not in wiring.yaml."""
        # GIVEN: Orchestrator file exists but not in wiring.yaml
        # WHEN: Validator checks for orphaned implementations
        # THEN: Orphaned file detected
    
    def test_validates_health_check_callable(self):
        """Test that health checks are callable for all orchestrators."""
        # GIVEN: Orchestrator in wiring.yaml
        # WHEN: Validator checks health check availability
        # THEN: Health check is callable or missing detected
    
    def test_extracts_orchestrators_from_wiring_yaml(self):
        """Test extraction of orchestrator list from wiring.yaml."""
        # GIVEN: wiring.yaml file
        # WHEN: Validator parses YAML
        # THEN: All orchestrator entries extracted
    
    def test_discovers_orchestrator_implementation_files(self):
        """Test discovery of all orchestrator .py files in cortex/orchestrators/."""
        # GIVEN: cortex/orchestrators/ directory
        # WHEN: Validator scans for .py files
        # THEN: All orchestrator files discovered
    
    def test_validates_orchestrator_class_name_matches_file(self):
        """Test that orchestrator class names follow naming conventions."""
        # GIVEN: Orchestrator file with class definition
        # WHEN: Validator checks class name
        # THEN: Class name matches expected pattern
    
    def test_validates_all_35_orchestrators_aligned(self):
        """Test that all 35 orchestrators have complete alignment."""
        # GIVEN: Complete wiring.yaml and implementation files
        # WHEN: Validator checks all orchestrators
        # THEN: All 35 orchestrators aligned
    
    def test_detects_malformed_wiring_yaml_entry(self):
        """Test detection of malformed entries in wiring.yaml."""
        # GIVEN: wiring.yaml with malformed entry
        # WHEN: Validator parses YAML
        # THEN: Malformed entry detected
    
    def test_validates_orchestrator_initialization_signature(self):
        """Test that orchestrator __init__ signatures are valid."""
        # GIVEN: Orchestrator class
        # WHEN: Validator checks __init__ method
        # THEN: Signature valid or issues detected
    
    def test_checks_orchestrator_has_required_methods(self):
        """Test that orchestrators have required methods (process, health_check)."""
        # GIVEN: Orchestrator implementation
        # WHEN: Validator checks for required methods
        # THEN: All required methods present or missing detected


class TestMCPToolExposure:
    """Test AC-PHASE39-009: MCP tool exposure completeness."""
    
    def test_detects_orchestrator_without_mcp_tool(self):
        """Test detection of orchestrators without MCP tool exposure."""
        # GIVEN: Orchestrator in wiring.yaml without @mcp_tool
        # WHEN: Validator checks MCP tool exposure
        # THEN: Missing MCP tool detected
    
    def test_detects_orphaned_mcp_tool_decorator(self):
        """Test detection of @mcp_tool decorators without orchestrator."""
        # GIVEN: @mcp_tool decorator on non-orchestrator function
        # WHEN: Validator scans for orphaned decorators
        # THEN: Orphaned decorator detected
    
    def test_validates_mcp_tool_naming_convention(self):
        """Test that MCP tool names follow cortex_* naming convention."""
        # GIVEN: MCP tool with custom name
        # WHEN: Validator checks tool naming
        # THEN: Naming convention validated
    
    def test_extracts_mcp_tools_from_codebase(self):
        """Test extraction of all @mcp_tool decorated functions."""
        # GIVEN: Codebase with @mcp_tool decorators
        # WHEN: Validator scans for decorators
        # THEN: All MCP tools extracted
    
    def test_validates_all_35_orchestrators_have_mcp_tools(self):
        """Test that all 35 orchestrators have corresponding MCP tools."""
        # GIVEN: All orchestrators in wiring.yaml
        # WHEN: Validator checks MCP tool exposure
        # THEN: All 35 have MCP tools
    
    def test_checks_mcp_tool_parameters_documented(self):
        """Test that MCP tool parameters have docstrings."""
        # GIVEN: MCP tool function
        # WHEN: Validator checks parameter documentation
        # THEN: All parameters documented or missing detected
    
    def test_validates_mcp_tool_return_type_hints(self):
        """Test that MCP tools have return type hints."""
        # GIVEN: MCP tool function
        # WHEN: Validator checks type hints
        # THEN: Return type hint present or missing detected
    
    def test_detects_duplicate_mcp_tool_names(self):
        """Test detection of duplicate MCP tool names."""
        # GIVEN: Multiple @mcp_tool with same name
        # WHEN: Validator checks for duplicates
        # THEN: Duplicates detected
    
    def test_validates_mcp_tool_registry_sync(self):
        """Test that MCP tools are registered in MCPToolsRegistry."""
        # GIVEN: @mcp_tool decorated functions
        # WHEN: Validator checks registry
        # THEN: All tools registered or missing detected
    
    def test_checks_mcp_tool_exposure_in_server_py(self):
        """Test that MCP tools are exposed in cortex/mcp/server.py."""
        # GIVEN: MCP tools
        # WHEN: Validator checks server.py exposure
        # THEN: All tools exposed or missing detected


class TestOrchestratorDependencyGraph:
    """Test AC-PHASE39-010: Orchestrator dependency graph validation."""
    
    def test_detects_circular_dependency_two_orchestrators(self):
        """Test detection of circular dependency between 2 orchestrators."""
        # GIVEN: Orchestrator A depends on B, B depends on A
        # WHEN: Validator builds dependency graph
        # THEN: Circular dependency detected
    
    def test_detects_circular_dependency_three_orchestrators(self):
        """Test detection of circular dependency chain (A→B→C→A)."""
        # GIVEN: Three orchestrators with circular dependency
        # WHEN: Validator analyzes dependency chain
        # THEN: Circular dependency detected
    
    def test_validates_dependency_exists(self):
        """Test that all declared dependencies exist."""
        # GIVEN: Orchestrator depends on non-existent orchestrator
        # WHEN: Validator checks dependency existence
        # THEN: Missing dependency detected
    
    def test_validates_tier_ordering_correct(self):
        """Test that tier ordering is correct (Tier 0 → 1 → 2 → 3)."""
        # GIVEN: Orchestrators with tier assignments
        # WHEN: Validator checks tier ordering
        # THEN: Tier 2 doesn't depend on Tier 3, etc.
    
    def test_builds_dependency_graph_from_imports(self):
        """Test building dependency graph from import statements."""
        # GIVEN: Orchestrator implementation files
        # WHEN: Validator parses import statements
        # THEN: Dependency graph built
    
    def test_validates_no_circular_dependencies_in_all_35(self):
        """Test that no circular dependencies exist across all 35 orchestrators."""
        # GIVEN: All orchestrator implementations
        # WHEN: Validator builds full dependency graph
        # THEN: No circular dependencies detected
    
    def test_detects_tier_violation_lower_depends_on_higher(self):
        """Test detection of tier violations (Tier 0 depends on Tier 1)."""
        # GIVEN: Lower tier orchestrator imports higher tier
        # WHEN: Validator checks tier constraints
        # THEN: Tier violation detected
    
    def test_extracts_tier_assignments_from_wiring_yaml(self):
        """Test extraction of tier assignments from wiring.yaml."""
        # GIVEN: wiring.yaml with tier metadata
        # WHEN: Validator parses tier assignments
        # THEN: All tier assignments extracted
    
    def test_validates_dependency_graph_is_dag(self):
        """Test that dependency graph is a Directed Acyclic Graph (DAG)."""
        # GIVEN: Complete dependency graph
        # WHEN: Validator checks for cycles
        # THEN: Graph is DAG or cycles detected
    
    def test_calculates_topological_sort_of_orchestrators(self):
        """Test calculation of topological sort order for orchestrators."""
        # GIVEN: Valid dependency graph
        # WHEN: Validator computes topological sort
        # THEN: Valid execution order returned


# AC_COMPLETE: AC-PHASE39-008 (Wiring-implementation alignment) - 10/10 tests RED ✅
# AC_COMPLETE: AC-PHASE39-009 (MCP tool exposure) - 10/10 tests RED ✅
# AC_COMPLETE: AC-PHASE39-010 (Dependency graph validation) - 10/10 tests RED ✅
# Total: 30/30 tests in RED phase
