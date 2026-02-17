"""
Test Intelligence Integration: MCP Tools → Intelligence Orchestrator → Brain Layers

AC_START: AC-INTELLIGENCE-INTEGRATION-001
Root Cause: MCP tools have stub implementations that don't invoke intelligence layers.
Fix: Wire cortex_lens MCP tool to IntelligenceOrchestrator with audit logging.

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict

import pytest

from cortex.mcp.tools.intelligence import CortexLens
from cortex.orchestrators.intelligence.intelligence_orchestrator import (
    IntelligenceOrchestrator,
)


class TestIntelligenceIntegration:
    """Test MCP tool → IntelligenceOrchestrator → Brain layers integration."""

    @pytest.fixture
    def temp_audit_db(self, tmp_path: Path) -> Path:
        """Create temporary audit database."""
        return tmp_path / "test_intelligence_audit.db"

    @pytest.fixture
    def intelligence_orchestrator(self, temp_audit_db: Path) -> IntelligenceOrchestrator:
        """Create IntelligenceOrchestrator with test audit DB."""
        return IntelligenceOrchestrator(audit_db_path=temp_audit_db)

    @pytest.fixture
    def cortex_lens_tool(self) -> CortexLens:
        """Create CortexLens MCP tool."""
        return CortexLens()

    @pytest.fixture
    def test_file(self, tmp_path: Path) -> Path:
        """Create test Python file."""
        test_file = tmp_path / "sample.py"
        test_file.write_text(
            '''"""Sample module for testing."""

def add(a: int, b: int) -> int:
    """Add two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of a and b
    """
    return a + b


class Calculator:
    """Simple calculator class."""
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b
'''
        )
        return test_file

    @pytest.fixture
    def orchestrator_context(self) -> Dict[str, Any]:
        """Create valid orchestrator context."""
        return {"source": "MasterOrchestrator", "timestamp": "2026-02-14T00:00:00"}

    # ========================================================================
    # RED Phase: Tests that should fail initially
    # ========================================================================

    @pytest.mark.asyncio
    async def test_cortex_lens_analyze_invokes_intelligence_orchestrator(
        self,
        cortex_lens_tool: CortexLens,
        intelligence_orchestrator: IntelligenceOrchestrator,
        test_file: Path,
        orchestrator_context: Dict[str, Any],
        temp_audit_db: Path,
    ) -> None:
        """Test: cortex_lens analyze operation invokes IntelligenceOrchestrator."""
        # Arrange: Wire orchestrator into tool
        cortex_lens_tool._intelligence_orchestrator = intelligence_orchestrator

        # Act: Execute analyze operation
        result = await cortex_lens_tool.execute(
            operation="analyze",
            target=str(test_file),
            depth="standard",
            orchestrator_context=orchestrator_context,
        )

        # Assert: Result successful
        assert result.success is True
        assert result.data is not None

        # Assert: Intelligence audit DB has entries
        conn = sqlite3.connect(temp_audit_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM intelligence_audit WHERE operation = 'PARSE'")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1, "Expected 1 PARSE operation logged to intelligence_audit.db"

    @pytest.mark.asyncio
    async def test_cortex_lens_ast_operation_logs_to_audit_db(
        self,
        cortex_lens_tool: CortexLens,
        intelligence_orchestrator: IntelligenceOrchestrator,
        test_file: Path,
        orchestrator_context: Dict[str, Any],
        temp_audit_db: Path,
    ) -> None:
        """Test: AST operation logs to audit database."""
        # Arrange
        cortex_lens_tool._intelligence_orchestrator = intelligence_orchestrator

        # Act
        result = await cortex_lens_tool.execute(
            operation="ast",
            target=str(test_file),
            orchestrator_context=orchestrator_context,
        )

        # Assert: Successful execution
        assert result.success is True
        assert "ast" in result.data
        assert "metrics" in result.data

        # Assert: Audit log contains AST parse entry
        conn = sqlite3.connect(temp_audit_db)
        cursor = conn.cursor()
        cursor.execute("SELECT operation, target FROM intelligence_audit")
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) > 0, "Expected audit entries"
        operations = [row[0] for row in rows]
        assert "PARSE" in operations, "Expected PARSE operation logged"

    @pytest.mark.asyncio
    async def test_parse_python_file_returns_accurate_metrics(
        self,
        intelligence_orchestrator: IntelligenceOrchestrator,
        test_file: Path,
    ) -> None:
        """Test: IntelligenceOrchestrator returns accurate AST metrics."""
        # Act
        result = intelligence_orchestrator.parse_python_file(test_file)

        # Assert: Parse successful
        assert result.success is True

        # Assert: Correct function count
        assert len(result.functions) == 1, "Expected 1 function (add)"

        # Assert: Correct class count
        assert len(result.classes) == 1, "Expected 1 class (Calculator)"

        # Assert: Function has correct name
        assert result.functions[0].name == "add"

    @pytest.mark.asyncio
    async def test_comment_analysis_extracts_docstrings(
        self,
        intelligence_orchestrator: IntelligenceOrchestrator,
        test_file: Path,
    ) -> None:
        """Test: Comment analyzer extracts docstrings correctly."""
        # Act
        comments = intelligence_orchestrator.analyze_comments(test_file)

        # Assert: Result is a list with CommentAnalysisResult
        assert len(comments) > 0, "Expected comment analysis results"
        
        # Get the CommentAnalysisResult object
        from cortex.brain.core.intelligence.comment_analyzer import CommentAnalysisResult
        result = comments[0]
        assert isinstance(result, CommentAnalysisResult)

        # Assert: Docstrings extracted
        assert len(result.docstrings) > 0, "Expected docstrings"

        # Assert: Module docstring found
        docstring_texts = [d.raw for d in result.docstrings]
        has_module_doc = any("Sample module" in text for text in docstring_texts)
        assert has_module_doc, "Expected module docstring"

    @pytest.mark.asyncio
    async def test_intelligence_orchestrator_caching_works(
        self,
        intelligence_orchestrator: IntelligenceOrchestrator,
        test_file: Path,
        temp_audit_db: Path,
    ) -> None:
        """Test: Intelligence orchestrator caches parse results."""
        # Act: Parse same file twice
        result1 = intelligence_orchestrator.parse_python_file(test_file)
        result2 = intelligence_orchestrator.parse_python_file(test_file)

        # Assert: Both successful
        assert result1.success is True
        assert result2.success is True

        # Assert: Check audit log shows 1 real parse, 1 cached
        conn = sqlite3.connect(temp_audit_db)
        cursor = conn.cursor()
        cursor.execute("SELECT metadata FROM intelligence_audit WHERE operation = 'PARSE'")
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 2, "Expected 2 audit entries"

        # First should be uncached, second cached
        import json
        metadata1 = json.loads(rows[0][0]) if rows[0][0] else {}
        metadata2 = json.loads(rows[1][0]) if rows[1][0] else {}

        assert metadata1.get("cached") is False
        assert metadata2.get("cached") is True

    @pytest.mark.asyncio
    async def test_cortex_lens_without_orchestrator_uses_stub(
        self,
        cortex_lens_tool: CortexLens,
        test_file: Path,
        orchestrator_context: Dict[str, Any],
    ) -> None:
        """Test: CortexLens without orchestrator falls back to stub (current behavior)."""
        # Act: Execute without wiring orchestrator
        result = await cortex_lens_tool.execute(
            operation="analyze",
            target=str(test_file),
            orchestrator_context=orchestrator_context,
        )

        # Assert: Returns stub data (no real analysis)
        assert result.success is True
        assert result.data["lens"]["language"]["primary"] == "python"
        # Stub returns hardcoded values, not real analysis

    @pytest.mark.asyncio
    async def test_brain_layers_invoked_via_intelligence_orchestrator(
        self,
        intelligence_orchestrator: IntelligenceOrchestrator,
        test_file: Path,
    ) -> None:
        """Test: IntelligenceOrchestrator invokes brain layers (AST, comments)."""
        # Arrange: Verify orchestrator has layer components
        assert intelligence_orchestrator.ast_engine is not None
        assert intelligence_orchestrator.comment_analyzer is not None
        assert intelligence_orchestrator.routing_engine is not None

        # Act: Parse file
        result = intelligence_orchestrator.parse_python_file(test_file)

        # Assert: AST engine was used (verified by accurate results)
        assert result.success is True
        assert len(result.functions) > 0  # Real parsing, not stub

    @pytest.mark.asyncio
    async def test_routing_engine_available_but_not_yet_integrated(
        self,
        intelligence_orchestrator: IntelligenceOrchestrator,
    ) -> None:
        """Test: Routing engine exists but not yet exposed via MCP tools."""
        # Assert: Routing engine is initialized
        assert intelligence_orchestrator.routing_engine is not None

        # Note: Routing engine integration with MCP tools is Phase 2
        # This test documents current state

    # ========================================================================
    # Integration with cortex_brain layers
    # ========================================================================

    @pytest.mark.asyncio
    async def test_perception_layer_not_yet_integrated(self) -> None:
        """Test: Perception layer exists but not yet wired to MCP tools."""
        # Import perception layer
        from cortex_intelligence.perception import PatternRegistry

        # Assert: Layer available
        registry = PatternRegistry()
        assert registry is not None

        # Note: Perception → MCP integration is future work
        # This test documents architectural gap

    @pytest.mark.asyncio
    async def test_reasoning_layer_not_yet_integrated(self) -> None:
        """Test: Reasoning layer exists but not yet wired to MCP tools."""
        # Import reasoning layer
        from cortex_intelligence.reasoning import StrategySelector

        # Assert: Layer available
        selector = StrategySelector()
        assert selector is not None

        # Note: Reasoning → MCP integration is future work

    @pytest.mark.asyncio
    async def test_action_layer_not_yet_integrated(self) -> None:
        """Test: Action layer exists but not yet wired to MCP tools."""
        # Import action layer
        from cortex_intelligence.action import ExecutionPlanner

        # Assert: Layer available
        planner = ExecutionPlanner()
        assert planner is not None

        # Note: Action → MCP integration is future work


# AC_COMPLETE: AC-INTELLIGENCE-INTEGRATION-001 ✅ RED phase complete
