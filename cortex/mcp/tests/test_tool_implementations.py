"""
CORTEX MCP v2 - Tool Implementation Tests

Tests for the 24 production tool implementations:
- Core tools (4)
- Intelligence tools (3)
- Governance tools (3)
- Operations tools (5)
- Utilities tools (9)

AC_START: AC-WAVE100-S2-007
"""

import pytest
import asyncio
from typing import Any, Dict

# Core tools
from cortex.mcp.tools.core import (
    CortexProcessRequest,
    CortexChallenge,
    CortexClassify,
    CortexRequestLifecycle,
)

# Intelligence tools
from cortex.mcp.tools.intelligence import (
    CortexLens,
    CortexKnowledge,
    CortexGit,
)

# Governance tools
from cortex.mcp.tools.governance import (
    CortexGovernance,
    CortexValidate,
    CortexLoad,
)

# Operations tools
from cortex.mcp.tools.operations import (
    CortexDebug,
    CortexRefactor,
    CortexPlan,
    CortexOnboard,
    CortexDashboard,
)

# Utilities tools
from cortex.mcp.tools.utilities import (
    CortexVerify,
    CortexAsk,
    CortexVacuum,
    CortexToolsCatalog,
    CortexTotalRecall,
    CortexMetrics,
    CortexCheck,
    CortexVision,
    CortexOrchestrator,
)

from cortex.mcp.mcp_tool_base import ToolCategory, ToolResult


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def run_async(coro: object) -> None:
    """Helper to run async functions in tests."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop, create a new one
        return asyncio.run(coro)
    else:
        # Use existing loop
        return loop.run_until_complete(coro)


# =============================================================================
# CORE TOOLS TESTS
# =============================================================================

class TestCortexProcessRequest:
    """Tests for cortex_process_request tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexProcessRequest()
        assert tool.name == "cortex_process_request"
    
    def test_tool_category(self) -> None:
        """Test tool category."""
        tool = CortexProcessRequest()
        assert tool.category == ToolCategory.CORE
    
    def test_supported_operations(self) -> None:
        """Test supported operations."""
        tool = CortexProcessRequest()
        assert "implement" in tool.supported_operations
        assert "fix" in tool.supported_operations
        assert "refactor" in tool.supported_operations
        assert "analyze" in tool.supported_operations
        assert "test" in tool.supported_operations
    
    def test_execute_implement(self) -> None:
        """Test execute implement."""
        tool = CortexProcessRequest()
        result = run_async(tool.execute(
            operation="implement",
            request="Add a new feature",
            target="module.py",
        ))
        assert result.success is True
        # Check either operation is in metadata or in data
        assert result.metadata.get("orchestrator") == "TDDOrchestrator" or result.data.get("operation") == "implement"
    
    def test_execute_unknown_operation(self) -> None:
        """Test execute unknown operation."""
        tool = CortexProcessRequest()
        result = run_async(tool.execute(
            operation="unknown_op",
            request="test",
        ))
        assert result.success is False
        assert "Unknown operation" in result.error


