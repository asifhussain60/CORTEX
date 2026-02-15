# Agent Integration Guide

**Authority:** cortex-registry/_cortex-master/index.yaml PHASE-L  
**Created:** 2026-02-12  
**AC-ID:** AC-PHASE-L-002

---

## Overview

This guide explains how orchestrators integrate with CORTEX agents using the lazy loading and interaction patterns implemented in phase-81.

**Key Benefits:**
- 60-88% token reduction (245k → 30-95k)
- Intent-based agent routing
- Standardized request/response protocols
- Testable agent interactions

---

## Intent → Agent Mapping

### Core Mappings

| Intent | Primary Agents | Token Cost | Use Case |
|--------|---------------|------------|----------|
| **IMPLEMENT** | cortex-executor, cortex-architect, cortex-holistic-validator | ~95k | TDD implementation, feature development |
| **FIX** | cortex-executor, cortex-debugger | ~63k | Bug fixing, issue resolution |
| **REFACTOR** | cortex-architect, cortex-holistic-validator | ~75k | Code improvement, restructuring |
| **ANALYZE** | cortex-auditor, cortex-holistic-validator, cortex-meta-auditor | ~87k | Code analysis, quality assessment |
| **AUDIT** | cortex-auditor, cortex-meta-auditor | ~61k | Compliance checking, governance |
| **DESIGN** | cortex-architect, cortex-challenger | ~70k | System design, architecture |
| **PLAN** | cortex-planner | ~31k | Phase planning, task decomposition |
| **DIGEST** | cortex-auditor, cortex-meta-auditor | ~61k | Session learning, knowledge extraction |
| **QUERY** | cortex-educator | ~30k | Educational queries, documentation |

### Token Savings

**Eager Loading (all agents):** 245,000 tokens  
**Lazy Loading (per intent):** 30,000 - 95,000 tokens  
**Average Savings:** 67%

---

## Quick Start: Using Lazy Loader

### 1. Basic Usage

```python
from cortex.agents.lazy_loader import load_agents_for_intent
from cortex.models.canonical_enums import IntentType

# Load agents for specific intent
agents = load_agents_for_intent(IntentType.IMPLEMENT)

# Returns AgentMetadata instances
for agent in agents:
    print(f"{agent.name}: {agent.capabilities}")
    # Output: cortex-executor: ['tdd', 'validation', 'execution']
```

### 2. Advanced Usage

```python
from cortex.agents.lazy_loader import IntentAgentMapper
from pathlib import Path

# Initialize mapper with custom agent directory
mapper = IntentAgentMapper(agent_dir=Path(".github/agents/core"))

# Get agents for intent
agents = mapper.get_agents_for_intent(IntentType.ANALYZE)

# Calculate token savings
savings = mapper.get_token_savings(IntentType.ANALYZE)
print(f"Token savings: {savings['savings_percent']:.1f}%")
# Output: Token savings: 64.5%

# Check if agent supports intent
supports = mapper.supports_intent("cortex-executor", IntentType.FIX)
print(f"Supports FIX: {supports}")
# Output: Supports FIX: True
```

---

## Orchestrator Integration

### Pattern 1: Using OrchestratorAgentInvoker Mixin

```python
from cortex.agents.interaction_patterns import OrchestratorAgentInvoker
from cortex.agents.lazy_loader import load_agents_for_intent
from cortex.models.canonical_enums import IntentType

class TDDOrchestrator(OrchestratorAgentInvoker):
    """Orchestrator for TDD implementation."""
    
    def __init__(self):
        super().__init__()
        
        # Lazy load agents for IMPLEMENT intent
        agents = load_agents_for_intent(IntentType.IMPLEMENT)
        
        # Preload agents into bridge
        for agent_metadata in agents:
            agent_instance = self._instantiate_agent(agent_metadata)
            self.agent_bridge.preload_agent(
                agent_metadata.name,
                agent_instance
            )
    
    def execute_red_phase(self, test_spec: str):
        """Execute RED phase with validation."""
        
        # Validate test spec with cortex-holistic-validator
        validation_response = self.validate_with_agent(
            agent_name="cortex-holistic-validator",
            validation_target=test_spec,
            phase="RED",
        )
        
        if not validation_response.success:
            return validation_response
        
        # Execute test creation with cortex-executor
        execution_response = self.execute_with_agent(
            agent_name="cortex-executor",
            execution_context={
                "action": "create_test",
                "spec": test_spec,
            }
        )
        
        return execution_response
```

### Pattern 2: Direct Bridge Usage

