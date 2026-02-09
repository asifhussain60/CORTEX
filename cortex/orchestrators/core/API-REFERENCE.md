# PersonaOrchestrator API Reference

Complete API documentation for the Role-Adaptive Persona System.

---

## PersonaOrchestrator

**Module:** `cortex.orchestrators.core.persona_orchestrator`

Main coordinator for the persona system, integrating role resolution, persona loading, depth management, response styling, template injection, and command handling.

### Constructor

```python
PersonaOrchestrator()
```

**Description:** Initializes all 7 persona system components with shared state management.

**Components Initialized:**
- `RoleResolver` — Infers user role from context
- `PersonaLoader` — Loads and caches personas.yaml
- `DepthManager` — Manages depth overrides with TTL
- `ResponseStyler` — Formats responses per persona
- `PersonaInjector` — Injects context into templates
- `PersonaCommandHandler` — Handles /persona commands
- `DetailCommandHandler` — Handles /detail commands

**Example:**
```python
orchestrator = PersonaOrchestrator()
```

---

### process_request()

```python
def process_request(
    self,
    query: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
```

**Description:** Executes inference workflow to determine active persona and depth.

**Parameters:**
- `query` (str) — User query text
- `context` (dict, optional) — Context signals for inference
  - `file_path` (str) — Current file being edited
  - `vocabulary_complexity` (float) — Technical vocabulary score (0-1)
  - `session_history` (list) — Previous persona assignments
  - `explicit_persona` (str) — Explicit persona override

**Returns:** Dict with:
- `persona_id` (str) — Resolved persona identifier
- `depth_id` (str) — Resolved depth level
- `confidence` (float) — Inference confidence score (0-1)
- `inference_used` (bool) — Whether inference was used vs explicit

**Example:**
```python
result = orchestrator.process_request(
    query="How should I optimize this database query?",
    context={
        "file_path": "app/models/database.py",
        "vocabulary_complexity": 0.88,
        "session_history": [
            {"persona": "engineer", "confidence": 0.92}
        ]
    }
)

print(result)
# {
#   "persona_id": "engineer",
#   "depth_id": "full",
#   "confidence": 0.88,
#   "inference_used": True
# }
```

**Workflow:**
1. Check for explicit persona in context
2. If none, use RoleResolver to infer from signals
3. Determine depth level (override or persona default)
4. Update internal state
5. Return result with confidence score

---

### style_response()

```python
def style_response(
    self,
    response: str,
    available_metrics: Optional[Dict[str, Any]] = None
) -> str
```

**Description:** Applies persona-based formatting to response text, with depth word limit override.

**Parameters:**
- `response` (str) — Raw response text to format
- `available_metrics` (dict, optional) — Available metrics for filtering
  - Example: `{"coverage": 0.89, "complexity": 12, "ROI": 15000}`

**Returns:** Formatted response string (styled, filtered, word-limited)

**Example:**
```python
# Engineer persona with executive depth override
orchestrator.execute_command("/persona set engineer")
orchestrator.execute_command("/detail executive")

raw = "Query optimization requires three steps: add indexes, implement connection pooling, and refactor N+1 queries. The indexes should target user_id and created_at columns..."

styled = orchestrator.style_response(
    response=raw,
    available_metrics={"coverage": 0.91, "complexity": 15}
)

print(len(styled.split()))  # ~100 words (executive depth limit)
```

**Behavior:**
- **Word Limit:** Depth word_limit overrides persona word_limit
- **Metrics Filtering:** Shows only metrics relevant to persona
- **Code Filtering:** Hides/shows code based on persona.show_code
- **Format Application:** BLUF, narrative, technical, etc.

**Word Limit Precedence:**
1. Active depth override word_limit (highest)
2. Persona default word_limit
3. No limit (if both are null)

---

### inject_persona_context()

```python
def inject_persona_context(self, template: str) -> str
```

**Description:** Replaces `{{PERSONA_INJECTION_POINT}}` marker with formatted persona guidance.

**Parameters:**
- `template` (str) — Prompt template containing marker

**Returns:** Template with marker replaced by persona context block

**Example:**
```python
orchestrator.execute_command("/persona set tech_lead")

template = """
{{PERSONA_INJECTION_POINT}}

## Task
Analyze test coverage for authentication module.

## Requirements
- Show coverage metrics
- Identify gaps
- Recommend improvements
"""

injected = orchestrator.inject_persona_context(template)

print(injected)
# 🏗️ **Tech Lead / Manager Mode** (Technical-Business Depth)
# 
# **Your preferences:**
# - Format: Architecture + metrics
# - Focus: Architecture, health metrics, tech debt
# - Word limit: 500 words
# - Code visibility: Diagrams only
# - Metrics: health_metrics, coverage, complexity, tech_debt
# 
# ---
# 
# ## Task
# Analyze test coverage for authentication module.
# ...
```

