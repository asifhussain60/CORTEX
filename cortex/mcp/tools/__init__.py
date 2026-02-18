"""
CORTEX MCP v2 - Tool Implementations

33 production tools organized by category:
- Core (4): process_request, challenge, classify, request_lifecycle
- Intelligence (4): lens, knowledge, git, generate_tests
- Governance (4): governance, validate, load, validate_request (Phase 48)
- Operations (5): debug, refactor, plan, onboard, dashboard
- Utilities (11): verify, ask, vacuum, tools_catalog, total_recall, metrics, check, vision, orchestrator,
                  health_orchestrate, vacuum_orchestrate (Phase 48)
- Toolkit (5): diagnose, verify_env, cleanup, validate_gov, analyze (Phase 90)

AC_START: AC-WAVE100-S2-006
AC_START: AC-P90-S7-001
AC_START: AC-P48-MCP-001
"""

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
from cortex.mcp.tools.intelligence_generation import (
    CortexGenerateTests,
)

# Governance tools
from cortex.mcp.tools.governance import (
    CortexGovernance,
    CortexValidate,
    CortexLoad,
    CortexValidateRequest,  # Phase 48 Stage 4
)

# Operations tools
from cortex.mcp.tools.operations import (
    CortexDebug,
    CortexRefactor,
    CortexPlan,
    CortexOnboard,
    CortexDashboard,
)
from cortex.mcp.tools.workflow_tools import (
    CortexWorkflow,  # Phase 100 Stage 2
)

# Utility tools
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

# Toolkit tools (Phase 90)
from cortex.mcp.tools.toolkit import (
    ToolkitDiagnoseTool,
    ToolkitVerifyTool,
    ToolkitCleanupTool,
    ToolkitValidateTool,
    ToolkitAnalyzeTool,
)

# Phase 48 — Health-Vacuum Integrity Pipeline tools
from cortex.mcp.tools.health_orchestrator_tool import CortexHealthOrchestrate
from cortex.mcp.tools.vacuum_orchestrator_tool import CortexVacuumOrchestrate


# All tool classes for registration
ALL_TOOLS = [
    # Core (4)
    CortexProcessRequest,
    CortexChallenge,
    CortexClassify,
    CortexRequestLifecycle,
    # Intelligence (4)
    CortexLens,
    CortexKnowledge,
    CortexGit,
    CortexGenerateTests,  # WAVE-2 Stage 6
    # Governance (4)
    CortexGovernance,
    CortexValidate,
    CortexLoad,
    CortexValidateRequest,  # Phase 48
    # Operations (6)
    CortexDebug,
    CortexRefactor,
    CortexPlan,
    CortexOnboard,
    CortexDashboard,
    CortexWorkflow,  # Phase 100 Stage 2
    # Utilities (9)
    CortexVerify,
    CortexAsk,
    CortexVacuum,
    CortexToolsCatalog,
    CortexTotalRecall,
    CortexMetrics,
    CortexCheck,
    CortexVision,
    CortexOrchestrator,
    # Toolkit (5) - Phase 90
    ToolkitDiagnoseTool,
    ToolkitVerifyTool,
    ToolkitCleanupTool,
    ToolkitValidateTool,
    ToolkitAnalyzeTool,
    # Health-Vacuum (2) - Phase 48
    CortexHealthOrchestrate,
    CortexVacuumOrchestrate,
]


def register_all_tools(registry) -> int:
    """
    Register all tool implementations with the registry.
    
    Args:
        registry: ToolRegistry instance
        
    Returns:
        Number of tools registered
    """
    count = 0
    for tool_class in ALL_TOOLS:
        try:
            tool = tool_class()
            registry.register(tool)
            count += 1
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to register {tool_class.__name__}: {e}")
    return count


__all__ = [
    # Core
    "CortexProcessRequest",
    "CortexChallenge",
    "CortexClassify",
    "CortexRequestLifecycle",
    # Intelligence
    "CortexLens",
    "CortexKnowledge",
    "CortexGit",
    "CortexGenerateTests",  # WAVE-2 Stage 6
    # Governance
    "CortexGovernance",
    "CortexValidate",
    "CortexLoad",
    "CortexValidateRequest",  # Phase 48
    # Operations
    "CortexDebug",
    "CortexRefactor",
    "CortexPlan",
    "CortexOnboard",
    "CortexDashboard",
    # Utilities
    "CortexVerify",
    "CortexAsk",
    "CortexVacuum",
    "CortexToolsCatalog",
    "CortexTotalRecall",
    "CortexMetrics",
    "CortexCheck",
    "CortexVision",
    "CortexOrchestrator",
    # Toolkit (Phase 90)
    "ToolkitDiagnoseTool",
    "ToolkitVerifyTool",
    "ToolkitCleanupTool",
    "ToolkitValidateTool",
    "ToolkitAnalyzeTool",
    # Health-Vacuum (Phase 48)
    "CortexHealthOrchestrate",
    "CortexVacuumOrchestrate",
    # Registration
    "ALL_TOOLS",
    "register_all_tools",
]

# AC_COMPLETE: AC-WAVE100-S2-006 ✅ All tools exported
# AC_COMPLETE: AC-P90-S7-001 ✅ 5 toolkit tools integrated
# AC_COMPLETE: AC-P48-MCP-001 ✅ 2 health-vacuum MCP tools registered