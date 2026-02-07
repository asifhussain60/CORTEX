"""
Unit tests for Upgrade Diff Analyzer.

Tests for Phase 40 Stage 1:
- AC-PHASE40-001: Detects prompt changes (5 tests)
- AC-PHASE40-002: Detects agent changes (3 tests)
- AC-PHASE40-003: Detects orchestrator changes (3 tests)
- AC-PHASE40-004: Detects MCP tool additions (2 tests)
- AC-PHASE40-005: Extracts version numbers (2 tests)

Total: 15 tests

Author: Asif Hussain
Date: 2026-02-07
Phase: 40
"""

import pytest
from pathlib import Path
from typing import Dict, List
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.support.upgrade_diff_analyzer import (
    UpgradeDiffAnalyzer,
    DiffResult,
    ChangeCategory,
    PromptChange,
    AgentChange,
    OrchestratorChange,
    MCPToolChange,
)


# AC_START: AC-PHASE40-001
# Description: Diff analyzer detects prompt changes (new modes/commands)
# Author: Asif Hussain
# Date: 2026-02-07


@pytest.fixture
def analyzer():
    """Create UpgradeDiffAnalyzer instance."""
    return UpgradeDiffAnalyzer(repo_path="/test/cortex")


@pytest.fixture
def sample_prompt_diff():
    """Sample git diff for prompt file."""
    return """
diff --git a/.github/prompts/cortex-architect.prompt.md b/.github/prompts/cortex-architect.prompt.md
index abc123..def456 100644
--- a/.github/prompts/cortex-architect.prompt.md
+++ b/.github/prompts/cortex-architect.prompt.md
@@ -1,5 +1,5 @@
 # CORTEX Architect Prompt
-**Version:** 14.3 | **Updated:** 2026-02-05
+**Version:** 14.4 | **Updated:** 2026-02-07

 ## 🎯 HEXA-MODE (6 Modes)
 
+### QUERY Mode (NEW)
+Consolidated INTERACTIVE + LIST + ask modes for multi-purpose queries.
+
+| Command | Action |
+|---------|--------|
+| `/query {topic}` | Multi-purpose query interface |
"""


class TestPromptChangeDetection:
    """Test detection of prompt file changes."""

    def test_detects_new_mode_in_prompt(self, analyzer, sample_prompt_diff):
        """Verify detection of new mode additions."""
        changes = analyzer.analyze_prompt_diff(sample_prompt_diff)
        
        assert len(changes) > 0
        assert any(c.change_type == "new_mode" for c in changes)
        assert any("QUERY" in c.name for c in changes)

    def test_detects_new_command_in_prompt(self, analyzer):
        """Verify detection of new command additions."""
        diff = """
+| `/debug {path}` | Full debug cycle |
+| `/check-env` | Environment check + upgrade detection |
"""
        changes = analyzer.analyze_prompt_diff(diff)
        
        assert len(changes) >= 2
        assert any("/debug" in c.name for c in changes)
        assert any("/check-env" in c.name for c in changes)

    def test_extracts_mode_description(self, analyzer, sample_prompt_diff):
        """Verify extraction of mode descriptions."""
        changes = analyzer.analyze_prompt_diff(sample_prompt_diff)
        
        query_mode = next((c for c in changes if "QUERY" in c.name), None)
        assert query_mode is not None
        assert "multi-purpose" in query_mode.description.lower()

    def test_detects_prompt_section_additions(self, analyzer):
        """Verify detection of new sections in prompts."""
        diff = """
+## 🔄 HOLISTIC WORK PROTOCOL (NEW - Phase 38.0)
+Complete, systematic work regardless of token budget.
"""
        changes = analyzer.analyze_prompt_diff(diff)
        
        assert len(changes) > 0
        assert any("HOLISTIC" in c.name for c in changes)

    def test_ignores_minor_prompt_edits(self, analyzer):
        """Verify minor edits (typo fixes, formatting) are filtered."""
        diff = """
-Use tool discovery orchestrator
+Use the tool discovery orchestrator
"""
        changes = analyzer.analyze_prompt_diff(diff)
        
        # Should filter out minor edits
        assert len(changes) == 0


# AC_COMPLETE: AC-PHASE40-001 ✅


# AC_START: AC-PHASE40-002
# Description: Diff analyzer detects agent changes
# Author: Asif Hussain
# Date: 2026-02-07


class TestAgentChangeDetection:
    """Test detection of agent file changes."""

    def test_detects_new_agent_file(self, analyzer):
        """Verify detection of new agent additions."""
        diff = """
diff --git a/.github/agents/core/cortex-debug.md b/.github/agents/core/cortex-debug.md
new file mode 100644
+# CORTEX Debug Agent
+**Version:** 1.0 | **Mode:** DEBUG
"""
        changes = analyzer.analyze_agent_diff(diff)
        
        assert len(changes) > 0
        assert changes[0].change_type == "new_agent"
        assert "Cortex Debug" in changes[0].name or "cortex-debug" in changes[0].name.lower()

    def test_detects_agent_capability_additions(self, analyzer):
        """Verify detection of new agent capabilities."""
        diff = """
+## Capabilities
+- Smart debug marker injection
+- Correlation ID tracking
+- Sensitive value exclusion
"""
        # Need to include agent context for capability detection
        diff_with_context = """
diff --git a/.github/agents/core/cortex-debug.md
""" + diff
        
        changes = analyzer.analyze_agent_diff(diff_with_context)
        
        assert len(changes) >= 3
        assert any("marker injection" in c.description.lower() for c in changes)

    def test_extracts_agent_version_from_diff(self, analyzer):
        """Verify extraction of agent version numbers."""
        diff = """
+**Version:** 2.0 | **Updated:** 2026-02-07
"""
        version = analyzer.extract_agent_version(diff)
        
        assert version == "2.0"


