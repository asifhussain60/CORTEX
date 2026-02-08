# Persona System Integration Guide

**How to integrate the Role-Adaptive Persona System into CORTEX components.**

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Advanced Features](#advanced-features)
4. [Error Handling](#error-handling)
5. [Session Management](#session-management)
6. [InteractionOrchestrator Integration](#interactionorchestrator-integration)
7. [MCP Tool Integration](#mcp-tool-integration)
8. [Testing Integration](#testing-integration)
9. [Best Practices](#best-practices)

---

## Getting Started

### Installation

PersonaOrchestrator is part of CORTEX core. No additional installation needed.

### Import

```python
from cortex.orchestrators.core.persona_orchestrator import PersonaOrchestrator
```

### Initialization

```python
# Create orchestrator instance
orchestrator = PersonaOrchestrator()

# Components auto-initialized:
# - RoleResolver
# - PersonaLoader
# - DepthManager
# - ResponseStyler
# - PersonaInjector
# - PersonaCommandHandler
# - DetailCommandHandler
```

---

## Basic Usage

### Pattern 1: Request Processing

```python
def process_user_request(query: str, context: dict) -> dict:
    """Process user request with persona inference."""
    orchestrator = PersonaOrchestrator()
    
    # Infer persona from context
    result = orchestrator.process_request(query, context)
    
    return {
        "persona": result["persona_id"],
        "depth": result["depth_id"],
        "confidence": result["confidence"]
    }
```

### Pattern 2: Response Styling

```python
def format_response(response: str, metrics: dict) -> str:
    """Format response based on active persona."""
    orchestrator = PersonaOrchestrator()
    
    # Apply persona formatting
    styled = orchestrator.style_response(response, metrics)
    
    # Consume turn (TTL management)
    orchestrator.consume_turn()
    
    return styled
```

### Pattern 3: Command Handling

```python
def handle_command(command: str) -> dict:
    """Handle persona/detail commands."""
    orchestrator = PersonaOrchestrator()
    
    if command.startswith(("/persona", "/detail")):
        result = orchestrator.execute_command(command)
        return result
    
    return {"success": False, "error": "Not a persona command"}
```

---

## Advanced Features

### Multi-Turn Conversations

```python
class ConversationManager:
    """Manages multi-turn conversations with persona state."""
    
    def __init__(self):
        self.orchestrator = PersonaOrchestrator()
        self.turn_count = 0
    
    def process_turn(self, query: str, context: dict) -> str:
        """Process single conversation turn."""
        self.turn_count += 1
        
        # Handle commands
        if query.startswith(("/persona", "/detail")):
            result = self.orchestrator.execute_command(query)
            return self._format_command_result(result)
        
        # Infer and process
        persona_result = self.orchestrator.process_request(query, context)
        
        # Generate response (your logic here)
        raw_response = self._generate_response(query, context)
        
        # Style response
        styled = self.orchestrator.style_response(raw_response, context.get("metrics"))
        
        # Consume turn
        self.orchestrator.consume_turn()
        
        return styled
    
    def _generate_response(self, query: str, context: dict) -> str:
        """Generate raw response (placeholder)."""
        return "Response generated based on query and context."
    
    def _format_command_result(self, result: dict) -> str:
        """Format command result for display."""
        if result.get("success"):
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
```

### Context Building

```python
def build_context(request: dict) -> dict:
    """Build context dict for persona inference."""
    context = {
        "query": request.get("query", ""),
        "file_path": request.get("file_path"),
        "session_history": request.get("history", [])
    }
    
    # Add vocabulary complexity
    if "query" in request:
        context["vocabulary_complexity"] = calculate_complexity(request["query"])
    
    # Add metrics if available
    if "metrics" in request:
        context["metrics"] = request["metrics"]
    
    return context

def calculate_complexity(text: str) -> float:
    """Calculate technical vocabulary complexity (0-1)."""
    technical_terms = [
        "async", "await", "generator", "decorator", "metaclass",
        "polymorphism", "encapsulation", "abstraction", "refactor"
    ]
    
    words = text.lower().split()
    technical_count = sum(1 for word in words if word in technical_terms)
    
    return min(technical_count / len(words), 1.0) if words else 0.0
```

### Template Injection

```python
def create_prompt_with_persona(query: str) -> str:
    """Create prompt with persona context injection."""
    orchestrator = PersonaOrchestrator()
    
    template = f"""
{{{{PERSONA_INJECTION_POINT}}}}

## User Query
{query}

## Context
[Your context here]

## Requirements
- Provide clear answer
- Include examples if relevant
- Match user's expertise level
"""
    
    return orchestrator.inject_persona_context(template)
```

---

## Error Handling

### Pattern: Graceful Degradation

```python
def process_with_fallback(query: str, context: dict) -> dict:
    """Process request with fallback to defaults."""
    orchestrator = PersonaOrchestrator()
    
    try:
        result = orchestrator.process_request(query, context)
        
        # Check confidence
        if result["confidence"] < 0.7:
            return {
                "success": False,
                "reason": "low_confidence",
                "persona": "unknown",
                "message": "Please specify your role with /persona set <role>"
            }
        
        return {
            "success": True,
            "persona": result["persona_id"],
            "depth": result["depth_id"]
        }
        
    except Exception as e:
        # Fall back to default
        return {
            "success": True,
            "persona": "engineer",  # Default
            "depth": "full",
            "fallback": True,
            "error": str(e)
        }
```

### Pattern: Command Validation

```python
def execute_validated_command(command: str) -> dict:
    """Execute command with validation."""
    orchestrator = PersonaOrchestrator()
    
    # Validate command format
    if not command.startswith(("/persona", "/detail")):
        return {
            "success": False,
            "error": "Invalid command. Use /persona or /detail"
        }
    
    # Execute
    result = orchestrator.execute_command(command)
    
    # Check result
    if not result.get("success"):
        # Log error
        print(f"Command failed: {result.get('error')}")
    
    return result
```

---

## Session Management

### Pattern: Persistent Sessions

```python
import json
from pathlib import Path

class SessionManager:
    """Manages persona state across sessions."""
    
    def __init__(self, session_dir: str = "./sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        self.orchestrator = PersonaOrchestrator()
    
    def load_session(self, session_id: str) -> bool:
        """Load session state from file."""
        session_file = self.session_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return False
        
        try:
            with open(session_file, "r") as f:
                state = json.load(f)
            
            self.orchestrator.restore_state(state)
            return True
            
        except Exception as e:
            print(f"Failed to load session: {e}")
            return False
    
    def save_session(self, session_id: str) -> bool:
        """Save session state to file."""
        session_file = self.session_dir / f"{session_id}.json"
        
        try:
            state = self.orchestrator.serialize_state()
            
            with open(session_file, "w") as f:
                json.dump(state, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Failed to save session: {e}")
            return False
    
    def process_with_persistence(self, session_id: str, query: str, context: dict) -> str:
        """Process request with session persistence."""
        # Load existing session
        self.load_session(session_id)
        
        # Process request
        if query.startswith(("/persona", "/detail")):
            result = self.orchestrator.execute_command(query)
            response = f"✅ {result.get('message', result.get('error'))}"
        else:
            persona_result = self.orchestrator.process_request(query, context)
            raw_response = f"Processed with {persona_result['persona_id']} persona"
            response = self.orchestrator.style_response(raw_response, context.get("metrics"))
            self.orchestrator.consume_turn()
        
        # Save session
        self.save_session(session_id)
        
        return response

# Usage
manager = SessionManager()
response = manager.process_with_persistence(
    session_id="user123",
    query="/persona set tech_lead",
    context={}
)
```

---

## InteractionOrchestrator Integration

### Pattern: Enhanced InteractionOrchestrator

```python
from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
from cortex.orchestrators.core.persona_orchestrator import PersonaOrchestrator

class PersonaAwareInteraction(InteractionOrchestrator):
    """InteractionOrchestrator enhanced with persona awareness."""
    
    def __init__(self):
        super().__init__()
        self.persona = PersonaOrchestrator()
    
    def process(self, query: str, context: dict) -> str:
        """Process request with persona-aware response."""
        
        # Step 1: Handle persona commands
        if query.startswith(("/persona", "/detail")):
            result = self.persona.execute_command(query)
            return self._format_command_result(result)
        
        # Step 2: Infer persona
        persona_result = self.persona.process_request(query, context)
        
        # Step 3: Add persona to context
        context["persona_id"] = persona_result["persona_id"]
        context["depth_id"] = persona_result["depth_id"]
        
        # Step 4: Call parent process
        raw_response = super().process(query, context)
        
        # Step 5: Style response
        styled = self.persona.style_response(raw_response, context.get("metrics"))
        
        # Step 6: Consume turn
        self.persona.consume_turn()
        
        return styled
    
    def process_with_injection(self, query: str, context: dict, template: str) -> str:
        """Process with template injection."""
        
        # Inject persona context
        injected_template = self.persona.inject_persona_context(template)
        
        # Process with injected template
        context["template"] = injected_template
        return self.process(query, context)
    
    def _format_command_result(self, result: dict) -> str:
        """Format command result."""
        if result.get("success"):
            return f"✅ {result['message']}"
        return f"❌ {result['error']}"
```

---

## MCP Tool Integration

### Pattern: MCP Tool Wrapper (Future)

```python
# NOTE: Stage 37.4 implementation
# This is a preview of planned MCP tool integration

from cortex.mcp.base import MCPTool

class PersonaMCPTool(MCPTool):
    """MCP tool for persona management."""
    
    def __init__(self):
        super().__init__(
            name="cortex_set_persona",
            description="Set user persona for response adaptation"
        )
        self.orchestrator = PersonaOrchestrator()
    
    def execute(self, role: str, save: bool = False) -> dict:
        """Execute persona set command."""
        command = f"/persona set {role}"
        result = self.orchestrator.execute_command(command)
        
        if result.get("success") and save:
            # Save to persistent storage (Stage 37.4)
            self._save_persona_preference(role)
        
        return result
    
    def _save_persona_preference(self, role: str):
        """Save persona preference (placeholder)."""
        # Implementation in Stage 37.4
        pass
```

---

## Testing Integration

### Pattern: Test Fixtures

```python
import pytest
from cortex.orchestrators.core.persona_orchestrator import PersonaOrchestrator

@pytest.fixture
def orchestrator():
    """Provide fresh PersonaOrchestrator instance."""
    return PersonaOrchestrator()

@pytest.fixture
def engineer_context():
    """Provide engineer persona context."""
    return {
        "file_path": "cortex/core/engine.py",
        "vocabulary_complexity": 0.88,
        "session_history": [{"persona": "engineer"}]
    }

def test_persona_inference(orchestrator, engineer_context):
    """Test persona inference with engineer context."""
    result = orchestrator.process_request(
        query="How do I implement async generators?",
        context=engineer_context
    )
    
    assert result["persona_id"] == "engineer"
    assert result["confidence"] >= 0.7
```

### Pattern: Integration Testing

```python
def test_full_workflow():
    """Test complete persona workflow."""
    orchestrator = PersonaOrchestrator()
    
    # Set persona
    cmd_result = orchestrator.execute_command("/persona set tech_lead")
    assert cmd_result["success"]
    
    # Process request
    result = orchestrator.process_request(
        query="Show test coverage metrics",
        context={"metrics": {"coverage": 0.91}}
    )
    assert result["persona_id"] == "tech_lead"
    
    # Style response
    raw = "Test coverage is 91% with 450 unit tests"
    styled = orchestrator.style_response(raw, {"coverage": 0.91})
    assert "91%" in styled
    
    # Verify state
    state = orchestrator.get_current_state()
    assert state["persona_id"] == "tech_lead"
```

---

## Best Practices

### 1. Always Consume Turns

```python
# ✅ CORRECT
styled = orchestrator.style_response(response, metrics)
orchestrator.consume_turn()  # Decrement TTL

# ❌ WRONG
styled = orchestrator.style_response(response, metrics)
# TTL not decremented, overrides don't expire
```

### 2. Build Rich Context

```python
# ✅ CORRECT
context = {
    "file_path": current_file,
    "vocabulary_complexity": calculate_complexity(query),
    "session_history": get_recent_personas(session_id),
    "metrics": get_available_metrics()
}

# ❌ WRONG
context = {}  # Inference will fail
```

### 3. Handle Low Confidence

```python
# ✅ CORRECT
result = orchestrator.process_request(query, context)
if result["confidence"] < 0.7:
    # Ask user to specify role
    print("Please use /persona set <role>")
else:
    # Proceed with inferred role
    process_with_persona(result["persona_id"])

# ❌ WRONG
result = orchestrator.process_request(query, context)
# Blindly trust low-confidence inference
```

### 4. Persist Sessions

```python
# ✅ CORRECT
state = orchestrator.serialize_state()
save_to_storage(session_id, state)

# Load in next session
orchestrator.restore_state(load_from_storage(session_id))

# ❌ WRONG
# State lost between sessions, user must re-specify persona
```

### 5. Inject Persona Context

```python
# ✅ CORRECT
template = """
{{PERSONA_INJECTION_POINT}}

User Query: {query}
"""
injected = orchestrator.inject_persona_context(template)

# ❌ WRONG
template = "User Query: {query}"
# No persona guidance, model doesn't know user preferences
```

---

## Common Pitfalls

### Pitfall 1: Not Calling consume_turn()

**Problem:** Depth overrides never expire

**Solution:**
```python
orchestrator.execute_command("/detail executive 3")
styled1 = orchestrator.style_response(response1, metrics)
orchestrator.consume_turn()  # Don't forget!
```

### Pitfall 2: Empty Context

**Problem:** Inference fails with low confidence

**Solution:**
```python
# Include at least file_path or vocabulary_complexity
context = {
    "file_path": "app/models/user.py",  # Strong signal
    "vocabulary_complexity": 0.85  # Strong signal
}
```

### Pitfall 3: Ignoring Command Results

**Problem:** Command failures go unnoticed

**Solution:**
```python
result = orchestrator.execute_command("/persona set invalid")
if not result["success"]:
    print(f"Error: {result['error']}")
    print(f"Valid options: {result['available']}")
```

---

## Performance Considerations

### Caching

PersonaLoader caches personas.yaml (LRU cache, size=1):
```python
# First call: Loads from disk
persona1 = loader.get_persona("engineer")  # ~5ms

# Subsequent calls: From cache
persona2 = loader.get_persona("engineer")  # ~0.1ms
```

### Memory

PersonaOrchestrator is lightweight:
- Memory footprint: ~10KB per instance
- No heavy dependencies
- Shared managers reduce duplication

### Latency

Typical operation times:
- `process_request()`: 1-2ms
- `style_response()`: 5-10ms (depends on response length)
- `execute_command()`: 0.5-1ms
- `inject_persona_context()`: 1-2ms

---

## Migration Guide

### From Raw Responses

**Before:**
```python
def process(query: str) -> str:
    return "Raw response text"
```

**After:**
```python
def process(query: str, context: dict) -> str:
    orchestrator = PersonaOrchestrator()
    orchestrator.process_request(query, context)
    raw = "Raw response text"
    return orchestrator.style_response(raw, context.get("metrics"))
```

### From Static Formatting

**Before:**
```python
if user_role == "executive":
    return format_bluf(response)
elif user_role == "engineer":
    return format_technical(response)
```

**After:**
```python
orchestrator = PersonaOrchestrator()
result = orchestrator.process_request(query, context)
return orchestrator.style_response(response, metrics)
# Persona inferred automatically
```

---

**See also:**
- [README-PERSONAS.md](./README-PERSONAS.md) — Main documentation
- [PERSONA-EXAMPLES.md](./PERSONA-EXAMPLES.md) — Usage examples
- [API-REFERENCE.md](./API-REFERENCE.md) — Complete API documentation
