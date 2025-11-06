"""
CORTEX Agents Package

This package contains all specialist agents for the CORTEX intelligence layer.
Each agent inherits from BaseAgent and implements specific capabilities.

Agent Types:
- Foundation: IntentRouter, WorkPlanner, HealthValidator
- Execution: CodeExecutor, TestGenerator, ErrorCorrector
- Advanced: SessionResumer, ScreenshotAnalyzer, ChangeGovernor, CommitHandler

Usage:
    from CORTEX.src.cortex_agents import IntentRouter, WorkPlanner
    from CORTEX.src.cortex_agents.base_agent import AgentRequest
    
    router = IntentRouter(tier1_api, tier2_kg, tier3_context)
    request = AgentRequest(intent="plan", context={}, user_message="Build feature")
    response = router.execute(request)
"""

from CORTEX.src.cortex_agents.base_agent import (
    BaseAgent,
    AgentRequest,
    AgentResponse,
)
from CORTEX.src.cortex_agents.agent_types import (
    AgentType,
    IntentType,
    Priority,
)

__version__ = "1.0.0"
__all__ = [
    "BaseAgent",
    "AgentRequest",
    "AgentResponse",
    "AgentType",
    "IntentType",
    "Priority",
]