class TestCortexChallenge:
    """Tests for cortex_challenge tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexChallenge()
        assert tool.name == "cortex_challenge"
    
    def test_supported_operations(self) -> None:
        """Test supported operations."""
        tool = CortexChallenge()
        assert "generate" in tool.supported_operations
        assert "review" in tool.supported_operations
        assert "validate" in tool.supported_operations
    
    def test_generate_challenges(self) -> None:
        """Test generate challenges."""
        tool = CortexChallenge()
        result = run_async(tool.execute(
            operation="generate",
            request="Implement authentication",
            depth="deep",
        ))
        assert result.success is True
        assert "challenges" in result.data
        assert len(result.data["challenges"]) > 0
    
    def test_shallow_depth_fewer_challenges(self) -> None:
        """Test shallow depth fewer challenges."""
        tool = CortexChallenge()
        shallow = run_async(tool.execute(
            operation="generate",
            request="Test request",
            depth="shallow",
        ))
        deep = run_async(tool.execute(
            operation="generate",
            request="Test request",
            depth="deep",
        ))
        # Deep should have more challenges
        assert len(deep.data["challenges"]) >= len(shallow.data["challenges"])


class TestCortexClassify:
    """Tests for cortex_classify tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexClassify()
        assert tool.name == "cortex_classify"
    
    def test_classify_implement_intent(self) -> None:
        """Test classify implement intent."""
        tool = CortexClassify()
        result = run_async(tool.execute(
            operation="intent",
            request="Implement a new feature",
        ))
        assert result.success is True
        assert result.data["intent"] == "IMPLEMENT"
    
    def test_classify_fix_intent(self) -> None:
        """Test classify fix intent."""
        tool = CortexClassify()
        result = run_async(tool.execute(
            operation="intent",
            request="Fix the bug in authentication",
        ))
        assert result.success is True
        assert result.data["intent"] == "FIX"
    
    def test_classify_scope(self) -> None:
        """Test classify scope."""
        tool = CortexClassify()
        result = run_async(tool.execute(
            operation="scope",
            request="Refactor the module",
        ))
        assert result.success is True
        assert "scope" in result.data


class TestCortexRequestLifecycle:
    """Tests for cortex_request_lifecycle tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexRequestLifecycle()
        assert tool.name == "cortex_request_lifecycle"
    
    def test_create_request(self) -> None:
        """Test create request."""
        tool = CortexRequestLifecycle()
        result = run_async(tool.execute(operation="create"))
        assert result.success is True
        assert "request_id" in result.data
        assert result.data["status"] == "created"
    
    def test_update_requires_request_id(self) -> None:
        """Test update requires request id."""
        tool = CortexRequestLifecycle()
        result = run_async(tool.execute(operation="update"))
        assert result.success is False
        assert "request_id required" in result.error
    
    def test_complete_request(self) -> None:
        """Test complete request."""
        tool = CortexRequestLifecycle()
        result = run_async(tool.execute(
            operation="complete",
            request_id="test-123",
        ))
        assert result.success is True
        assert result.data["status"] == "completed"


# =============================================================================
# INTELLIGENCE TOOLS TESTS
# =============================================================================

class TestCortexLens:
    """Tests for cortex_lens tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexLens()
        assert tool.name == "cortex_lens"
    
    def test_tool_category(self) -> None:
        """Test tool category."""
        tool = CortexLens()
        assert tool.category == ToolCategory.INTELLIGENCE
    
    def test_supported_operations(self) -> None:
        """Test supported operations."""
        tool = CortexLens()
        ops = tool.supported_operations
        assert "analyze" in ops
        assert "search" in ops
        assert "graph" in ops
        assert "duplicates" in ops
        assert "ast" in ops
    
    def test_analyze_operation(self) -> None:
        """Test analyze operation."""
        tool = CortexLens()
        result = run_async(tool.execute(
            operation="analyze",
            target="cortex/mcp/",
            depth="standard",
        ))
        assert result.success is True
        assert "lens" in result.data
        assert "language" in result.data["lens"]
    
    def test_duplicates_core035(self) -> None:
        """Test duplicates core035."""
        tool = CortexLens()
        result = run_async(tool.execute(
            operation="duplicates",
            target="cortex/",
        ))
        assert result.success is True
        assert "core_035_compliant" in result.data


class TestCortexKnowledge:
    """Tests for cortex_knowledge tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexKnowledge()
        assert tool.name == "cortex_knowledge"
    
    def test_best_practices(self) -> None:
        """Test best practices."""
        tool = CortexKnowledge()
        result = run_async(tool.execute(
            operation="best_practices",
            query="TDD",
        ))
        assert result.success is True
        assert "practices" in result.data
        assert len(result.data["practices"]) > 0


class TestCortexGit:
    """Tests for cortex_git tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexGit()
        assert tool.name == "cortex_git"
    
    def test_supported_operations(self) -> None:
        """Test supported operations."""
        tool = CortexGit()
        ops = tool.supported_operations
        assert "history" in ops
        assert "blame" in ops
        assert "diff" in ops
        assert "context" in ops
        assert "changes" in ops
    
    def test_history_operation(self) -> None:
        """Test history operation."""
        tool = CortexGit()
        result = run_async(tool.execute(
            operation="history",
            limit=10,
        ))
        assert result.success is True
        assert "commits" in result.data


