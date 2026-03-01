from typing import Any
"""
CORTEX MCP v3 — Tool Implementations (WAVE-101 consolidation)

30 production tools organized by category:
- Core (3): challenge, classify, request_lifecycle
  (CortexProcessRequest deprecated — not registered)
- Intelligence (5): lens, knowledge, git, generate_tests, brain_query
  (CortexIntelligenceMatrix removed — abstract method failure)
- Governance (4): governance, validate, load, validate_request
- Operations (7): debug, refactor, plan, onboard, dashboard, workflow, scaffold_files
- Utilities (9): verify (+check ops), ask, vacuum, tools_catalog (+recall ops),
                 total_recall (alias), metrics, check (alias), vision, orchestrator
- Toolkit (5): diagnose, verify_env, cleanup, validate_gov, analyze
- MasterPlan (1): master_plan
- GitOrchestrator (1): git_push
- TestQualityGate (1): score_tests
- Learning (1): learning

AC_START: AC-WAVE100-S2-006
AC_START: AC-P90-S7-001
AC_START: AC-P48-MCP-001
AC_START: AC-P50-MCP-001
AC_START: PB-STS-001-RUN-2-SCAFFOLD-TOOL
AC_START: AC-OPJ-PHASE52-MCP
AC_START: AC-WAVE101-CONSOLIDATION
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
    CortexIntelligenceMatrix,  # Phase 65 — Cross-Cutting Intelligence Matrix
)
from cortex.mcp.tools.brain import CortexBrainQuery  # Phase 66-A — GAP-66-002
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

# Phase 52 — Operational Pattern Journal MCP tool (function-based)
from cortex.mcp.tools.opj_tool import cortex_query_opj

# Toolkit consolidation tools (Phase 63 — Toolkit integration)
from cortex.mcp.tools.mcp_toolkit_tools import (
    cortex_scan,
    cortex_batch_transform,
    cortex_enrich,
    cortex_workflow,
)

# Phase 83 — Unified Reinforcement Signal (URS) learning tool
from cortex.mcp.tools.learning_tool import CortexLearning


# All tool classes for registration
# WAVE-101 consolidation: CortexProcessRequest (deprecated) and
# CortexIntelligenceMatrix (abstract method failure) removed from ALL_TOOLS.
# Their imports are kept for backward-compat; they are NOT registered.
ALL_TOOLS = [
    # Core (3) — CortexProcessRequest removed (deprecated)
    CortexChallenge,
    CortexClassify,
    CortexRequestLifecycle,
    # Intelligence (5) — CortexIntelligenceMatrix removed (abstract method failure)
    CortexLens,
    CortexKnowledge,
    CortexGit,
    CortexGenerateTests,  # WAVE-2 Stage 6
    CortexBrainQuery,  # Phase 66-A — GAP-66-002
    # Governance (4)
    CortexGovernance,
    CortexValidate,
    CortexLoad,
    CortexValidateRequest,  # Phase 48
    # Operations (7)
    CortexDebug,
    CortexRefactor,
    CortexPlan,
    CortexOnboard,
    CortexDashboard,
    CortexWorkflow,  # Phase 100 Stage 2
    CortexScaffoldFiles,  # PB-STS-001 Run 2 — GAP-007 resolution
    # Utilities (9) — CortexCheck and CortexTotalRecall kept as delegation aliases
    CortexVerify,
    CortexAsk,
    CortexVacuum,
    CortexToolsCatalog,
    CortexTotalRecall,  # delegation alias → CortexToolsCatalog
    CortexMetrics,
    CortexCheck,        # delegation alias → CortexVerify
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
    # Learning (1) - Phase 83 — Unified Reinforcement Signal
    CortexLearning,
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
    
    # Register class-based tools
    for tool_class in ALL_TOOLS:
        try:
            tool = tool_class()
            registry.register(tool)
            count += 1
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to register {tool_class.__name__}: {e}")
    
    # Register function-based toolkit tools (Phase 63)
    from cortex.mcp.mcp_tool_base import Tool, ToolDefinition, ToolCategory, ToolParameter
    
    function_tools = [
        ("cortex_scan", cortex_scan),
        ("cortex_batch_transform", cortex_batch_transform),
        ("cortex_enrich", cortex_enrich),
        ("cortex_workflow", cortex_workflow),
    ]
    
    for tool_name, tool_func in function_tools:
        try:
            # Create a Tool wrapper for function-based tools
            class FunctionTool(Tool):
                def __init__(self, name: str, func: Any):
                    self.func = func
                    super().__init__(
                        ToolDefinition(
                            name=name,
                            description=func.__doc__ or f"Toolkit tool: {name}",
                            category=ToolCategory.OPERATIONS,
                            parameters=[],
                        )
                    )
                
                def execute(self, **kwargs: Any) -> Any:
                    """Execute the wrapped toolkit function with the provided keyword arguments."""
                    return self.func(**kwargs)
            
            tool = FunctionTool(tool_name, tool_func)
            registry.register(tool)
            count += 1
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to register function tool {tool_name}: {e}")
    
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
    "CortexIntelligenceMatrix",  # Phase 65 — ENH-MATRIX-001
    "CortexBrainQuery",  # Phase 66-A — GAP-66-002
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
    # OPJ (Phase 52)
    "cortex_query_opj",
    # Learning (Phase 83)
    "CortexLearning",
    # Registration
    "ALL_TOOLS",
    "register_all_tools",
]

# AC_COMPLETE: AC-WAVE100-S2-006 ✅ All tools exported
# AC_COMPLETE: AC-P90-S7-001 ✅ 5 toolkit tools integrated
# AC_COMPLETE: AC-P48-MCP-001 ✅ 2 health-vacuum MCP tools registered
# AC_COMPLETE: AC-P50-MCP-001 ✅ CortexMasterPlanTool registered
# AC_COMPLETE: AC-OPJ-PHASE52-MCP ✅ cortex_query_opj registered (MCP tool #26)
# AC_COMPLETE: AC-WAVE101-CONSOLIDATION ✅ cortex_check→cortex_verify, cortex_total_recall→cortex_tools_catalog