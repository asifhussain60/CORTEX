# Building Your First Orchestrator

**Last Updated:** 2026-01-20  
**Version:** 1.0.0  
**Status:** Production Ready  
**Audience:** Developers, Integrators

## Overview

This tutorial guides you through building a custom CORTEX orchestrator from scratch. You'll learn the core patterns including the `OrchestratorBase` class, `ConversationProtocol`, and how orchestrators integrate with the governance framework.

**Time Required:** 30-45 minutes  
**Prerequisites:** [Installation](0-installation.md) and [Quick Start](1-quickstart.md) completed

---

## Table of Contents

1. [Understanding Orchestrators](#understanding-orchestrators)
2. [Project Setup](#project-setup)
3. [Basic Orchestrator](#basic-orchestrator)
4. [Adding Conversation Support](#adding-conversation-support)
5. [Integrating Governance](#integrating-governance)
6. [Testing Your Orchestrator](#testing-your-orchestrator)
7. [Registration and Deployment](#registration-and-deployment)
8. [Next Steps](#next-steps)

---

## Understanding Orchestrators

### What is an Orchestrator?

An orchestrator in CORTEX is a specialized component that:

1. **Receives intent** from users or systems
2. **Processes through LENS** for comprehension
3. **Executes business logic** with governance checks
4. **Returns structured responses** with audit trails

### Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Your Custom Orchestrator                     │
├─────────────────────────────────────────────────────────────────┤
│  OrchestratorBase                                               │
│  ├── LENS Protocol Integration                                  │
│  ├── Governance Hooks                                           │
│  ├── ConversationProtocol Support                               │
│  └── Audit Trail Generation                                     │
├─────────────────────────────────────────────────────────────────┤
│  Your Business Logic                                            │
│  ├── Custom Processing                                          │
│  ├── External Integrations                                      │
│  └── Domain-Specific Rules                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Orchestrator Lifecycle

```
1. INIT       → Configure, load rules
2. RECEIVE    → Accept intent/request
3. COMPREHEND → LENS Protocol processing
4. VALIDATE   → Governance checks
5. EXECUTE    → Business logic
6. COMPOSE    → Response formatting
7. AUDIT      → Trail generation
8. RESPOND    → Return result
```

---

## Project Setup

### Directory Structure

Create a new orchestrator package:

```bash
mkdir -p src/orchestrators/my_first
cd src/orchestrators/my_first
touch __init__.py orchestrator.py config.py tests/__init__.py tests/test_orchestrator.py
```

Expected structure:

```
src/orchestrators/my_first/
├── __init__.py
├── orchestrator.py      # Main orchestrator logic
├── config.py            # Configuration
└── tests/
    ├── __init__.py
    └── test_orchestrator.py
```

### Configuration File

Create `config.py`:

```python
"""Configuration for MyFirst orchestrator."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MyFirstConfig:
    """Configuration for the MyFirst orchestrator."""
    
    # Identification
    name: str = "my-first-orchestrator"
    version: str = "1.0.0"
    description: str = "My first custom CORTEX orchestrator"
    
    # Governance
    governance_tier: int = 3  # Tier 3 = application logic
    required_rules: List[str] = field(default_factory=lambda: [
        "CORE-001",  # Safe operations only
        "CORE-002",  # Audit trail required
    ])
    
    # Behavior
    max_turns: int = 10
    timeout_seconds: float = 30.0
    enable_lens: bool = True
    
    # Response composition
    default_mode: str = "balanced"
    default_tone: str = "professional"
    
    # Resilience
    retry_attempts: int = 3
    circuit_breaker_threshold: int = 5


# Default configuration instance
DEFAULT_CONFIG = MyFirstConfig()
```

---

## Basic Orchestrator

### Minimal Implementation

Create `orchestrator.py`:

```python
"""MyFirst Orchestrator - A simple custom orchestrator."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid

from src.orchestrators.base import OrchestratorBase, OrchestratorResult
from src.orchestrators.my_first.config import MyFirstConfig, DEFAULT_CONFIG


class ProcessingStatus(Enum):
    """Status of orchestrator processing."""
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    GOVERNANCE_BLOCKED = "governance_blocked"


@dataclass
class MyFirstResult(OrchestratorResult):
    """Result from MyFirst orchestrator."""
    
    status: ProcessingStatus
    data: Dict[str, Any] = field(default_factory=dict)
    messages: List[str] = field(default_factory=list)
    execution_time_ms: float = 0.0
    

class MyFirstOrchestrator(OrchestratorBase):
    """
    A simple custom orchestrator demonstrating CORTEX patterns.
    
    This orchestrator:
    - Accepts text input
    - Processes through basic validation
    - Returns structured results with audit trail
    """
    
    def __init__(self, config: Optional[MyFirstConfig] = None):
        """Initialize the orchestrator.
        
        Args:
            config: Optional configuration override
        """
        self.config = config or DEFAULT_CONFIG
        self._session_id = str(uuid.uuid4())
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize orchestrator resources."""
        if self._initialized:
            return
            
        # Load any required resources
        # Connect to external services
        # Validate configuration
        
        self._initialized = True
        
    async def process(self, intent: str, context: Optional[Dict[str, Any]] = None) -> MyFirstResult:
        """Process an intent through the orchestrator.
        
        Args:
            intent: The user's intent or request
            context: Optional additional context
            
        Returns:
            MyFirstResult with processing outcome
        """
        start_time = datetime.utcnow()
        context = context or {}
        
        try:
            # Step 1: Validate input
            if not intent or not intent.strip():
                return MyFirstResult(
                    status=ProcessingStatus.ERROR,
                    messages=["Empty intent provided"],
                )
            
            # Step 2: Basic processing
            processed_intent = intent.strip().lower()
            word_count = len(processed_intent.split())
            
            # Step 3: Apply business logic
            result_data = {
                "original_intent": intent,
                "processed_intent": processed_intent,
                "word_count": word_count,
                "session_id": self._session_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Step 4: Generate response
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return MyFirstResult(
                status=ProcessingStatus.SUCCESS,
                data=result_data,
                messages=[f"Successfully processed intent with {word_count} words"],
                execution_time_ms=execution_time,
            )
            
        except Exception as e:
            return MyFirstResult(
                status=ProcessingStatus.ERROR,
                messages=[f"Processing error: {str(e)}"],
            )
    
    async def shutdown(self) -> None:
        """Clean up orchestrator resources."""
        self._initialized = False
```

### Testing Basic Orchestrator

```python
"""Tests for MyFirst orchestrator."""

import pytest
from src.orchestrators.my_first.orchestrator import (
    MyFirstOrchestrator,
    ProcessingStatus,
)


@pytest.mark.asyncio
async def test_basic_processing():
    """Test basic intent processing."""
    orchestrator = MyFirstOrchestrator()
    await orchestrator.initialize()
    
    result = await orchestrator.process("Hello, CORTEX!")
    
    assert result.status == ProcessingStatus.SUCCESS
    assert result.data["word_count"] == 2
    assert "hello, cortex!" in result.data["processed_intent"]
    

@pytest.mark.asyncio
async def test_empty_intent():
    """Test handling of empty intent."""
    orchestrator = MyFirstOrchestrator()
    await orchestrator.initialize()
    
    result = await orchestrator.process("")
    
    assert result.status == ProcessingStatus.ERROR
    assert "Empty intent" in result.messages[0]
```

Run tests:

```bash
pytest src/orchestrators/my_first/tests/ -v
```

---

## Adding Conversation Support

### ConversationProtocol Integration

The `ConversationProtocol` pattern enables multi-turn interactions with explicit termination:

```python
"""Enhanced orchestrator with ConversationProtocol support."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class TerminationReason(Enum):
    """Why a conversation turn ended."""
    COMPLETE = "complete"           # Task finished successfully
    NEEDS_INPUT = "needs_input"     # Waiting for user input
    NEEDS_APPROVAL = "needs_approval"  # Requires confirmation
    ERROR = "error"                 # Processing error
    GOVERNANCE_BLOCK = "governance_block"  # Rule violation
    MAX_TURNS = "max_turns"         # Turn limit reached


@dataclass
class ContinuationDecision:
    """Decision about whether to continue conversation."""
    
    should_continue: bool
    reason: TerminationReason
    next_prompt: Optional[str] = None
    requires_confirmation: bool = False
    confirmation_prompt: Optional[str] = None


@dataclass
class ConversationTurn:
    """A single turn in the conversation."""
    
    turn_number: int
    user_input: str
    response: str
    decision: ContinuationDecision
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationalOrchestrator(MyFirstOrchestrator):
    """Orchestrator with multi-turn conversation support."""
    
    def __init__(self, config: Optional[MyFirstConfig] = None):
        super().__init__(config)
        self._conversation_history: List[ConversationTurn] = []
        self._current_turn = 0
        
    async def converse(
        self, 
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ConversationTurn:
        """Process a conversation turn.
        
        Args:
            user_input: User's message for this turn
            context: Optional context dictionary
            
        Returns:
            ConversationTurn with response and continuation decision
        """
        self._current_turn += 1
        context = context or {}
        
        # Check turn limit
        if self._current_turn > self.config.max_turns:
            return ConversationTurn(
                turn_number=self._current_turn,
                user_input=user_input,
                response="Maximum conversation turns reached.",
                decision=ContinuationDecision(
                    should_continue=False,
                    reason=TerminationReason.MAX_TURNS,
                ),
            )
        
        # Process the input
        result = await self.process(user_input, context)
        
        # Determine continuation
        if result.status == ProcessingStatus.ERROR:
            decision = ContinuationDecision(
                should_continue=False,
                reason=TerminationReason.ERROR,
            )
            response = f"Error: {result.messages[0] if result.messages else 'Unknown error'}"
        elif self._needs_more_input(result):
            decision = ContinuationDecision(
                should_continue=True,
                reason=TerminationReason.NEEDS_INPUT,
                next_prompt="Please provide more details:",
            )
            response = self._format_response(result)
        else:
            decision = ContinuationDecision(
                should_continue=False,
                reason=TerminationReason.COMPLETE,
            )
            response = self._format_response(result)
        
        # Create turn record
        turn = ConversationTurn(
            turn_number=self._current_turn,
            user_input=user_input,
            response=response,
            decision=decision,
            metadata={"result_data": result.data},
        )
        
        # Store in history
        self._conversation_history.append(turn)
        
        return turn
    
    def _needs_more_input(self, result: MyFirstResult) -> bool:
        """Determine if more user input is needed."""
        # Example: short inputs might need clarification
        word_count = result.data.get("word_count", 0)
        return word_count < 3
    
    def _format_response(self, result: MyFirstResult) -> str:
        """Format the result into a response string."""
        if result.status == ProcessingStatus.SUCCESS:
            return f"Processed: {result.data.get('processed_intent', '')}"
        return "Processing complete."
    
    def get_history(self) -> List[ConversationTurn]:
        """Get conversation history."""
        return self._conversation_history.copy()
    
    def reset_conversation(self) -> None:
        """Reset conversation state."""
        self._conversation_history.clear()
        self._current_turn = 0
```

### Usage Example

```python
async def example_conversation():
    """Example multi-turn conversation."""
    orchestrator = ConversationalOrchestrator()
    await orchestrator.initialize()
    
    # Turn 1
    turn1 = await orchestrator.converse("Hi")
    print(f"Turn {turn1.turn_number}: {turn1.response}")
    print(f"Continue? {turn1.decision.should_continue}")
    # Output: Continue? True (short input needs more)
    
    # Turn 2
    turn2 = await orchestrator.converse("Please analyze this document for security issues")
    print(f"Turn {turn2.turn_number}: {turn2.response}")
    print(f"Continue? {turn2.decision.should_continue}")
    # Output: Continue? False (sufficient input)
    
    # Check history
    print(f"Total turns: {len(orchestrator.get_history())}")
```

---

## Integrating Governance

### Governance Hooks

Add governance validation to your orchestrator:

```python
"""Orchestrator with governance integration."""

from typing import List, Optional
from src.core.governance import GovernanceEngine, RuleViolation


class GovernedOrchestrator(ConversationalOrchestrator):
    """Orchestrator with full governance integration."""
    
    def __init__(
        self, 
        config: Optional[MyFirstConfig] = None,
        governance_engine: Optional[GovernanceEngine] = None
    ):
        super().__init__(config)
        self._governance = governance_engine
        
    async def initialize(self) -> None:
        """Initialize with governance validation."""
        await super().initialize()
        
        if self._governance:
            # Validate required rules are loaded
            for rule_id in self.config.required_rules:
                if not self._governance.has_rule(rule_id):
                    raise ValueError(f"Required rule {rule_id} not found")
    
    async def process(
        self, 
        intent: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> MyFirstResult:
        """Process with governance checks."""
        context = context or {}
        
        # Pre-execution governance check
        if self._governance:
            violations = await self._check_governance(intent, context)
            if violations:
                return MyFirstResult(
                    status=ProcessingStatus.GOVERNANCE_BLOCKED,
                    messages=[f"Blocked by rule: {v.rule_id}" for v in violations],
                    data={"violations": [v.to_dict() for v in violations]},
                )
        
        # Execute normal processing
        result = await super().process(intent, context)
        
        # Post-execution audit
        if self._governance:
            await self._audit_execution(intent, result)
        
        return result
    
    async def _check_governance(
        self, 
        intent: str, 
        context: Dict[str, Any]
    ) -> List[RuleViolation]:
        """Check governance rules before execution."""
        violations = []
        
        # Check each required rule
        for rule_id in self.config.required_rules:
            result = await self._governance.evaluate_rule(
                rule_id=rule_id,
                intent=intent,
                context=context,
            )
            if not result.passed:
                violations.append(result.violation)
        
        return violations
    
    async def _audit_execution(
        self, 
        intent: str, 
        result: MyFirstResult
    ) -> None:
        """Record execution in audit trail."""
        await self._governance.record_audit(
            orchestrator_name=self.config.name,
            intent=intent,
            status=result.status.value,
            session_id=self._session_id,
        )
```

### Complexity Gate Integration

For operations that might be risky, integrate the complexity gate:

```python
async def process_with_complexity(
    self, 
    intent: str, 
    context: Optional[Dict[str, Any]] = None
) -> MyFirstResult:
    """Process with complexity-aware confirmation."""
    context = context or {}
    
    # Analyze complexity
    complexity = await self._analyze_complexity(intent, context)
    
    # Check if confirmation needed
    if complexity.score > 0.7:  # High complexity
        if not context.get("user_confirmed", False):
            return MyFirstResult(
                status=ProcessingStatus.PARTIAL,
                messages=["This operation requires confirmation"],
                data={
                    "complexity_score": complexity.score,
                    "complexity_factors": complexity.factors,
                    "requires_confirmation": True,
                    "confirmation_prompt": self._generate_confirmation_prompt(complexity),
                },
            )
    
    # Proceed with execution
    return await super().process(intent, context)

async def _analyze_complexity(
    self, 
    intent: str, 
    context: Dict[str, Any]
) -> ComplexityResult:
    """Analyze operation complexity."""
    factors = []
    score = 0.0
    
    # Factor: Intent length
    if len(intent) > 500:
        factors.append("long_intent")
        score += 0.2
    
    # Factor: Sensitive keywords
    sensitive = ["delete", "remove", "destroy", "production"]
    if any(kw in intent.lower() for kw in sensitive):
        factors.append("sensitive_operation")
        score += 0.4
    
    # Factor: Context flags
    if context.get("affects_production", False):
        factors.append("production_impact")
        score += 0.3
    
    return ComplexityResult(score=min(score, 1.0), factors=factors)
```

---

## Testing Your Orchestrator

### Unit Tests

```python
"""Comprehensive tests for the orchestrator."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.orchestrators.my_first.orchestrator import (
    GovernedOrchestrator,
    ProcessingStatus,
    MyFirstConfig,
)


class TestGovernedOrchestrator:
    """Tests for GovernedOrchestrator."""
    
    @pytest.fixture
    def mock_governance(self):
        """Create mock governance engine."""
        governance = MagicMock()
        governance.has_rule.return_value = True
        governance.evaluate_rule = AsyncMock(return_value=MagicMock(passed=True))
        governance.record_audit = AsyncMock()
        return governance
    
    @pytest.fixture
    async def orchestrator(self, mock_governance):
        """Create initialized orchestrator."""
        orch = GovernedOrchestrator(governance_engine=mock_governance)
        await orch.initialize()
        return orch
    
    @pytest.mark.asyncio
    async def test_passes_governance(self, orchestrator, mock_governance):
        """Test processing when governance passes."""
        result = await orchestrator.process("Test intent")
        
        assert result.status == ProcessingStatus.SUCCESS
        mock_governance.evaluate_rule.assert_called()
        mock_governance.record_audit.assert_called()
    
    @pytest.mark.asyncio
    async def test_blocks_on_violation(self, orchestrator, mock_governance):
        """Test blocking when governance fails."""
        mock_governance.evaluate_rule.return_value = MagicMock(
            passed=False,
            violation=MagicMock(rule_id="CORE-001", to_dict=lambda: {"rule_id": "CORE-001"})
        )
        
        result = await orchestrator.process("Dangerous intent")
        
        assert result.status == ProcessingStatus.GOVERNANCE_BLOCKED
        assert "CORE-001" in result.messages[0]
    
    @pytest.mark.asyncio
    async def test_conversation_flow(self, orchestrator):
        """Test multi-turn conversation."""
        # Short input - needs more
        turn1 = await orchestrator.converse("Hi")
        assert turn1.decision.should_continue is True
        
        # Longer input - complete
        turn2 = await orchestrator.converse("Please help me analyze this document")
        assert turn2.decision.should_continue is False
        
        # Verify history
        history = orchestrator.get_history()
        assert len(history) == 2
```

### Integration Tests

```python
"""Integration tests with real governance."""

import pytest
from src.orchestrators.my_first.orchestrator import GovernedOrchestrator
from src.core.governance import GovernanceEngine


@pytest.mark.integration
class TestGovernanceIntegration:
    """Integration tests with real governance engine."""
    
    @pytest.fixture
    async def real_orchestrator(self):
        """Create orchestrator with real governance."""
        governance = GovernanceEngine()
        await governance.load_rules()
        
        orch = GovernedOrchestrator(governance_engine=governance)
        await orch.initialize()
        return orch
    
    @pytest.mark.asyncio
    async def test_full_flow(self, real_orchestrator):
        """Test full processing flow with real governance."""
        result = await real_orchestrator.process(
            intent="Analyze code for security issues",
            context={"repository": "my-repo"}
        )
        
        assert result.status in [ProcessingStatus.SUCCESS, ProcessingStatus.GOVERNANCE_BLOCKED]
```

### Running All Tests

```bash
# Unit tests only
pytest src/orchestrators/my_first/tests/ -v -m "not integration"

# Integration tests
pytest src/orchestrators/my_first/tests/ -v -m integration

# All tests with coverage
pytest src/orchestrators/my_first/tests/ -v --cov=src/orchestrators/my_first
```

---

## Registration and Deployment

### Registering Your Orchestrator

Add to the orchestrator registry:

```python
# src/orchestrators/registry.py

from typing import Dict, Type
from src.orchestrators.base import OrchestratorBase
from src.orchestrators.my_first.orchestrator import GovernedOrchestrator

ORCHESTRATOR_REGISTRY: Dict[str, Type[OrchestratorBase]] = {
    "my-first-orchestrator": GovernedOrchestrator,
    # ... other orchestrators
}


def get_orchestrator(name: str) -> Type[OrchestratorBase]:
    """Get orchestrator class by name."""
    if name not in ORCHESTRATOR_REGISTRY:
        raise ValueError(f"Unknown orchestrator: {name}")
    return ORCHESTRATOR_REGISTRY[name]
```

### Configuration in cortex-config.yaml

```yaml
# cortex-config.yaml

orchestrators:
  my-first-orchestrator:
    enabled: true
    config:
      max_turns: 15
      timeout_seconds: 45.0
      governance_tier: 3
    governance:
      required_rules:
        - CORE-001
        - CORE-002
        - CUSTOM-001  # Your custom rule
```

### CLI Access

Once registered, use via CLI:

```bash
# List orchestrators
cortex orchestrator list

# Run your orchestrator
cortex orchestrator run my-first-orchestrator --intent "Test message"

# Interactive mode
cortex orchestrator interactive my-first-orchestrator
```

### MCP Tool Exposure

To expose via MCP:

```python
# src/mcp/tools/my_first_tool.py

from src.mcp.server import ToolDefinition
from src.orchestrators.my_first.orchestrator import GovernedOrchestrator


MY_FIRST_TOOL = ToolDefinition(
    name="cortex_my_first",
    description="Process intent through MyFirst orchestrator",
    input_schema={
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "description": "The intent to process"
            },
            "context": {
                "type": "object",
                "description": "Optional context"
            }
        },
        "required": ["intent"]
    }
)


async def handle_my_first(params: dict) -> dict:
    """Handle MCP tool call."""
    orchestrator = GovernedOrchestrator()
    await orchestrator.initialize()
    
    result = await orchestrator.process(
        intent=params["intent"],
        context=params.get("context", {})
    )
    
    return {
        "status": result.status.value,
        "data": result.data,
        "messages": result.messages,
    }
```

---

## Next Steps

### Enhance Your Orchestrator

1. **Add LENS Integration**: Connect to the LENS Protocol for intent comprehension
2. **Domain Brain Queries**: Integrate knowledge retrieval
3. **Custom Response Composition**: Use the 6 modes and 5 tones
4. **Resilience Patterns**: Add circuit breakers and retry logic

### Learn More

- [Orchestration Engine Architecture](../02-architecture/3-orchestration-engine.md)
- [Governance Framework](../02-architecture/1-system-overview.md#governance-tiers)
- [Response Composition Guide](../04-guides/advanced/response-composition.md)
- [Testing Strategy](../07-contributing/3-testing-strategy.md)

### Example Orchestrators

Study existing orchestrators for patterns:

- `src/orchestrators/master/` - Master Orchestrator (full ConversationProtocol)
- `src/orchestrators/lens/` - LENS Protocol implementation
- `src/orchestrators/domain_brain/` - Knowledge orchestration

---

## Troubleshooting

### Common Issues

**"Required rule not found"**
- Ensure governance database is initialized: `cortex governance init`
- Check rule ID matches exactly (case-sensitive)

**"Orchestrator not in registry"**
- Add to `ORCHESTRATOR_REGISTRY` in `src/orchestrators/registry.py`
- Restart the service

**"Governance blocked unexpectedly"**
- Check audit logs: `cortex audit list --limit 10`
- Verify context contains required fields

### Getting Help

- Check [Troubleshooting Guide](3-troubleshooting.md)
- Search [Known Issues](../05-reference/known-issues.md)
- Ask in the development channel

---

**Next:** [Troubleshooting Setup](3-troubleshooting.md)