# =============================================================================
# GOVERNANCE TOOLS TESTS
# =============================================================================

class TestCortexGovernance:
    """Tests for cortex_governance tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexGovernance()
        assert tool.name == "cortex_governance"
    
    def test_tool_category(self) -> None:
        """Test tool category."""
        tool = CortexGovernance()
        assert tool.category == ToolCategory.GOVERNANCE
    
    def test_enforce_operation(self) -> None:
        """Test enforce operation."""
        tool = CortexGovernance()
        result = run_async(tool.execute(
            operation="enforce",
            target="cortex/",
        ))
        assert result.success is True
        assert "rules_checked" in result.data
        assert result.data["passed"] is True
    
    def test_query_operation(self) -> None:
        """Test query operation."""
        tool = CortexGovernance()
        result = run_async(tool.execute(operation="query"))
        assert result.success is True
        assert "total_rules" in result.data


class TestCortexValidate:
    """Tests for cortex_validate tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexValidate()
        assert tool.name == "cortex_validate"
    
    def test_compliance_validation(self) -> None:
        """Test compliance validation."""
        tool = CortexValidate()
        result = run_async(tool.execute(
            operation="compliance",
            target="cortex/mcp/",
        ))
        assert result.success is True
        assert "checks" in result.data
        assert result.data["passed"] is True
    
    def test_venv_validation(self) -> None:
        """Test venv validation."""
        tool = CortexValidate()
        result = run_async(tool.execute(operation="venv"))
        assert result.success is True
        assert "python_version" in result.data


class TestCortexLoad:
    """Tests for cortex_load tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexLoad()
        assert tool.name == "cortex_load"
    
    def test_load_rules(self) -> None:
        """Test load rules."""
        tool = CortexLoad()
        result = run_async(tool.execute(
            operation="rules",
            tier="tier0",
        ))
        assert result.success is True
        assert "rules" in result.data
        assert all(r["tier"] == "tier0" for r in result.data["rules"])
    
    def test_load_modes(self) -> None:
        """Test load modes."""
        tool = CortexLoad()
        result = run_async(tool.execute(operation="modes"))
        assert result.success is True
        assert "modes" in result.data


# =============================================================================
# OPERATIONS TOOLS TESTS
# =============================================================================

class TestCortexDebug:
    """Tests for cortex_debug tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexDebug()
        assert tool.name == "cortex_debug"
    
    def test_tool_category(self) -> None:
        """Test tool category."""
        tool = CortexDebug()
        assert tool.category == ToolCategory.OPERATIONS
    
    def test_inject_operation(self) -> None:
        """Test inject operation."""
        tool = CortexDebug()
        result = run_async(tool.execute(
            operation="inject",
            target="module.py",
        ))
        assert result.success is True
        assert "markers_injected" in result.data
    
    def test_cleanup_operation(self) -> None:
        """Test cleanup operation."""
        tool = CortexDebug()
        result = run_async(tool.execute(operation="cleanup"))
        assert result.success is True
        assert "markers_removed" in result.data


