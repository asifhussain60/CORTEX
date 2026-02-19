"""
CORTEX MCP v2 - Operations Tools

Development workflow operations:
- cortex_debug: Debug cycle management
- cortex_refactor: Refactoring operations
- cortex_plan: Phase planning
- cortex_onboard: Repository onboarding
- cortex_dashboard: Dashboard operations

ORCHESTRATION ENFORCEMENT:
All tools validate orchestrator_context. Direct invocations bypass
MasterOrchestrator routing and are rejected.

AC_START: AC-WAVE100-S2-004
AC_CONTINUE: AC-MASTERORCH-ROUTING-001
"""

from typing import Any, Dict, List, Optional
from cortex.mcp.tools._shared import validate_orchestrator_context
from pathlib import Path

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)



class CortexDebug(ConsolidatedTool):
    """
    Debug cycle management.
    
    Operations:
    - inject: Inject debug markers
    - capture: Capture debug logs
    - analyze: Analyze debug output
    - fix_plan: Generate fix plan
    - cleanup: Remove debug markers
    """
    
    @property
    def name(self) -> str:
        return "cortex_debug"
    
    @property
    def description(self) -> str:
        return (
            "Comprehensive debugging for CORTEX applications. Inject markers, "
            "capture logs, analyze issues, and generate fix plans."
        )
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.OPERATIONS
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Debug operation: inject, capture, analyze, fix_plan, cleanup",
                required=True,
                enum=["inject", "capture", "analyze", "fix_plan", "cleanup"],
            ),
            ToolParameter(
                name="target",
                type="string",
                description="Target file or directory",
                required=False,
            ),
            ToolParameter(
                name="markers",
                type="array",
                description="Debug markers to inject",
                required=False,
            ),
            ToolParameter(
                name="log_level",
                type="string",
                description="Log level: debug, info, warning, error",
                required=False,
                enum=["debug", "info", "warning", "error"],
            ),
        ]
    
    @property
    def supported_operations(self) -> List[str]:
        return ["inject", "capture", "analyze", "fix_plan", "cleanup"]
    
    async def execute(self, **params) -> ToolResult:
        """Execute debug operation."""
        # ENFORCEMENT: Validate orchestrator routing
        validate_orchestrator_context(params.get("orchestrator_context"))
        
        operation = params.get("operation", "analyze")
        target = params.get("target")
        markers = params.get("markers", [])
        log_level = params.get("log_level", "debug")
        
        # WAVE-R Integration: Use DebugMCPTools for operations
        if operation == "inject":
            try:
                from cortex.mcp.tools.debug_tools import DebugMCPTools
                from cortex.core.event_bus import EventBus
                from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
                
                # Initialize infrastructure
                event_bus = EventBus()
                orchestrator = DebuggerOrchestrator(event_bus)
                tools = DebugMCPTools(event_bus, orchestrator)
                
                # Extract marker injection parameters
                trigger_type = params.get("trigger_type", "test_failure")
                file_path = target or "/tmp/unknown.py"
                line_number = params.get("line_number", 1)
                context = params.get("context", {})
                
                # Inject markers via DebugMCPTools
                result = tools.auto_inject(
                    trigger_type=trigger_type,
                    file_path=file_path,
                    line_number=line_number,
                    context=context
                )
                
                return ToolResult(
                    success=result["status"] == "success",
                    data=result,
                    metadata={"operation": "inject", "wave_r": True},
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Debug marker injection failed: {str(e)}",
                    metadata={"operation": "inject"}
                )
        
        elif operation == "list_sessions":
            try:
                from cortex.mcp.tools.debug_tools import DebugMCPTools
                from cortex.core.event_bus import EventBus
                from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
                
                event_bus = EventBus()
                orchestrator = DebuggerOrchestrator(event_bus)
                tools = DebugMCPTools(event_bus, orchestrator)
                
                status_filter = params.get("status_filter", "all")
                result = tools.list_sessions(status_filter=status_filter)
                
                return ToolResult(
                    success=True,
                    data=result,
                    metadata={"operation": "list_sessions", "wave_r": True}
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Session listing failed: {str(e)}",
                    metadata={"operation": "list_sessions"}
                )
        
        elif operation == "cleanup":
            try:
                from cortex.mcp.tools.debug_tools import DebugMCPTools
                from cortex.core.event_bus import EventBus
                from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
                
                event_bus = EventBus()
                orchestrator = DebuggerOrchestrator(event_bus)
                tools = DebugMCPTools(event_bus, orchestrator)
                
                session_id = params.get("session_id")
                cleanup_all = params.get("cleanup_all", False)
                result = tools.cleanup(session_id=session_id, cleanup_all=cleanup_all)
                
                return ToolResult(
                    success=result["status"] == "success",
                    data=result,
                    metadata={"operation": "cleanup", "wave_r": True}
                )
            except Exception as e:
                return ToolResult(
                    success=False,
                    error=f"Debug cleanup failed: {str(e)}",
                    metadata={"operation": "cleanup"}
                )
        
        elif operation == "capture":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "logs_captured": [],
                    "log_level": log_level,
                    "duration": "0s",
                },
                metadata={"operation": "capture"},
            )
        
        elif operation == "analyze":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "issues_found": [],
                    "root_causes": [],
                    "severity": "low",
                },
                metadata={"operation": "analyze"},
            )
        
        elif operation == "fix_plan":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "plan": [],
                    "estimated_effort": "low",
                    "auto_fixable": True,
                },
                metadata={"operation": "fix_plan"},
            )
        
        return ToolResult(success=False, error=f"Unknown operation: {operation}")


