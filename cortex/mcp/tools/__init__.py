"""
CORTEX MCP v2 - Tool Implementations

25 production tools organized by category:
- Core (4): process_request, challenge, classify, request_lifecycle
- Intelligence (3): lens, knowledge, git
- Governance (4): governance, validate, load, validate_request (Phase 48)
- Operations (5): debug, refactor, plan, onboard, dashboard
- Utilities (9): verify, ask, vacuum, tools_catalog, total_recall, metrics, check, vision, orchestrator

AC_START: AC-WAVE100-S2-006
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


# All tool classes for registration
ALL_TOOLS = [
    # Core (4)
    CortexProcessRequest,
    CortexChallenge,
    CortexClassify,
    CortexRequestLifecycle,
    # Intelligence (3)
    CortexLens,
    CortexKnowledge,
    CortexGit,
    # Governance (4)
    CortexGovernance,
    CortexValidate,
    CortexLoad,
    CortexValidateRequest,  # Phase 48
    # Operations (5)
    CortexDebug,
    CortexRefactor,
    CortexPlan,
    CortexOnboard,
    CortexDashboard,
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
    # Registration
    "ALL_TOOLS",
    "register_all_tools",
]

# AC_COMPLETE: AC-WAVE100-S2-006 ✅ All tools exported