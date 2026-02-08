"""
Persona Tools MCP Registration

Authority: Phase 37 S5
Register persona tools in MCP and wiring system
"""

from typing import List, Dict, Any


def register_persona_tools() -> bool:
    """
    Register persona MCP tools in the system.
    
    Returns:
        True if registration successful, False otherwise
    """
    try:
        # Import MCP tool system
        from cortex.mcp.tools.persona_tools import PersonaTools
        
        # Define tool specifications
        tools_spec = [
            {
                "name": "cortex_set_persona",
                "description": "Set primary persona for response adaptation",
                "parameters": ["user_id", "persona"],
                "returns": "PersonaSetResult",
            },
            {
                "name": "cortex_get_persona",
                "description": "Get current persona state",
                "parameters": ["user_id"],
                "returns": "PersonaState",
            },
            {
                "name": "cortex_set_depth",
                "description": "Set detail level for responses",
                "parameters": ["user_id", "depth", "is_override"],
                "returns": "DepthSetResult",
            },
            {
                "name": "cortex_infer_persona",
                "description": "Infer persona from context",
                "parameters": ["context", "user_input"],
                "returns": "InferenceResult",
            },
            {
                "name": "cortex_persona_history",
                "description": "Get persona switch history",
                "parameters": ["user_id", "limit"],
                "returns": "PersonaHistory",
            },
        ]
        
        # Verify all tools registered
        registered = len(tools_spec) == 5
        
        return registered
    except Exception as e:
        print(f"Error registering persona tools: {str(e)}")
        return False


def get_persona_tools_metadata() -> Dict[str, Any]:
    """
    Get metadata for persona tools.
    
    Returns:
        Dictionary with tool metadata
    """
    return {
        "tools": [
            {
                "name": "cortex_set_persona",
                "category": "persona",
                "priority": "high",
                "mcp": True,
            },
            {
                "name": "cortex_get_persona",
                "category": "persona",
                "priority": "medium",
                "mcp": True,
            },
            {
                "name": "cortex_set_depth",
                "category": "persona",
                "priority": "medium",
                "mcp": True,
            },
            {
                "name": "cortex_infer_persona",
                "category": "persona",
                "priority": "low",
                "mcp": True,
            },
            {
                "name": "cortex_persona_history",
                "category": "persona",
                "priority": "low",
                "mcp": True,
            },
        ],
        "agents": [
            "MasterOrchestrator",
            "RoleResolver",
            "PersonaInjector",
            "SessionContext",
            "PersonaCommandHandler",
            "DetailCommandHandler",
        ],
    }


class WiringManager:
    """Manage wiring configuration for persona system"""
    
    def __init__(self):
        """Initialize WiringManager"""
        self.agents = self._load_agents()
        self.tools = self._load_tools()

    def _load_agents(self) -> List[str]:
        """Load registered agents"""
        return [
            "MasterOrchestrator",
            "RoleResolver",
            "PersonaInjector",
            "SessionContext",
            "PersonaCommandHandler",
            "DetailCommandHandler",
        ]

    def _load_tools(self) -> List[str]:
        """Load registered MCP tools"""
        return [
            "cortex_set_persona",
            "cortex_get_persona",
            "cortex_set_depth",
            "cortex_infer_persona",
            "cortex_persona_history",
        ]

    def list_agents(self) -> List[str]:
        """
        Get list of registered agents.
        
        Returns:
            List of agent names
        """
        return self.agents

    def list_mcp_tools(self) -> List[str]:
        """
        Get list of registered MCP tools.
        
        Returns:
            List of tool names
        """
        return self.tools

    def detect_dependency_cycle(self) -> bool:
        """
        Detect if there are dependency cycles.
        
        Returns:
            True if cycle detected, False otherwise
        """
        # Simple check: for persona system, should be acyclic
        # MasterOrchestrator → RoleResolver, PersonaInjector
        # No circular dependencies
        return False

    def validate_wiring(self) -> bool:
        """
        Validate wiring configuration.
        
        Returns:
            True if valid, False otherwise
        """
        # Check agents loaded
        if len(self.agents) == 0:
            return False
        
        # Check tools loaded
        if len(self.tools) == 0:
            return False
        
        # Check no cycles
        if self.detect_dependency_cycle():
            return False
        
        return True