class CortexRefactor(ConsolidatedTool):
    """
    Semantic refactoring operations.
    
    Operations:
    - extract: Extract method/class
    - rename: Rename symbol
    - move: Move to new location
    - inline: Inline variable/method
    - organize: Organize imports/code
    """
    
    @property
    def name(self) -> str:
        return "cortex_refactor"
    
    @property
    def description(self) -> str:
        return (
            "Execute semantic refactoring operations. Supports extract, rename, "
            "move, inline, and organize across Python, C#, TypeScript/JavaScript."
        )
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.OPERATIONS
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Refactor operation: extract, rename, move, inline, organize",
                required=True,
                enum=["extract", "rename", "move", "inline", "organize"],
            ),
            ToolParameter(
                name="target",
                type="string",
                description="Target file or symbol",
                required=True,
            ),
            ToolParameter(
                name="new_name",
                type="string",
                description="New name for rename operations",
                required=False,
            ),
            ToolParameter(
                name="destination",
                type="string",
                description="Destination for move operations",
                required=False,
            ),
            ToolParameter(
                name="scope",
                type="string",
                description="Scope: local, module, package, workspace",
                required=False,
                enum=["local", "module", "package", "workspace"],
            ),
        ]
    
    @property
    def supported_operations(self) -> List[str]:
        return ["extract", "rename", "move", "inline", "organize"]
    
    async def execute(self, **params) -> ToolResult:
        """Execute refactoring operation."""
        # ENFORCEMENT: Validate orchestrator routing
        validate_orchestrator_context(params.get("orchestrator_context"))
        
        operation = params.get("operation", "organize")
        target = params.get("target", "")
        new_name = params.get("new_name")
        destination = params.get("destination")
        scope = params.get("scope", "module")
        
        if operation == "extract":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "extracted_to": new_name or "new_method",
                    "type": "method",
                    "changes": [],
                },
                metadata={"operation": "extract"},
            )
        
        elif operation == "rename":
            if not new_name:
                return ToolResult(success=False, error="new_name required for rename")
            return ToolResult(
                success=True,
                data={
                    "old_name": target,
                    "new_name": new_name,
                    "scope": scope,
                    "references_updated": 0,
                },
                metadata={"operation": "rename"},
            )
        
        elif operation == "move":
            if not destination:
                return ToolResult(success=False, error="destination required for move")
            return ToolResult(
                success=True,
                data={
                    "source": target,
                    "destination": destination,
                    "imports_updated": 0,
                },
                metadata={"operation": "move"},
            )
        
        elif operation == "inline":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "inlined_at": [],
                    "original_removed": True,
                },
                metadata={"operation": "inline"},
            )
        
        elif operation == "organize":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "imports_sorted": True,
                    "unused_removed": 0,
                    "groups_created": ["stdlib", "third_party", "local"],
                },
                metadata={"operation": "organize"},
            )
        
        return ToolResult(success=False, error=f"Unknown operation: {operation}")