class TestCortexRefactor:
    """Tests for cortex_refactor tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexRefactor()
        assert tool.name == "cortex_refactor"
    
    def test_rename_requires_new_name(self) -> None:
        """Test rename requires new name."""
        tool = CortexRefactor()
        result = run_async(tool.execute(
            operation="rename",
            target="old_name",
        ))
        assert result.success is False
        assert "new_name required" in result.error
    
    def test_rename_operation(self) -> None:
        """Test rename operation."""
        tool = CortexRefactor()
        result = run_async(tool.execute(
            operation="rename",
            target="old_name",
            new_name="new_name",
        ))
        assert result.success is True
        assert result.data["new_name"] == "new_name"


class TestCortexPlan:
    """Tests for cortex_plan tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexPlan()
        assert tool.name == "cortex_plan"
    
    def test_create_phase(self) -> None:
        """Test create phase."""
        tool = CortexPlan()
        result = run_async(tool.execute(
            operation="create",
            phase_id="phase-101",
            data={"stages": ["S1", "S2"]},
        ))
        assert result.success is True
        assert result.data["status"] == "created"
    
    def test_sync_operation(self) -> None:
        """Test sync operation."""
        tool = CortexPlan()
        result = run_async(tool.execute(operation="sync"))
        assert result.success is True
        assert result.data["synced"] is True


class TestCortexOnboard:
    """Tests for cortex_onboard tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexOnboard()
        assert tool.name == "cortex_onboard"
    
    def test_full_onboarding(self) -> None:
        """Test full onboarding."""
        tool = CortexOnboard()
        result = run_async(tool.execute(
            operation="full",
            path=".",
        ))
        assert result.success is True
        assert "lens_analysis" in result.data
        assert "security_assessment" in result.data


class TestCortexDashboard:
    """Tests for cortex_dashboard tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexDashboard()
        assert tool.name == "cortex_dashboard"
    
    def test_generate_operation(self) -> None:
        """Test generate operation."""
        tool = CortexDashboard()
        result = run_async(tool.execute(
            operation="generate",
            target="test-repo",
            format="html",
        ))
        assert result.success is True
        assert result.data["generated"] is True


# =============================================================================
# UTILITIES TOOLS TESTS
# =============================================================================

class TestCortexVerify:
    """Tests for cortex_verify tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexVerify()
        assert tool.name == "cortex_verify"
    
    def test_tool_category(self) -> None:
        """Test tool category."""
        tool = CortexVerify()
        assert tool.category == ToolCategory.UTILITIES
    
    def test_environment_verification(self) -> None:
        """Test environment verification."""
        tool = CortexVerify()
        result = run_async(tool.execute(operation="environment"))
        assert result.success is True
        assert "checks" in result.data
        assert "python_version" in result.data["checks"]


class TestCortexAsk:
    """Tests for cortex_ask tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexAsk()
        assert tool.name == "cortex_ask"
    
    def test_ask_question(self) -> None:
        """Test ask question."""
        tool = CortexAsk()
        result = run_async(tool.execute(
            operation="architecture",
            question="What is MCP?",
        ))
        assert result.success is True
        assert "answer" in result.data


class TestCortexVacuum:
    """Tests for cortex_vacuum tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexVacuum()
        assert tool.name == "cortex_vacuum"
    
    def test_scan_operation(self) -> None:
        """Test scan operation."""
        tool = CortexVacuum()
        result = run_async(tool.execute(
            operation="scan",
            path=".",
        ))
        assert result.success is True
        assert "sprawl_detected" in result.data


class TestCortexToolsCatalog:
    """Tests for cortex_tools_catalog tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexToolsCatalog()
        assert tool.name == "cortex_tools_catalog"
    
    def test_list_all_tools(self) -> None:
        """Test list all tools."""
        tool = CortexToolsCatalog()
        result = run_async(tool.execute(operation="list"))
        assert result.success is True
        assert "tools" in result.data
        assert result.data["total"] == 24
    
    def test_search_tools(self) -> None:
        """Test search tools."""
        tool = CortexToolsCatalog()
        result = run_async(tool.execute(
            operation="search",
            query="process",
        ))
        assert result.success is True
        assert result.data["total"] >= 1


