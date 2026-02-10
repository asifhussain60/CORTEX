"""
Integration tests for Phase 71: Markdown Artifact Prevention System.

Tests end-to-end workflow:
1. EnforcementOrchestrator blocks violations
2. Git pre-commit hook enforces at filesystem level
"""

import pytest
import subprocess
from pathlib import Path
from cortex.orchestrators.core.enforcement_orchestrator import (
    EnforcementOrchestrator,
    EnforcementLevel,
)


class TestPhase71MarkdownPrevention:
    """Integration tests for Phase 71 artifact prevention."""

    def test_enforcement_orchestrator_blocks_root_markdown(self):
        """EnforcementOrchestrator blocks root markdown generation."""
        orchestrator = EnforcementOrchestrator()
        
        operation = {
            "intent": "DOCUMENT",
            "output_files": ["PHASE-71-TEST-SUMMARY.md"],
        }
        
        result = orchestrator.validate_operation(operation)
        
        assert result.is_err(), "Should block root markdown file"
        enforcement_result = result.error
        assert enforcement_result.level == EnforcementLevel.BLOCKED
        # Updated assertion: Check for CORE-002 violation (not "root directory")
        assert any("CORE-002" in v for v in enforcement_result.violations), \
            f"Expected CORE-002 violation, got: {enforcement_result.violations}"

    def test_enforcement_orchestrator_blocks_docs_markdown(self):
        """EnforcementOrchestrator blocks docs/ markdown (CORE-002-SUB)."""
        orchestrator = EnforcementOrchestrator()
        
        operation = {
            "intent": "DOCUMENT",
            "output_files": ["docs/phase-71-guide.md"],
        }
        
        result = orchestrator.validate_operation(operation)
        
        # After Gap #2A fix: docs/ markdown is NO LONGER ALLOWED
        assert result.is_err(), "Should block docs/ markdown files"
        enforcement_result = result.error
        assert enforcement_result.level == EnforcementLevel.BLOCKED
        assert any("CORE-002" in v for v in enforcement_result.violations)

    def test_enforcement_orchestrator_allows_readme(self):
        """EnforcementOrchestrator allows README.md in root."""
        orchestrator = EnforcementOrchestrator()
        
        operation = {
            "intent": "DOCUMENT",
            "output_files": ["README.md"],
        }
        
        result = orchestrator.validate_operation(operation)
        
        assert result.is_ok(), "Should allow README.md"

    def test_git_hook_installed(self):
        """Verify git pre-commit hook is installed."""
        hook_path = Path(".githooks/pre-commit")
        
        assert hook_path.exists(), "Pre-commit hook should exist"
        assert hook_path.stat().st_mode & 0o111, "Hook should be executable"

    def test_git_config_uses_custom_hooks(self):
        """Verify git is configured to use .githooks directory."""
        result = subprocess.run(
            ["git", "config", "core.hooksPath"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert ".githooks" in result.stdout

    def test_multi_layer_defense(self):
        """Verify multiple prevention layers work together."""
        # Layer 1: EnforcementOrchestrator
        orchestrator = EnforcementOrchestrator()
        operation = {
            "intent": "IMPLEMENT",
            "output_files": ["SESSION-TEST.md", "docs/guide.md"],
        }
        
        result = orchestrator.validate_operation(operation)
        assert result.is_err(), "Layer 1 should block"
        
        # Layer 2: Git hook (integration test only - real hook runs on git commit)
        hook_path = Path(".githooks/pre-commit")
        assert hook_path.exists(), "Layer 2 should be active"


class TestPhase71EdgeCases:
    """Edge case testing for Phase 71."""

    def test_case_insensitive_md_extension(self):
        """Verify .MD extension (uppercase) is also blocked."""
        orchestrator = EnforcementOrchestrator()
        
        operation = {
            "intent": "DOCUMENT",
            "output_files": ["TEST-FILE.MD"],
        }
        
        result = orchestrator.validate_operation(operation)
        assert result.is_err(), "Should block .MD extension"

    def test_explicit_user_request_override(self):
        """User explicit request overrides prevention."""
        orchestrator = EnforcementOrchestrator()
        
        operation = {
            "intent": "DOCUMENT",
            "output_files": ["requested-file.md"],  # kebab-case to avoid CORE-028
            "user_explicit_request": True,
        }
        
        result = orchestrator.validate_operation(operation)
        assert result.is_ok(), "Explicit request should override"

    def test_multiple_violations_reported(self):
        """Multiple root files should report all violations."""
        orchestrator = EnforcementOrchestrator()
        
        operation = {
            "intent": "DOCUMENT",
            "output_files": [
                "PHASE-71-SUMMARY.md",
                "SESSION-COMPLETE.md",
                "AUDIT-REPORT.md",
            ],
        }
        
        result = orchestrator.validate_operation(operation)
        assert result.is_err()
        # Each file can trigger multiple violations (pattern + root)
        assert len(result.error.violations) >= 3