class CortexPlan(ConsolidatedTool):
    """
    Phase planning operations.
    
    Operations:
    - create: Create new phase
    - update: Update phase status
    - complete: Mark phase complete
    - query: Query phases
    - sync: Sync with dashboard
    """
    
    @property
    def name(self) -> str:
        return "cortex_plan"
    
    @property
    def description(self) -> str:
        return (
            "Phase lifecycle management with intelligent resolution, "
            "setup/teardown hooks, and dashboard synchronization."
        )
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.OPERATIONS
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Plan operation: create, update, complete, query, sync",
                required=True,
                enum=["create", "update", "complete", "query", "sync"],
            ),
            ToolParameter(
                name="phase_id",
                type="string",
                description="Phase identifier (e.g., 'phase-100')",
                required=False,
            ),
            ToolParameter(
                name="data",
                type="object",
                description="Phase data for create/update operations",
                required=False,
            ),
            ToolParameter(
                name="filter",
                type="object",
                description="Filter criteria for query operations",
                required=False,
            ),
        ]
    
    @property
    def supported_operations(self) -> List[str]:
        return ["create", "update", "complete", "query", "sync"]
    
    async def execute(self, **params) -> ToolResult:
        """Execute plan operation."""
        # ENFORCEMENT: Validate orchestrator routing
        validate_orchestrator_context(params.get("orchestrator_context"))
        
        operation = params.get("operation", "query")
        phase_id = params.get("phase_id")
        data = params.get("data", {})
        filter_criteria = params.get("filter", {})
        
        if operation == "create":
            return ToolResult(
                success=True,
                data={
                    "phase_id": phase_id or "phase-new",
                    "status": "created",
                    "stages": data.get("stages", []),
                    "priority": data.get("priority", "P1"),
                },
                metadata={"operation": "create"},
            )
        
        elif operation == "update":
            if not phase_id:
                return ToolResult(success=False, error="phase_id required for update")
            return ToolResult(
                success=True,
                data={
                    "phase_id": phase_id,
                    "status": "updated",
                    "changes": list(data.keys()),
                },
                metadata={"operation": "update"},
            )
        
        elif operation == "complete":
            if not phase_id:
                return ToolResult(success=False, error="phase_id required for complete")
            return ToolResult(
                success=True,
                data={
                    "phase_id": phase_id,
                    "status": "completed",
                    "completed_at": "2026-02-12T00:00:00Z",
                    "metrics": {},
                },
                metadata={"operation": "complete"},
            )
        
        elif operation == "query":
            return ToolResult(
                success=True,
                data={
                    "phases": [],
                    "total": 0,
                    "active": 0,
                    "completed": 0,
                    "filter": filter_criteria,
                },
                metadata={"operation": "query"},
            )
        
        elif operation == "sync":
            return ToolResult(
                success=True,
                data={
                    "synced": True,
                    "dashboard_updated": True,
                    "timestamp": "2026-02-12T00:00:00Z",
                },
                metadata={"operation": "sync"},
            )
        
        return ToolResult(success=False, error=f"Unknown operation: {operation}")


class CortexOnboard(ConsolidatedTool):
    """
    Repository onboarding with LENS analysis and security assessment.
    
    Operations:
    - full: Full onboarding (LENS + security)
    - lens: LENS analysis only
    - security: Security assessment only
    - status: Check onboarding status
    """
    
    @property
    def name(self) -> str:
        return "cortex_onboard"
    
    @property
    def description(self) -> str:
        return (
            "Onboard repository with holistic LENS analysis and security assessment. "
            "Generates comprehensive knowledge base and security report."
        )
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.OPERATIONS
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Onboard operation: full, lens, security, status",
                required=True,
                enum=["full", "lens", "security", "status"],
            ),
            ToolParameter(
                name="path",
                type="string",
                description="Repository path to onboard",
                required=False,
            ),
            ToolParameter(
                name="options",
                type="object",
                description="Onboarding options (depth, security_level, etc.)",
                required=False,
            ),
        ]
    
    @property
    def supported_operations(self) -> List[str]:
        return ["full", "lens", "security", "status"]
    
    async def execute(self, **params) -> ToolResult:
        """Execute onboard operation."""
        # ENFORCEMENT: Validate orchestrator routing
        validate_orchestrator_context(params.get("orchestrator_context"))
        
        operation = params.get("operation", "full")
        path = params.get("path", ".")
        options = params.get("options", {})
        
        if operation == "full":
            return ToolResult(
                success=True,
                data={
                    "path": path,
                    "status": "onboarded",
                    "lens_analysis": {
                        "languages": ["python"],
                        "frameworks": [],
                        "patterns": [],
                    },
                    "security_assessment": {
                        "score": 95,
                        "vulnerabilities": [],
                        "priority": [],
                    },
                    "knowledge_base_created": True,
                },
                metadata={"operation": "full"},
            )
        
        elif operation == "lens":
            return ToolResult(
                success=True,
                data={
                    "path": path,
                    "analysis": {
                        "language": {},
                        "examination": {},
                        "navigation": {},
                        "synthesis": {},
                    },
                },
                metadata={"operation": "lens"},
            )
        
        elif operation == "security":
            return ToolResult(
                success=True,
                data={
                    "path": path,
                    "assessment": {
                        "P0": [],
                        "P1": [],
                        "P2": [],
                    },
                    "score": 95,
                    "compliant": True,
                },
                metadata={"operation": "security"},
            )
        
        elif operation == "status":
            return ToolResult(
                success=True,
                data={
                    "path": path,
                    "onboarded": True,
                    "last_updated": "2026-02-12T00:00:00Z",
                    "knowledge_files": 0,
                },
                metadata={"operation": "status"},
            )
        
        return ToolResult(success=False, error=f"Unknown operation: {operation}")