**Behavior:**
- If marker present: Replaces with persona context
- If marker absent: Prepends persona context to template
- Context includes: Emoji icon, persona name, depth, preferences, word limit

---

### execute_command()

```python
def execute_command(self, command: str) -> Dict[str, Any]
```

**Description:** Routes and executes `/persona` or `/detail` commands.

**Parameters:**
- `command` (str) — Command string (must start with `/persona` or `/detail`)

**Returns:** Dict with:
- `success` (bool) — Whether command succeeded
- `message` (str) — Success message (if success=True)
- `error` (str) — Error message (if success=False)
- Additional fields depending on command

**Supported Commands:**

#### /persona Commands

```python
# Set persona
result = orchestrator.execute_command("/persona set engineer")
# {"success": True, "message": "Persona set to engineer", "persona_id": "engineer"}

# Show current persona
result = orchestrator.execute_command("/persona show")
# {"success": True, "persona_id": "engineer", "depth_id": "full"}

# List all personas
result = orchestrator.execute_command("/persona list")
# {"success": True, "personas": ["business_leader", "product_owner", ...]}
```

#### /detail Commands

```python
# Set depth (TTL=1)
result = orchestrator.execute_command("/detail executive")
# {"success": True, "message": "Depth set to executive for 1 turn"}

# Set depth with explicit TTL
result = orchestrator.execute_command("/detail executive 3")
# {"success": True, "message": "Depth set to executive for 3 turns"}

# Set sticky depth
result = orchestrator.execute_command("/detail standard sticky")
# {"success": True, "message": "Depth set to standard (sticky)"}

# Show current depth
result = orchestrator.execute_command("/detail show")
# {"success": True, "depth_id": "executive", "ttl": 3}

# Reset to persona default
result = orchestrator.execute_command("/detail reset")
# {"success": True, "message": "Depth reset to persona default"}
```

**Aliases:** See command handlers for full alias mappings (e.g., "ceo" → "business_leader")

---

### get_current_state()

```python
def get_current_state(self) -> Dict[str, str]
```

**Description:** Retrieves current persona and depth state.

**Parameters:** None

**Returns:** Dict with:
- `persona_id` (str) — Active persona identifier
- `depth_id` (str) — Active depth level

**Example:**
```python
orchestrator.execute_command("/persona set tech_lead")
orchestrator.execute_command("/detail detailed")

state = orchestrator.get_current_state()
print(state)
# {
#   "persona_id": "tech_lead",
#   "depth_id": "detailed"
# }
```

**Behavior:**
- Checks for active depth override first
- Falls back to persona default depth
- Always returns both persona and depth

---

### consume_turn()

```python
def consume_turn(self) -> None
```

**Description:** Decrements depth override TTL by 1. Call after each response.

**Parameters:** None

**Returns:** None

**Example:**
```python
orchestrator.execute_command("/detail executive 3")  # TTL=3

state1 = orchestrator.get_current_state()
print(state1["depth_id"])  # "executive"

orchestrator.consume_turn()  # TTL: 3 → 2
orchestrator.consume_turn()  # TTL: 2 → 1
orchestrator.consume_turn()  # TTL: 1 → 0 (expired)

state2 = orchestrator.get_current_state()
print(state2["depth_id"])  # "full" (reverted to persona default)
```

**Behavior:**
- If no override: No-op
- If override with TTL: Decrement TTL
- If TTL reaches 0: Remove override, revert to default
- If sticky override: No-op (TTL is None)

---

### serialize_state()

```python
def serialize_state(self) -> Dict[str, Any]
```

**Description:** Serializes current state to JSON-compatible dict for persistence.

**Parameters:** None

**Returns:** Dict with:
- `current_persona` (str) — Active persona ID
- `current_depth` (str) — Active depth ID
- `depth_override` (dict|null) — Active override or null
  - `depth_id` (str)
  - `ttl` (int|null)
  - `sticky` (bool)
- `switch_history` (list) — Recent persona switches

**Example:**
```python
orchestrator.execute_command("/persona set engineer")
orchestrator.execute_command("/detail executive 2")

state = orchestrator.serialize_state()
print(state)
# {
#   "current_persona": "engineer",
#   "current_depth": "executive",
#   "depth_override": {
#     "depth_id": "executive",
#     "ttl": 2,
#     "sticky": False
#   },
#   "switch_history": [
#     {
#       "from": None,
#       "to": "engineer",
#       "timestamp": "2026-02-07T10:30:15Z"
#     }
#   ]
# }
```

**Use Case:** Save to session storage for cross-turn persistence.

---

### restore_state()

```python
def restore_state(self, state: Dict[str, Any]) -> None
```

**Description:** Restores orchestrator state from serialized dict.

