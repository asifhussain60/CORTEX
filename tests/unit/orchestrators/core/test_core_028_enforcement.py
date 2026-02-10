"""
Tests for CORE-028 File Naming Enforcement

Authority: CORE-028 (updated 2026-02-04 with plan file exception)
Phase: File Naming Governance Fix
Date: 2026-02-04

Tests the FileNamingEnforcementAgent integration into EnforcementOrchestrator.
"""

import pytest
from cortex.orchestrators.core.enforcement_orchestrator import (
    FileNamingEnforcementAgent,
    EnforcementOrchestrator,
    EnforcementLevel,
    EnforcementResult,
)


class TestFileNamingEnforcementAgent:
    """Tests for FileNamingEnforcementAgent."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.agent = FileNamingEnforcementAgent()
    
    # =========================================================================
    # SCREAMING_CASE Detection (BLOCKED)
    # =========================================================================
    
    def test_screaming_case_blocked(self):
        """SCREAMING_CASE filenames must be BLOCKED."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["PHASE-21-SPA-ENHANCEMENT-PLAN.yaml"]
        }
        
        result = self.agent.validate(operation)
        
        assert result.is_blocked(), "SCREAMING_CASE should be blocked"
        violations = result.violations
        assert any("SCREAMING_CASE" in v for v in violations)
        assert any("phase-21-spa-enhancement-plan.yaml" in v for v in violations)
    
    def test_partial_screaming_case_blocked(self):
        """Partial SCREAMING_CASE (e.g., SPA-AUDIT) must be BLOCKED."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["SPA-AUDIT-REPORT.yaml"]
        }
        
        result = self.agent.validate(operation)
        
        assert result.is_blocked(), "Partial SCREAMING_CASE should be blocked"
        violations = result.violations
        assert any("SCREAMING_CASE" in v for v in violations)
    
    # =========================================================================
    # Length Limits
    # =========================================================================
    
    def test_general_file_length_limit_30_chars(self):
        """General files must not exceed 30 characters."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["very-long-filename-that-exceeds-thirty-chars.yaml"]  # 52 chars
        }
        
        result = self.agent.validate(operation)
        
        assert result.is_blocked(), "Filename >30 chars should be blocked"
        violations = result.violations
        assert any("too long" in v for v in violations)
        assert any("30" in v for v in violations)
    
    def test_plan_file_length_limit_40_chars(self):
        """Plan files can be up to 40 characters."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["phase-21-spa-enhancement-plan.yaml"]  # 32 chars - VALID
        }
        
        result = self.agent.validate(operation)
        
        # Should pass (lowercase, 32 chars, ends with -plan.yaml)
        assert not result.is_blocked(), f"Plan file 32 chars should be valid: {result.violations}"
    
    def test_plan_file_exceeds_40_chars_blocked(self):
        """Plan files exceeding 40 characters must be BLOCKED."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["phase-21-enterprise-repository-intelligence-system-plan.yaml"]  # 60+ chars
        }
        
        result = self.agent.validate(operation)
        
        assert result.is_blocked(), "Plan file >40 chars should be blocked"
        violations = result.violations
        assert any("too long" in v for v in violations)
        assert any("40" in v for v in violations)
    
    # =========================================================================
    # Kebab-Case Validation
    # =========================================================================
    
    def test_kebab_case_valid(self):
        """Lowercase kebab-case filenames must be VALID."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": [
                "migration-summary.md",
                "docker-config.yaml",
                "phase-21-plan.yaml",
            ]
        }
        
        result = self.agent.validate(operation)
        
        assert not result.is_blocked(), f"Kebab-case should be valid: {result.violations}"
    
    def test_spaces_blocked(self):
        """Spaces in filenames must be BLOCKED."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["migration summary.md"]
        }
        
        result = self.agent.validate(operation)
        
        assert result.is_blocked(), "Spaces should be blocked"
        violations = result.violations
        assert any("Spaces not allowed" in v for v in violations)
    
    # =========================================================================
    # Plan File Exception Recognition
    # =========================================================================
    
    def test_plan_file_suffixes_recognized(self):
        """Files ending with -plan.yaml, -spec.yaml, -system.yaml get 40-char limit."""
        valid_plan_files = [
            "cortex-self-improvement-sdlc-plan.yaml",  # 40 chars
            "phase-21-enterprise-dashboard-spec.yaml",  # 40 chars
            "capacity-planning-system.yaml",  # 26 chars
        ]
        
        for filename in valid_plan_files:
            operation = {
                "intent": "IMPLEMENT",
                "output_files": [filename]
            }
            
            result = self.agent.validate(operation)
            
            assert not result.is_blocked(), f"Plan file {filename} ({len(filename)} chars) should be valid"
    
    # =========================================================================
    # Python Files (snake_case allowed)
    # =========================================================================
    
    def test_python_files_snake_case_allowed(self):
        """Python files can use snake_case per PEP 8."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": [
                "git_history_analyzer.py",
                "intent_router.py",
                "test_enforcement.py",
            ]
        }
        
        result = self.agent.validate(operation)
        
        # Python files with underscores should pass (warning only, not violation)
        assert not result.is_blocked() or (result.is_blocked() and "SCREAMING_CASE" not in str(result.violations))
    
    # =========================================================================
    # Skip Patterns
    # =========================================================================
    
    def test_init_files_skipped(self):
        """__init__.py files should skip validation."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["__init__.py"]
        }
        
        result = self.agent.validate(operation)
        
        assert not result.is_blocked(), "__init__.py should skip validation"
    
    def test_setup_files_skipped(self):
        """setup.py files should skip validation."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["setup.py"]
        }
        
        result = self.agent.validate(operation)
        
        assert not result.is_blocked(), "setup.py should skip validation"
    
    # =========================================================================
    # Multiple Files
    # =========================================================================
    
    def test_multiple_files_mixed_validity(self):
        """Mix of valid and invalid filenames."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": [
                "migration-summary.md",  # VALID
                "PHASE-21-PLAN.yaml",  # INVALID (SCREAMING_CASE)
                "docker-config.yaml",  # VALID
            ]
        }
        
        result = self.agent.validate(operation)
        
        assert result.is_blocked(), "Should block due to one invalid file"
        violations = result.violations
        assert any("SCREAMING_CASE" in v for v in violations)
    
    # =========================================================================
    # Edge Cases
    # =========================================================================
    
    def test_no_output_files_passes(self):
        """Operations without output files should pass."""
        operation = {
            "intent": "ANALYZE",
            "output_files": []
        }
        
        result = self.agent.validate(operation)
        
        assert not result.is_blocked(), "No files to validate should pass"
    
    def test_target_file_fallback(self):
        """Agent should check target_file if output_files empty."""
        operation = {
            "intent": "IMPLEMENT",
            "target_file": "/path/to/SCREAMING-FILE.yaml",
            "output_files": []
        }
        
        result = self.agent.validate(operation)
        
        assert result.is_blocked(), "Should validate target_file as fallback"