# AC_COMPLETE: AC-PHASE40-002 ✅


# AC_START: AC-PHASE40-003
# Description: Diff analyzer detects orchestrator changes
# Author: Asif Hussain
# Date: 2026-02-07


class TestOrchestratorChangeDetection:
    """Test detection of orchestrator changes in wiring.yaml."""

    def test_detects_new_orchestrator_in_wiring(self, analyzer):
        """Verify detection of new orchestrator registration."""
        diff = """
+    - name: "DigestEnhancementOrchestrator"
+      module: "cortex.orchestrators.learning.digest_enhancement_orchestrator"
+      class: "DigestEnhancementOrchestrator"
+      priority: 83
"""
        changes = analyzer.analyze_wiring_diff(diff)
        
        assert len(changes) > 0
        assert changes[0].change_type == "new_orchestrator"
        assert "DigestEnhancementOrchestrator" in changes[0].name

    def test_detects_orchestrator_capability_additions(self, analyzer):
        """Verify detection of new orchestrator capabilities."""
        diff = """
+      capabilities:
+        - digest_automation
+        - enhancement_generation
+        - similarity_checking
"""
        changes = analyzer.analyze_wiring_diff(diff)
        
        capabilities = [c for c in changes if c.change_type == "new_capability"]
        assert len(capabilities) >= 3

    def test_extracts_orchestrator_metadata(self, analyzer):
        """Verify extraction of orchestrator metadata."""
        diff = """
+    - name: "TestOrchestrator"
+      description: "Test orchestrator for Phase 40"
+      priority: 90
"""
        changes = analyzer.analyze_wiring_diff(diff)
        
        assert len(changes) > 0
        assert changes[0].name == "TestOrchestrator"
        assert "Phase 40" in changes[0].description


# AC_COMPLETE: AC-PHASE40-003 ✅


# AC_START: AC-PHASE40-004
# Description: Diff analyzer detects MCP tool additions
# Author: Asif Hussain
# Date: 2026-02-07


class TestMCPToolChangeDetection:
    """Test detection of MCP tool additions."""

    def test_detects_new_mcp_tool_decorator(self, analyzer):
        """Verify detection of new @mcp_tool decorated functions."""
        diff = """
+@mcp_tool(name="cortex_digest_session")
+def cortex_digest_session(file_path: str, dry_run: bool = False) -> DigestResult:
+    '''Analyze chat session and extract learnings.'''
"""
        changes = analyzer.analyze_mcp_tool_diff(diff)
        
        assert len(changes) > 0
        assert changes[0].change_type == "new_mcp_tool"
        assert "cortex_digest_session" in changes[0].name

    def test_extracts_mcp_tool_description_from_docstring(self, analyzer):
        """Verify extraction of tool descriptions from docstrings."""
        diff = """
+@mcp_tool(name="cortex_debug_inject")
+def cortex_debug_inject(target_path: str) -> DebugResult:
+    '''Inject debug markers for CORTEX-assisted debugging.'''
+    pass
"""
        changes = analyzer.analyze_mcp_tool_diff(diff)
        
        assert len(changes) > 0
        assert "debug markers" in changes[0].description.lower()


# AC_COMPLETE: AC-PHASE40-004 ✅


# AC_START: AC-PHASE40-005
# Description: Diff analyzer extracts version numbers
# Author: Asif Hussain
# Date: 2026-02-07


class TestVersionExtraction:
    """Test extraction of version numbers from diffs."""

    def test_extracts_prompt_version_change(self, analyzer):
        """Verify extraction of version number changes."""
        diff = """
-**Version:** 14.3 | **Updated:** 2026-02-05
+**Version:** 14.4 | **Updated:** 2026-02-07
"""
        old_version, new_version = analyzer.extract_version_change(diff)
        
        assert old_version == "14.3"
        assert new_version == "14.4"

    def test_extracts_orchestrator_version(self, analyzer):
        """Verify extraction of orchestrator version numbers."""
        diff = """
+      version: "1.0.0"
+      metadata:
+        phase: "40"
"""
        version = analyzer.extract_orchestrator_version(diff)
        
        assert version == "1.0.0"


# AC_COMPLETE: AC-PHASE40-005 ✅


# Integration test
def test_full_upgrade_diff_analysis(analyzer):
    """Integration test for complete upgrade diff analysis."""
    with patch.object(analyzer, 'get_git_diff') as mock_diff:
        mock_diff.return_value = """
diff --git a/.github/prompts/cortex-architect.prompt.md
+**Version:** 14.4
+### QUERY Mode (NEW)

diff --git a/.github/agents/core/cortex-debug.md
new file mode 100644
+# CORTEX Debug Agent

diff --git a/cortex/wiring/specifications/wiring.yaml
+    - name: "DigestEnhancementOrchestrator"

diff --git a/cortex/mcp/tools/learning/digest_tools.py
+@mcp_tool(name="cortex_digest_session")
"""
        
        result = analyzer.analyze_upgrade()
        
        assert result is not None
        assert len(result.prompt_changes) > 0
        assert len(result.agent_changes) > 0
        assert len(result.orchestrator_changes) > 0
        assert len(result.mcp_tool_changes) > 0