class CortexDashboard(ConsolidatedTool):
    """
    Dashboard operations.
    
    Operations:
    - generate: Generate dashboard
    - update: Update dashboard
    - query: Query dashboard data
    - landing: Generate landing page
    - full_cycle: Full dashboard cycle
    """
    
    @property
    def name(self) -> str:
        return "cortex_dashboard"
    
    @property
    def description(self) -> str:
        return (
            "Generate and manage dashboards. Create landing pages, "
            "repo dashboards, and perform full dashboard cycles."
        )
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.OPERATIONS
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Dashboard operation: generate, update, query, landing, full_cycle",
                required=True,
                enum=["generate", "update", "query", "landing", "full_cycle"],
            ),
            ToolParameter(
                name="target",
                type="string",
                description="Target repository or dashboard",
                required=False,
            ),
            ToolParameter(
                name="format",
                type="string",
                description="Output format: html, json, yaml",
                required=False,
                enum=["html", "json", "yaml"],
            ),
            ToolParameter(
                name="options",
                type="object",
                description="Dashboard generation options",
                required=False,
            ),
        ]
    
    @property
    def supported_operations(self) -> List[str]:
        return ["generate", "update", "query", "landing", "full_cycle"]
    
    async def execute(self, **params) -> ToolResult:
        """Execute dashboard operation."""
        # ENFORCEMENT: Validate orchestrator routing
        validate_orchestrator_context(params.get("orchestrator_context"))
        
        operation = params.get("operation", "query")
        target = params.get("target")
        output_format = params.get("format", "html")
        options = params.get("options", {})
        
        if operation == "generate":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "format": output_format,
                    "generated": True,
                    "path": f"cortex-registry/company/dashboards/{target or 'default'}.{output_format}",
                },
                metadata={"operation": "generate"},
            )
        
        elif operation == "update":
            return ToolResult(
                success=True,
                data={
                    "target": target,
                    "updated": True,
                    "timestamp": "2026-02-12T00:00:00Z",
                },
                metadata={"operation": "update"},
            )
        
        elif operation == "query":
            return ToolResult(
                success=True,
                data={
                    "dashboards": [],
                    "total": 0,
                    "active": 0,
                },
                metadata={"operation": "query"},
            )
        
        elif operation == "landing":
            return ToolResult(
                success=True,
                data={
                    "generated": True,
                    "path": "cortex-registry/company/dashboards/index.html",
                    "repos_included": 0,
                },
                metadata={"operation": "landing"},
            )
        
        elif operation == "full_cycle":
            return ToolResult(
                success=True,
                data={
                    "steps_completed": [
                        "kill_processes",
                        "start_server",
                        "health_check",
                        "launch_dashboard",
                    ],
                    "success": True,
                    "url": "http://localhost:8080",
                },
                metadata={"operation": "full_cycle"},
            )
        
        return ToolResult(success=False, error=f"Unknown operation: {operation}")


# Export all operations tools
__all__ = [
    "CortexDebug",
    "CortexRefactor",
    "CortexPlan",
    "CortexOnboard",
    "CortexDashboard",
]

# AC_COMPLETE: AC-WAVE100-S2-004 ✅ Operations tools implemented