```python
from cortex.agents.interaction_patterns import (
    AgentToOrchestratorBridge,
    AgentRequest,
    AgentResponseFormat,
)

class LENSOrchestrator:
    """Orchestrator for LENS analysis."""
    
    def __init__(self):
        self.bridge = AgentToOrchestratorBridge()
        self._load_agents()
    
    def _load_agents(self):
        """Lazy load agents for ANALYZE intent."""
        from cortex.agents.lazy_loader import load_agents_for_intent
        from cortex.models.canonical_enums import IntentType
        
        agents = load_agents_for_intent(IntentType.ANALYZE)
        for agent_metadata in agents:
            # Preload agent instances
            agent = self._instantiate_agent(agent_metadata)
            self.bridge.preload_agent(agent_metadata.name, agent)
    
    def analyze_code(self, target_file: str):
        """Analyze code with LENS agents."""
        
        # Invoke cortex-auditor for analysis
        response = self.bridge.invoke_agent(
            agent_name="cortex-auditor",
            operation="analyze",
            context={"target": target_file},
            format=AgentResponseFormat.STRUCTURED,
        )
        
        return response
```

---

## Agent Request/Response Protocol

### Request Structure

```python
from cortex.agents.interaction_patterns import AgentRequest, AgentResponseFormat

request = AgentRequest(
    agent_name="cortex-executor",
    operation="validate",
    context={
        "code": "def hello(): return 'world'",
        "strict": True,
    },
    format=AgentResponseFormat.STRUCTURED,
    metadata={"priority": "high"}
)
```

### Response Structure

```python
from cortex.agents.interaction_patterns import AgentResponse

response = AgentResponse(
    agent_name="cortex-executor",
    operation="validate",
    success=True,
    data={
        "valid": True,
        "issues": [],
        "confidence": 0.95,
    },
    errors=[],
    warnings=["Missing docstring"],
    metadata={"execution_time_ms": 42}
)
```

### Response Formatting

```python
from cortex.agents.interaction_patterns import format_agent_response_for_user

# Format response for user display
formatted = format_agent_response_for_user(response)
print(formatted)

# Output:
# ✅ **cortex-executor** (validate)
# 
# - **valid:** True
# - **issues:** []
# - **confidence:** 0.95
# 
# **Warnings:**
# - ⚠️ Missing docstring
```

---

## Response Format Types

### STRUCTURED (default)

Dictionary with sections:

```python
data = {
    "status": "complete",
    "results": {...},
    "metrics": {...}
}
```

### NARRATIVE

Markdown formatted text:

```python
data = """
## Analysis Results

The code quality is **excellent** with:
- 95% test coverage
- 0 critical issues
- 2 minor warnings
"""
```

### LIST

List of items:

```python
data = [
    "Issue 1: Missing type hints",
    "Issue 2: Unused imports",
    "Issue 3: Low complexity"
]
```

### TABLE

Tabular data:

```python
data = {
    "headers": ["File", "Coverage", "Issues"],
    "rows": [
        ["file1.py", "95%", "0"],
        ["file2.py", "87%", "2"],
    ]
}
```

---

## Testing Agent Interactions

### Unit Testing with Mocks

```python
import pytest
from unittest.mock import Mock
from cortex.agents.interaction_patterns import AgentResponse

def test_orchestrator_agent_invocation():
    """Test orchestrator invokes agent correctly."""
    
    # Create mock agent
    mock_agent = Mock()
    mock_agent.execute.return_value = AgentResponse(
        agent_name="cortex-executor",
        operation="validate",
        success=True,
        data={"valid": True}
    )
    
    # Create orchestrator
    orchestrator = TDDOrchestrator()
    orchestrator.agent_bridge.preload_agent("cortex-executor", mock_agent)
    
    # Test invocation
    response = orchestrator.validate_with_agent(
        agent_name="cortex-executor",
        validation_target="test_code.py"
    )
    
    assert response.success is True
    mock_agent.execute.assert_called_once()
```

### Integration Testing

```python
def test_real_agent_integration():
    """Test with real agent instances."""
    from cortex.agents.lazy_loader import load_agents_for_intent
    from cortex.models.canonical_enums import IntentType
    
    # Load real agents
    agents = load_agents_for_intent(IntentType.IMPLEMENT)
    
    # Verify agents loaded
    assert len(agents) > 0
    
    # Verify token cost
    total_cost = sum(agent.token_cost for agent in agents)
    assert total_cost < 100_000  # Lazy loading target
```

---

## Best Practices

### 1. Use Intent-Based Loading

✅ **DO:**
```python
# Load only required agents
agents = load_agents_for_intent(IntentType.IMPLEMENT)
```

❌ **DON'T:**
```python
# Load all agents (245k tokens!)
from cortex.agents import all_agents
```

### 2. Preload Agents at Initialization

✅ **DO:**
```python
class MyOrchestrator(OrchestratorAgentInvoker):
    def __init__(self):
        super().__init__()
        agents = load_agents_for_intent(self.intent)
        for agent in agents:
            self.agent_bridge.preload_agent(agent.name, agent_instance)
```