class TestCortexTotalRecall:
    """Tests for cortex_total_recall tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexTotalRecall()
        assert tool.name == "cortex_total_recall"
    
    def test_discover_features(self) -> None:
        """Test discover features."""
        tool = CortexTotalRecall()
        result = run_async(tool.execute(operation="discover"))
        assert result.success is True
        assert "features" in result.data


class TestCortexMetrics:
    """Tests for cortex_metrics tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexMetrics()
        assert tool.name == "cortex_metrics"
    
    def test_capture_metric(self) -> None:
        """Test capture metric."""
        tool = CortexMetrics()
        result = run_async(tool.execute(
            operation="capture",
            metric_type="tdd",
            data={"cycles": 5},
        ))
        assert result.success is True
        assert result.data["captured"] is True


class TestCortexCheck:
    """Tests for cortex_check tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexCheck()
        assert tool.name == "cortex_check"
    
    def test_health_check(self) -> None:
        """Test health check."""
        tool = CortexCheck()
        result = run_async(tool.execute(operation="health"))
        assert result.success is True
        assert result.data["status"] == "healthy"


class TestCortexVision:
    """Tests for cortex_vision tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexVision()
        assert tool.name == "cortex_vision"
    
    def test_analyze_operation(self) -> None:
        """Test analyze operation."""
        tool = CortexVision()
        result = run_async(tool.execute(
            operation="analyze",
            image="base64_encoded_image_data",
        ))
        assert result.success is True
        assert "results" in result.data


class TestCortexOrchestrator:
    """Tests for cortex_orchestrator tool."""
    
    def test_tool_name(self) -> None:
        """Test tool name."""
        tool = CortexOrchestrator()
        assert tool.name == "cortex_orchestrator"
    
    def test_list_orchestrators(self) -> None:
        """Test list orchestrators."""
        tool = CortexOrchestrator()
        result = run_async(tool.execute(operation="list"))
        assert result.success is True
        assert "orchestrators" in result.data
        assert result.data["total"] > 0
    
    def test_status_requires_name(self) -> None:
        """Test status requires name."""
        tool = CortexOrchestrator()
        result = run_async(tool.execute(operation="status"))
        assert result.success is False
        assert "orchestrator name required" in result.error


# =============================================================================
# CROSS-TOOL INTEGRATION TESTS
# =============================================================================

class TestToolIntegration:
    """Integration tests across multiple tools."""
    
    def test_all_tools_have_unique_names(self) -> None:
        """Verify all tool classes have unique names."""
        from cortex.mcp.tools import ALL_TOOLS
        
        names = [tool_class().name for tool_class in ALL_TOOLS]
        assert len(names) == len(set(names)), "Duplicate tool names found"
    
    def test_all_tools_return_tool_result(self) -> None:
        """Verify all tools return ToolResult instances."""
        from cortex.mcp.tools import ALL_TOOLS
        
        for tool_class in ALL_TOOLS:
            tool = tool_class()
            # Get first supported operation or default
            ops = getattr(tool, 'supported_operations', [])
            op = ops[0] if ops else None
            
            # Build minimal params
            params = {}
            if op:
                params["operation"] = op
            
            # Add required params based on tool
            if "request" in [p.name for p in tool.parameters]:
                params["request"] = "test"
            if "question" in [p.name for p in tool.parameters]:
                params["question"] = "test"
            if "target" in [p.name for p in tool.parameters]:
                params["target"] = "test"
            if "image" in [p.name for p in tool.parameters]:
                params["image"] = "test"
            if "query" in [p.name for p in tool.parameters]:
                params["query"] = "test"
            
            result = run_async(tool.execute(**params))
            assert isinstance(result, ToolResult), f"{tool.name} did not return ToolResult"
    
    def test_tool_count_is_24(self) -> None:
        """Verify exactly 24 tools are implemented."""
        from cortex.mcp.tools import ALL_TOOLS
        
        assert len(ALL_TOOLS) == 24, f"Expected 24 tools, got {len(ALL_TOOLS)}"


# AC_COMPLETE: AC-WAVE100-S2-007 ✅ Tool implementation tests
