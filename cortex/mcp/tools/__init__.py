from typing import Any
"""
CORTEX MCP v2 - Tool Implementations

35 production tools organized by category:
- Core (4): process_request, challenge, classify, request_lifecycle
- Intelligence (4): lens, knowledge, git, generate_tests
- Governance (4): governance, validate, load, validate_request (Phase 48)
- Operations (7): debug, refactor, plan, onboard, dashboard, master_plan (Phase 50), scaffold_files (PB-STS-001)
- Utilities (11): verify, ask, vacuum, tools_catalog, total_recall, metrics, check, vision, orchestrator,
                  health_orchestrate, vacuum_orchestrate (Phase 48)
- Toolkit (5): diagnose, verify_env, cleanup, validate_gov, analyze (Phase 90)

AC_START: AC-WAVE100-S2-006
AC_START: AC-P90-S7-001
AC_START: AC-P48-MCP-001
AC_START: AC-P50-MCP-001
AC_START: PB-STS-001-RUN-2-SCAFFOLD-TOOL
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

# Scaffold files tool (PB-STS-001 Run 2 — GAP-007 resolution)
from cortex.mcp.tools.scaffold_files_tool import CortexScaffoldFiles

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

# Phase 51 — Health-Vacuum Integrity Pipeline tools (replaces Phase 48)
from cortex.mcp.tools.health_scan_tool import cortex_health_scan
from cortex.mcp.tools.vacuum_execute_tool import cortex_vacuum_execute

# Phase 50 — CortexMasterPlanOrchestrator exposure (CORE-035: registered via ConsolidatedTool)
from cortex.mcp.tools.master_plan_tool import CortexMasterPlanTool, cortex_master_plan

# GitOrchestrator — replaces git hooks + GitHub Actions (2026-02-19)
from cortex.mcp.tools.git_orchestrator_tool import CortexGitPush

# Phase 07b — Canonical test quality gate MCP tool
from cortex.mcp.tools.test_quality_tool import CortexScoreTests

# Phase 23 — Workflow template discovery tool (function-based)
from cortex.mcp.tools.list_workflow_templates import cortex_list_workflow_templates


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
    CortexScaffoldFiles,  # PB-STS-001 Run 2 — GAP-007 resolution
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
    # Health-Vacuum (Phase 51 — function-based, not class-based)
    # cortex_health_scan and cortex_vacuum_execute are standalone functions
    # MasterPlan (1) - Phase 50
    CortexMasterPlanTool,
    # GitOrchestrator (1) - replaces git hooks + GitHub Actions
    CortexGitPush,
    # TestQualityGate (1) - Phase 07b canonical scorer
    CortexScoreTests,
]


def register_all_tools(registry: Any) -> int:
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
    "CortexWorkflow",
    "CortexScaffoldFiles",  # PB-STS-001 Run 2 — GAP-007 resolution
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
    # Health-Vacuum (Phase 51)
    "cortex_health_scan",
    "cortex_vacuum_execute",
    # MasterPlan (Phase 50)
    "CortexMasterPlanTool",
    "cortex_master_plan",
    # GitOrchestrator (replaces git hooks + GitHub Actions)
    "CortexGitPush",
    # TestQualityGate (Phase 07b)
    "CortexScoreTests",
    # WorkflowTemplates (Phase 23)
    "cortex_list_workflow_templates",
    # Registration
    "ALL_TOOLS",
    "register_all_tools",
]

# AC_COMPLETE: AC-WAVE100-S2-006 ✅ All tools exported
# AC_COMPLETE: AC-P90-S7-001 ✅ 5 toolkit tools integrated
# AC_COMPLETE: AC-P48-MCP-001 ✅ 2 health-vacuum MCP tools registered
# AC_COMPLETE: AC-P50-MCP-001 ✅ CortexMasterPlanTool registered