**Parameters:**
- `state` (dict) — State dict from serialize_state()

**Returns:** None

**Example:**
```python
# Session 1: Save state
orchestrator1 = PersonaOrchestrator()
orchestrator1.execute_command("/persona set tech_lead")
state = orchestrator1.serialize_state()
save_to_file("session123.json", state)

# Session 2: Restore state
orchestrator2 = PersonaOrchestrator()
state = load_from_file("session123.json")
orchestrator2.restore_state(state)

# State preserved
current = orchestrator2.get_current_state()
print(current["persona_id"])  # "tech_lead"
```

**Behavior:**
- Restores persona, depth, override, history
- Validates state structure
- Handles missing/invalid fields gracefully

---

## Component APIs

### RoleResolver

**Purpose:** Infers user role from context signals.

```python
from cortex.orchestrators.core.role_resolver import RoleResolver

resolver = RoleResolver()

context = {
    "file_path": "app/models/user.py",
    "vocabulary_complexity": 0.85,
    "session_history": [{"persona": "engineer"}]
}

result = resolver.resolve_role(query="How do I optimize this?", context=context)
print(result)
# {
#   "persona_id": "engineer",
#   "confidence": 0.87,
#   "signals_used": ["vocabulary", "file_context", "history"]
# }
```

---

### PersonaLoader

**Purpose:** Loads and caches personas.yaml.

```python
from cortex.orchestrators.core.persona_loader import PersonaLoader

loader = PersonaLoader()

# Get persona
persona = loader.get_persona("engineer")
print(persona.display_name)  # "Software Engineer"
print(persona.word_limit)  # None (unlimited)

# Get depth
depth = loader.get_depth_level("executive")
print(depth.word_limit)  # 100

# List all
personas = loader.list_persona_ids()
print(personas)  # ["business_leader", "product_owner", ...]
```

---

### DepthManager

**Purpose:** Manages depth overrides with TTL.

```python
from cortex.orchestrators.core.depth_manager import DepthManager

manager = DepthManager()

# Set override
manager.set_override("executive", ttl=3)

# Get override
override = manager.get_override()
print(override.depth_id)  # "executive"
print(override.ttl)  # 3

# Consume turn
manager.consume_turn()  # TTL: 3 → 2

# Check if active
print(manager.has_override())  # True

# Clear
manager.clear_override()
```

---

### ResponseStyler

**Purpose:** Formats responses per persona.

```python
from cortex.orchestrators.core.response_styler import ResponseStyler

styler = ResponseStyler()

response = "Long technical explanation..."
metrics = {"coverage": 0.91, "ROI": 15000}

styled = styler.style("business_leader", response, metrics)
print(styled)  # BLUF format, ROI shown, code hidden
```

---

### PersonaInjector

**Purpose:** Injects persona context into templates.

```python
from cortex.orchestrators.core.persona_injector import PersonaInjector

injector = PersonaInjector()

template = "{{PERSONA_INJECTION_POINT}}\n\nTask: Analyze coverage"
injected = injector.inject(template, "engineer", "full")

print(injected)
# 🛠️ **Engineer Mode** (Full Depth)
# ...
# Task: Analyze coverage
```

---

## Error Handling

All methods return structured error information:

```python
# Invalid persona
result = orchestrator.execute_command("/persona set invalid")
if not result["success"]:
    print(result["error"])  # "Unknown persona: invalid"
    print(result["available"])  # List of valid personas

# Invalid depth
result = orchestrator.execute_command("/detail invalid")
if not result["success"]:
    print(result["error"])  # "Unknown depth: invalid"
```

---

## Type Definitions

### PersonaResult

```python
{
    "persona_id": str,
    "depth_id": str,
    "confidence": float,  # 0.0-1.0
    "inference_used": bool
}
```

### CommandResult

```python
{
    "success": bool,
    "message": str,  # If success=True
    "error": str,  # If success=False
    "available": list[str]  # If applicable
}
```

### StateDict

```python
{
    "current_persona": str,
    "current_depth": str,
    "depth_override": {
        "depth_id": str,
        "ttl": int | None,
        "sticky": bool
    } | None,
    "switch_history": list[dict]
}
```

---

## Testing

Complete test coverage available in:
- `tests/integration/test_persona_integration.py` (19 tests)
- `tests/unit/orchestrators/test_persona_orchestrator.py` (planned)

Run tests:
```bash
pytest tests/integration/test_persona_integration.py -v
```

---

**See also:**
- [README-PERSONAS.md](./README-PERSONAS.md) — Main documentation
- [PERSONA-EXAMPLES.md](./PERSONA-EXAMPLES.md) — Usage examples
- [INTEGRATION-GUIDE.md](./INTEGRATION-GUIDE.md) — Integration patterns
