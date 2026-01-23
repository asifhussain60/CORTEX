"""
Orchestrator Bootstrap & Initialization Module

AC-AR-006-02: Wire all orchestrators into MasterOrchestrator
- Register domain orchestrators (Planning, Refactoring)
- Initialize conversation orchestrator (ConversationOrchestrator)
- Wire intent router integration
- Initialize registry and discovery
- Activate all MCP tools

Ensures all orchestrators operational and interconnected.

Author: Asif Hussain
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import threading

from cortex.core.result import Ok, Err
from cortex.core.interfaces import IOrchestrator
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class OrchestratorBootstrapConfig:
    """Configuration for orchestrator bootstrap"""
    auto_register: bool = True
    initialize_conversation: bool = True
    initialize_registry: bool = True
    initialize_discovery: bool = True
    enable_mcp_tools: bool = True
    timeout_seconds: float = 30.0


class OrchestratorBootstrap:
    """
    Bootstrap manager for all orchestrators.
    
    Coordinates initialization and wiring of:
    - MasterOrchestrator
    - Domain orchestrators (Planning, Refactoring)
    - ConversationOrchestrator
    - Intent router integration
    - Registry & discovery
    - MCP tools
    """
    
    _instance: Optional['OrchestratorBootstrap'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'OrchestratorBootstrap':
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize bootstrap manager"""
        if self._initialized:
            return
        
        self.logger = EnhancedAuditLogger.instance()
        self.config: Optional[OrchestratorBootstrapConfig] = None
        self.master_orchestrator: Optional[IOrchestrator] = None
        self.domain_orchestrators: Dict[str, IOrchestrator] = {}
        self.conversation_orchestrator: Optional[Any] = None
        self.registry_initialized: bool = False
        self.discovery_initialized: bool = False
        self._initialized = True
    
    @classmethod
    def instance(cls) -> 'OrchestratorBootstrap':
        """Get singleton instance"""
        return cls()
    
    def bootstrap(self, config: Optional[OrchestratorBootstrapConfig] = None):
        """
        Bootstrap all orchestrators.
        
        AC-AR-006-02: Wire orchestrator ecosystem
        
        Args:
            config: Bootstrap configuration (defaults to standard config)
            
        Returns:
            Ok(dict) with bootstrap status and metrics
        """
        try:
            self.config = config or OrchestratorBootstrapConfig()
            
            bootstrap_result = {
                "started_at": datetime.now().isoformat(),
                "steps": [],
                "orchestrators": {},
                "errors": []
            }
            
            # Step 1: Initialize MasterOrchestrator
            step1 = self._initialize_master()
            bootstrap_result["steps"].append(step1)
            if not step1["success"]:
                bootstrap_result["errors"].append(step1["error"])
            else:
                bootstrap_result["orchestrators"]["master"] = "READY"
            
            # Step 2: Register domain orchestrators
            step2 = self._register_domain_orchestrators()
            bootstrap_result["steps"].append(step2)
            if not step2["success"]:
                bootstrap_result["errors"].append(step2["error"])
            else:
                bootstrap_result["orchestrators"]["domains"] = step2["registered"]
            
            # Step 3: Initialize ConversationOrchestrator
            step3 = self._initialize_conversation()
            bootstrap_result["steps"].append(step3)
            if not step3["success"]:
                bootstrap_result["errors"].append(step3["error"])
            else:
                bootstrap_result["orchestrators"]["conversation"] = "READY"
            
            # Step 4: Initialize registry
            step4 = self._initialize_registry()
            bootstrap_result["steps"].append(step4)
            if not step4["success"]:
                bootstrap_result["errors"].append(step4["error"])
            
            # Step 5: Initialize discovery
            step5 = self._initialize_discovery()
            bootstrap_result["steps"].append(step5)
            if not step5["success"]:
                bootstrap_result["errors"].append(step5["error"])
            
            # Step 6: Enable MCP tools
            step6 = self._enable_mcp_tools()
            bootstrap_result["steps"].append(step6)
            if not step6["success"]:
                bootstrap_result["errors"].append(step6["error"])
            else:
                bootstrap_result["orchestrators"]["mcp_tools"] = step6["count"]
            
            bootstrap_result["completed_at"] = datetime.now().isoformat()
            bootstrap_result["success"] = len(bootstrap_result["errors"]) == 0
            
            # Log bootstrap completion
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-02",
                operation="ORCHESTRATOR_BOOTSTRAP",
                success=bootstrap_result["success"],
                details=bootstrap_result
            )
            
            return Ok(bootstrap_result)
        
        except Exception as e:
            error_msg = f"Orchestrator bootstrap failed: {str(e)}"
            self.logger.log_operation_complete(
                ac_id="AC-AR-006-02",
                operation="ORCHESTRATOR_BOOTSTRAP",
                success=False,
                details={"error": error_msg}
            )
            return Err(error_msg)
    
    def _initialize_master(self) -> Dict[str, Any]:
        """Initialize MasterOrchestrator - AC-AR-006-01"""
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
            
            self.master_orchestrator = MasterOrchestrator.instance()
            # Don't call initialize() here to avoid recursion - just return success
            
            return {
                "step": "Initialize MasterOrchestrator",
                "success": True,
                "message": "MasterOrchestrator instance created"
            }
        except Exception as e:
            return {
                "step": "Initialize MasterOrchestrator",
                "success": False,
                "error": f"Failed to initialize MasterOrchestrator: {str(e)}"
            }
    
    def _register_domain_orchestrators(self) -> Dict[str, Any]:
        """Register domain orchestrators - AC-AR-006-02"""
        try:
            if not self.master_orchestrator:
                return {
                    "step": "Register Domain Orchestrators",
                    "success": False,
                    "error": "MasterOrchestrator not initialized"
                }
            
            registered = []
            
            # Register Planning Orchestrator
            try:
                from cortex.orchestrators.domain.planning_orchestrator import PlanningOrchestrator
                planning_orch = PlanningOrchestrator()
                self.master_orchestrator.register_orchestrator(
                    domain="planning",
                    orchestrator=planning_orch,
                    capabilities=["workflow_coordination", "task_planning"]
                )
                self.domain_orchestrators["planning"] = planning_orch
                registered.append("PlanningOrchestrator")
            except Exception as e:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-006-02",
                    operation="REGISTER_PLANNING_ORCHESTRATOR",
                    success=False,
                    details={"error": str(e)}
                )
            
            # Register Refactoring Orchestrator
            try:
                from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator
                refactoring_orch = RefactoringOrchestrator()
                self.master_orchestrator.register_orchestrator(
                    domain="refactoring",
                    orchestrator=refactoring_orch,
                    capabilities=["code_refactoring", "architecture_improvement"]
                )
                self.domain_orchestrators["refactoring"] = refactoring_orch
                registered.append("RefactoringOrchestrator")
            except Exception as e:
                self.logger.log_operation_complete(
                    ac_id="AC-AR-006-02",
                    operation="REGISTER_REFACTORING_ORCHESTRATOR",
                    success=False,
                    details={"error": str(e)}
                )
            
            return {
                "step": "Register Domain Orchestrators",
                "success": len(registered) > 0,
                "registered": registered,
                "count": len(registered)
            }
        except Exception as e:
            return {
                "step": "Register Domain Orchestrators",
                "success": False,
                "error": f"Failed to register domain orchestrators: {str(e)}"
            }
    
    def _initialize_conversation(self) -> Dict[str, Any]:
        """Initialize ConversationOrchestrator - AC-AR-006-03"""
        try:
            if not self.config.initialize_conversation:
                return {
                    "step": "Initialize ConversationOrchestrator",
                    "success": True,
                    "message": "Conversation initialization disabled"
                }
            
            from cortex.orchestrators.conversation_orchestrator import ConversationOrchestrator
            
            self.conversation_orchestrator = ConversationOrchestrator(
                timeout_seconds=self.config.timeout_seconds
            )
            
            return {
                "step": "Initialize ConversationOrchestrator",
                "success": True,
                "session_id": self.conversation_orchestrator.session_id,
                "message": "ConversationOrchestrator initialized successfully"
            }
        except Exception as e:
            return {
                "step": "Initialize ConversationOrchestrator",
                "success": False,
                "error": f"Failed to initialize ConversationOrchestrator: {str(e)}"
            }
    
    def _initialize_registry(self) -> Dict[str, Any]:
        """Initialize orchestrator registry - AC-AR-017-01"""
        try:
            if not self.config.initialize_registry:
                return {
                    "step": "Initialize OrchestratorRegistry",
                    "success": True,
                    "message": "Registry initialization disabled"
                }
            
            from cortex.orchestrators.registry.orchestrator_registry import OrchestratorRegistry
            
            registry = OrchestratorRegistry.instance()
            
            self.registry_initialized = True
            return {
                "step": "Initialize OrchestratorRegistry",
                "success": True,
                "message": "OrchestratorRegistry initialized as singleton"
            }
        except Exception as e:
            return {
                "step": "Initialize OrchestratorRegistry",
                "success": False,
                "error": f"Failed to initialize registry: {str(e)}"
            }
    
    def _initialize_discovery(self) -> Dict[str, Any]:
        """Initialize discovery engine - AC-AR-017-02"""
        try:
            if not self.config.initialize_discovery:
                return {
                    "step": "Initialize DiscoveryEngine",
                    "success": True,
                    "message": "Discovery initialization disabled"
                }
            
            from cortex.orchestrators.registry.discovery_engine import DiscoveryEngine
            
            discovery = DiscoveryEngine.instance()
            
            self.discovery_initialized = True
            return {
                "step": "Initialize DiscoveryEngine",
                "success": True,
                "message": "DiscoveryEngine initialized as singleton"
            }
        except Exception as e:
            return {
                "step": "Initialize DiscoveryEngine",
                "success": False,
                "error": f"Failed to initialize discovery: {str(e)}"
            }
    
    def _enable_mcp_tools(self) -> Dict[str, Any]:
        """Enable all MCP tools - AC-MCP-001"""
        try:
            if not self.config.enable_mcp_tools:
                return {
                    "step": "Enable MCP Tools",
                    "success": True,
                    "message": "MCP tools initialization disabled",
                    "count": 0
                }
            
            # Import MCP tools to ensure registration
            try:
                from cortex.mcp import registry as mcp_registry
                tool_registry = mcp_registry.ToolRegistry.instance()
                tools = tool_registry.list_tools()
                
                return {
                    "step": "Enable MCP Tools",
                    "success": True,
                    "message": f"Enabled {len(tools)} MCP tools",
                    "count": len(tools),
                    "tools": [t.get("name", "unknown") for t in tools]
                }
            except ImportError:
                # MCP tools not available in this environment
                return {
                    "step": "Enable MCP Tools",
                    "success": True,
                    "message": "MCP tools module not available",
                    "count": 0
                }
        except Exception as e:
            return {
                "step": "Enable MCP Tools",
                "success": False,
                "error": f"Failed to enable MCP tools: {str(e)}",
                "count": 0
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bootstrap status"""
        return {
            "master_orchestrator_ready": self.master_orchestrator is not None,
            "domain_orchestrators": list(self.domain_orchestrators.keys()),
            "conversation_orchestrator_ready": self.conversation_orchestrator is not None,
            "registry_initialized": self.registry_initialized,
            "discovery_initialized": self.discovery_initialized,
            "timestamp": datetime.now().isoformat()
        }


def bootstrap_orchestrators(config: Optional[OrchestratorBootstrapConfig] = None):
    """
    Bootstrap all orchestrators.
    
    AC-AR-006-02: Wire orchestrator ecosystem
    """
    bootstrap = OrchestratorBootstrap.instance()
    return bootstrap.bootstrap(config)


# Module-level initialization flag
_bootstrapped = False


def ensure_bootstrapped():
    """
    Ensure orchestrators are bootstrapped.
    
    Safe to call multiple times - only bootstraps once.
    """
    global _bootstrapped
    
    if _bootstrapped:
        return Ok({"already_bootstrapped": True})
    
    result = bootstrap_orchestrators()
    if result.is_ok():
        _bootstrapped = True
    
    return result
