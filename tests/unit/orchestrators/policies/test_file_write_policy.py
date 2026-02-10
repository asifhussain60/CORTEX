"""
Unit tests for FileWritePolicy.

Tests markdown report detection and blocking.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 specification (AC-29-F6), CORE-002
"""

import pytest
from cortex.orchestrators.policies.file_write_policy import (
    FileWritePolicy,
    ReportIntentDetected,
    MarkdownBanViolation
)


class TestFileWritePolicyReportDetection:
    """Test report intent detection (AC-29-F6)."""
    
    def test_report_markdown_blocked(self):
        """Files matching **/report*.md are blocked."""
        policy = FileWritePolicy()
        
        blocked_paths = [
            "project-report.md",
            "_workspaces/phase-1-report.md",
            "analysis/security-report.md",
            "reports/weekly-report.md",
        ]
        
        for path in blocked_paths:
            assert policy.is_report_intent(path, ""), f"Failed to block: {path}"
    
    def test_summary_markdown_blocked(self):
        """Files matching **/summary*.md are blocked."""
        policy = FileWritePolicy()
        
        blocked_paths = [
            "summary.md",
            "phase-summary.md",
            "_workspaces/session-summary.md",
            "completion-summary.md",
        ]
        
        for path in blocked_paths:
            assert policy.is_report_intent(path, ""), f"Failed to block: {path}"
    
    def test_completion_markdown_blocked(self):
        """Files matching **/*completion*.md are blocked."""
        policy = FileWritePolicy()
        
        blocked_paths = [
            "completion.md",
            "phase-completion.md",
            "project-completion-report.md",
        ]
        
        for path in blocked_paths:
            assert policy.is_report_intent(path, ""), f"Failed to block: {path}"
    
    def test_progress_markdown_blocked(self):
        """Files matching **/*progress*.md are blocked."""
        policy = FileWritePolicy()
        
        blocked_paths = [
            "progress.md",
            "weekly-progress.md",
            "phase-progress-update.md",
        ]
        
        for path in blocked_paths:
            assert policy.is_report_intent(path, ""), f"Failed to block: {path}"
    
    def test_analysis_markdown_blocked(self):
        """Files matching **/*analysis*.md are blocked."""
        policy = FileWritePolicy()
        
        blocked_paths = [
            "analysis.md",
            "code-analysis.md",
            "security-analysis-report.md",
        ]
        
        for path in blocked_paths:
            assert policy.is_report_intent(path, ""), f"Failed to block: {path}"


class TestFileWritePolicyExceptions:
    """Test allowed markdown files (exceptions)."""
    
    def test_docs_markdown_allowed(self):
        """docs/ directory markdown allowed."""
        policy = FileWritePolicy()
        
        allowed_paths = [
            "docs/README.md",
            "docs/architecture/overview.md",
            "docs/guides/quickstart.md",
        ]
        
        for path in allowed_paths:
            assert policy.allow_exception(path), f"Should allow: {path}"
    
    def test_readme_markdown_allowed(self):
        """README.md files allowed."""
        policy = FileWritePolicy()
        
        allowed_paths = [
            "README.md",
            "project/README.md",
            "src/README.md",
        ]
        
        for path in allowed_paths:
            assert policy.allow_exception(path), f"Should allow: {path}"
    
    def test_dotgithub_allowed(self):
        """.github/ directory markdown allowed."""
        policy = FileWritePolicy()
        
        allowed_paths = [
            ".github/prompts/CORTEX.prompt.md",
            ".github/agents/core/agent.md",
        ]
        
        for path in allowed_paths:
            assert policy.allow_exception(path), f"Should allow: {path}"
    
    def test_registry_allowed(self):
        """cortex-registry/ markdown allowed."""
        policy = FileWritePolicy()
        
        allowed_paths = [
            "cortex-registry/_cortex-master/phases/active/phase-29.yaml",
            "cortex-registry/_cortex-master/governance/core-rules.yaml",
        ]
        
        for path in allowed_paths:
            assert policy.allow_exception(path), f"Should allow: {path}"


class TestFileWritePolicyEnforcement:
    """Test policy enforcement at write-time."""
    
    def test_block_raises_exception(self):
        """Blocking a write raises MarkdownBanViolation."""
        policy = FileWritePolicy(enforce=True)
        
        with pytest.raises(MarkdownBanViolation):
            policy.check_write("phase-report.md", "# Report\n\nContent")
    
    def test_warn_only_mode(self):
        """Warn-only mode doesn't raise exception."""
        policy = FileWritePolicy(enforce=False)
        
        # Should not raise
        result = policy.check_write("phase-report.md", "Content")
        assert result is False  # Blocked but no exception
    
    def test_allowed_writes_pass(self):
        """Allowed writes return True."""
        policy = FileWritePolicy(enforce=True)
        
        result = policy.check_write("docs/guide.md", "Content")
        assert result is True


class TestFileWritePolicyContentAnalysis:
    """Test content-based intent detection."""
    
    def test_report_keywords_in_content(self):
        """Content with report keywords flagged."""
        policy = FileWritePolicy()
        
        content = """
# Phase 29 Completion Report

## Summary
All phases complete.

## Metrics
- 15 tests passing
- 550 LOC added
"""
        
        assert policy.is_report_intent("output.md", content)
    
# Data Adapter Architecture

## Overview
The adapter pattern provides...

## Implementation
```python
class JSONAdapter:
    pass
```
"""
        
        # Even if filename is suspicious, content analysis says it's technical
        # (This is a soft check - filename takes precedence)
        assert not policy.is_report_intent("docs/adapter.md", content)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