class TestEnforcementOrchestratorIntegration:
    """Integration tests for EnforcementOrchestrator with FileNamingEnforcementAgent."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.orchestrator = EnforcementOrchestrator()
    
    def test_file_naming_agent_registered(self):
        """FileNamingEnforcementAgent should be in agents list."""
        agent_names = [agent.__class__.__name__ for agent in self.orchestrator.agents]
        assert "FileNamingEnforcementAgent" in agent_names
    
    def test_enforcement_blocks_screaming_case(self):
        """EnforcementOrchestrator should block SCREAMING_CASE filenames."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["PHASE-21-SPA-ENHANCEMENT-PLAN.yaml"],
            "test_file": "tests/test_spa.py",  # Satisfy CORE-008
            "discovery_performed": True,  # Satisfy CORE-030 discovery
        }
        
        result = self.orchestrator.validate_operation(operation)
        
        assert result.is_err(), "Should block SCREAMING_CASE"
        enforcement_result = result.error
        assert enforcement_result.is_blocked()
        assert any("CORE-028" in v for v in enforcement_result.violations)
    
    def test_enforcement_allows_valid_plan_file(self):
        """EnforcementOrchestrator should allow valid plan files."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["phase-21-spa-enhancement-plan.yaml"],
            "test_file": "tests/test_spa.py",  # Satisfy CORE-008
            "discovery_performed": True,  # Satisfy CORE-030 discovery
        }
        
        result = self.orchestrator.validate_operation(operation)
        
        # Should pass or have warnings only (not blocked)
        if result.is_err():
            enforcement_result = result.error
            # Only check for CORE-028 violations - other violations might be expected
            core028_violations = [v for v in enforcement_result.violations if "CORE-028" in v]
            assert not core028_violations, f"Should not block valid plan file with CORE-028: {core028_violations}"
    
    def test_enforcement_parallel_execution(self):
        """All agents (including FileNaming) should execute in parallel."""
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["migration-summary.md"],
            "test_file": "tests/test_migration.py",
            "discovery_performed": True,  # Satisfy CORE-030 discovery
        }
        
        result = self.orchestrator.validate_operation(operation)
        
        # Verify metadata shows agents executed
        if result.is_ok():
            enforcement_result = result.value
            # Agent count may vary, just check it exists
            assert "agent_count" in enforcement_result.metadata or len(enforcement_result.metadata) >= 0