❌ **DON'T:**
```python
# Load agents on every invocation (slow)
def execute(self):
    agents = load_agents_for_intent(self.intent)
    # ...
```

### 3. Use Standardized Request/Response

✅ **DO:**
```python
response = self.validate_with_agent(
    agent_name="cortex-validator",
    validation_target=code,
)
```

❌ **DON'T:**
```python
# Direct method calls bypass protocol
result = agent.validate(code)
```

### 4. Handle Errors Gracefully

✅ **DO:**
```python
response = bridge.invoke_agent(...)
if not response.success:
    for error in response.errors:
        logger.error(f"Agent error: {error}")
    return fallback_behavior()
```

❌ **DON'T:**
```python
# Assume success
result = bridge.invoke_agent(...)
return result.data  # May be None!
```

---

## Performance Metrics

### Token Usage by Intent

```
QUERY:     30,000 tokens (-88% vs eager)
PLAN:      31,000 tokens (-87% vs eager)
FIX:       63,000 tokens (-74% vs eager)
AUDIT:     61,000 tokens (-75% vs eager)
DESIGN:    70,000 tokens (-71% vs eager)
REFACTOR:  75,000 tokens (-69% vs eager)
ANALYZE:   87,000 tokens (-64% vs eager)
IMPLEMENT: 95,000 tokens (-61% vs eager)
DIGEST:    61,000 tokens (-75% vs eager)

Eager (all agents): 245,000 tokens
Average savings: 67%
```

### Load Times

- **Lazy loading:** <100ms (per intent)
- **Eager loading:** ~500ms (all agents)
- **Cache hit:** <1ms

---

## Troubleshooting

### Issue: Agent Not Found

**Symptom:** `AgentResponse.success = False`, error "Agent not found"

**Solution:**
```python
# Check agent is in intent map
from cortex.agents.lazy_loader import IntentAgentMapper
mapper = IntentAgentMapper()
agents = mapper.get_agents_for_intent(IntentType.IMPLEMENT)
print([a.name for a in agents])

# Verify agent file exists
from pathlib import Path
agent_file = Path(".github/agents/core/cortex-executor.md")
assert agent_file.exists()
```

### Issue: High Token Usage

**Symptom:** Token usage > 100k for single intent

**Solution:**
```python
# Calculate token savings
savings = mapper.get_token_savings(IntentType.IMPLEMENT)
print(f"Using {savings['lazy_loading']} tokens")

# If still high, check agent metadata
for agent in agents:
    print(f"{agent.name}: {agent.token_cost} tokens")
```

### Issue: Agent Execution Failure

**Symptom:** `AgentResponse.success = False`, agent exception

**Solution:**
```python
# Check response errors
response = bridge.invoke_agent(...)
if not response.success:
    print("Errors:")
    for error in response.errors:
        print(f"  - {error}")
    
    # Check agent implementation
    # Verify agent has execute() method
    # Check agent.capabilities matches operation
```

---

## Migration from Direct Imports

### Before (Direct Import)

```python
from cortex.agents.executor import CortexExecutor

class TDDOrchestrator:
    def __init__(self):
        self.executor = CortexExecutor()  # Direct instantiation
    
    def execute(self, code):
        return self.executor.validate(code)  # Direct method call
```

### After (Lazy Loading + Bridge)

```python
from cortex.agents.lazy_loader import load_agents_for_intent
from cortex.agents.interaction_patterns import OrchestratorAgentInvoker
from cortex.models.canonical_enums import IntentType

class TDDOrchestrator(OrchestratorAgentInvoker):
    def __init__(self):
        super().__init__()
        
        # Lazy load agents
        agents = load_agents_for_intent(IntentType.IMPLEMENT)
        for agent in agents:
            self.agent_bridge.preload_agent(agent.name, agent_instance)
    
    def execute(self, code):
        # Use standardized protocol
        return self.validate_with_agent(
            agent_name="cortex-executor",
            validation_target=code,
        )
```

**Benefits:**
- ✅ 67% token reduction
- ✅ Testable with mocks
- ✅ Standardized protocol
- ✅ Intent-based routing

---

## Reference

### Key Files

- `cortex/agents/lazy_loader.py` - Intent-based agent loading
- `cortex/agents/interaction_patterns.py` - Request/response protocols
- `tests/unit/agents/test_lazy_loader.py` - Lazy loader tests
- `tests/unit/agents/test_interaction_patterns.py` - Protocol tests

### Related Documentation

- `.github/agents/core/` - Agent specifications
- `cortex-registry/_cortex-master/index.yaml` - Phase tracking (PHASE-L)

---

**Last Updated:** 2026-02-12  
**Version:** 1.0.0  
**Phase:** phase-81 (Agent Architecture Redesign)
