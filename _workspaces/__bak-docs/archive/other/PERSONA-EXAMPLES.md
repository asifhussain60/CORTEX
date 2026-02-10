# Persona System Examples

**Comprehensive workflows demonstrating the Role-Adaptive Persona System.**

---

## Example 1: Basic Persona Switching

```python
from cortex.orchestrators.core.persona_orchestrator import PersonaOrchestrator

orchestrator = PersonaOrchestrator()

# Scenario: Product Owner wants engineering update
result = orchestrator.execute_command("/persona set product_owner")

print(result)
# {
#   "success": true,
#   "message": "Persona set to product_owner",
#   "persona_id": "product_owner",
#   "depth_id": "standard",
#   "format": "narrative"
# }

# Query processed with product owner context
response = orchestrator.process_request(
    query="What's the status of the authentication feature?",
    context={"session_history": []}
)

print(response)
# {
#   "persona_id": "product_owner",
#   "depth_id": "standard",
#   "confidence": 1.0,  # Explicit setting, no inference
#   "inference_used": false
# }
```

---

## Example 2: Depth Override with TTL

```python
orchestrator = PersonaOrchestrator()

# Set engineer persona (default: full depth, unlimited words)
orchestrator.execute_command("/persona set engineer")

# Override to executive depth for next 3 turns
orchestrator.execute_command("/detail executive 3")

# Turn 1: 100 word limit applied
styled_1 = orchestrator.style_response(
    response="Long technical explanation about database optimization...",
    available_metrics={}
)
orchestrator.consume_turn()  # TTL: 3 → 2

# Turn 2: Still 100 word limit
styled_2 = orchestrator.style_response(
    response="Another long explanation...",
    available_metrics={}
)
orchestrator.consume_turn()  # TTL: 2 → 1

# Turn 3: Still 100 word limit
styled_3 = orchestrator.style_response(
    response="Final explanation...",
    available_metrics={}
)
orchestrator.consume_turn()  # TTL: 1 → 0 (expired, reverts to 'full')

# Turn 4: Back to unlimited (engineer default)
styled_4 = orchestrator.style_response(
    response="Now unlimited again...",
    available_metrics={}
)
```

---

## Example 3: Inference Workflow

```python
orchestrator = PersonaOrchestrator()

# Context signals: Technical vocabulary + Python file
context = {
    "query": "How should I refactor this async generator?",
    "file_path": "cortex/orchestrators/core/optimizer.py",
    "vocabulary_complexity": 0.88,
    "session_history": [
        {"persona": "engineer", "confidence": 0.92}
    ]
}

result = orchestrator.process_request(
    query=context["query"],
    context=context
)

print(result)
# {
#   "persona_id": "engineer",
#   "depth_id": "full",
#   "confidence": 0.85,
#   "inference_used": true
# }

# Styled for engineer: Full technical depth
response = "To refactor async generators, consider using async comprehensions..."
styled = orchestrator.style_response(response, context.get("metrics"))

# Engineer gets full code examples, no word limit
print(len(styled))  # 1500+ characters
```

---

## Example 4: Business Leader Workflow

```python
orchestrator = PersonaOrchestrator()

# Explicit business leader persona
orchestrator.execute_command("/persona set business_leader")

# Business query
context = {
    "query": "What's our test coverage improvement this quarter?",
    "vocabulary_complexity": 0.45,  # Low complexity
    "session_history": []
}

result = orchestrator.process_request(
    query=context["query"],
    context=context
)

# Styled for business leader: BLUF format, 150 words max
response = """Test coverage improved from 78% to 91% this quarter (+13 points).

Key achievements:
- Added 450 unit tests across 12 modules
- Implemented integration test suite (85 tests)
- Automated coverage reporting in CI/CD

Business impact:
- 40% reduction in production bugs (15 → 9 incidents)
- Faster deployment confidence (manual QA time -50%)
- $25k annual savings in bug fix costs

Investment: 3 engineer-weeks (within planned sprint capacity)
ROI: 300% (payback in 4 months)

Risks mitigated: Critical path coverage now 98% (up from 65%)"""

styled = orchestrator.style_response(response, {"business_impact": "high"})

print(len(styled.split()))  # ~120 words (within 150 limit)
print("BLUF" in styled)  # True (formatted with bottom-line-up-front)
```

---

## Example 5: Session Persistence

```python
# Session 1: User sets preferences
orchestrator = PersonaOrchestrator()
orchestrator.execute_command("/persona set tech_lead")
orchestrator.execute_command("/detail detailed sticky")

# Serialize state
state = orchestrator.serialize_state()
print(state)
# {
#   "current_persona": "tech_lead",
#   "current_depth": "detailed",
#   "depth_override": {
#     "depth_id": "detailed",
#     "ttl": null,  # sticky = infinite
#     "sticky": true
#   },
#   "switch_history": [
#     {"from": null, "to": "tech_lead", "timestamp": "2026-02-07T10:30:00Z"}
#   ]
# }

# Save to storage (user-specific)
save_to_session(user_id="user123", state=state)

# --- Session 2: Different conversation, same user ---

orchestrator2 = PersonaOrchestrator()

# Restore state
state = load_from_session(user_id="user123")
orchestrator2.restore_state(state)

# Preferences preserved
current = orchestrator2.get_current_state()
print(current)
# {
#   "persona_id": "tech_lead",
#   "depth_id": "detailed"
# }
```

---

## Example 6: Template Injection

```python
orchestrator = PersonaOrchestrator()
orchestrator.execute_command("/persona set engineer")

# Template with injection point
template = """
{{PERSONA_INJECTION_POINT}}

## Task
Optimize the database query in app/queries.py

## Context
Current query takes 2.5s for 10k records.

## Requirements
- Reduce query time by 50%+
- Maintain backward compatibility
- Add tests
"""

injected = orchestrator.inject_persona_context(template)

print(injected)
# 🛠️ **Engineer Mode** (Full Depth)
# 
# **Your preferences:**
# - Format: Full technical depth
# - Focus: Code, algorithms, implementation details
# - Word limit: Unlimited
# - Code visibility: Full (with examples)
# - Metrics: coverage, complexity, test_results, performance
# 
# ---
# 
# ## Task
# Optimize the database query in app/queries.py
# ...
```

---

## Example 7: Command Aliases

```python
orchestrator = PersonaOrchestrator()

# All these are equivalent
orchestrator.execute_command("/persona set ceo")
orchestrator.execute_command("/persona set executive")
orchestrator.execute_command("/persona set director")
orchestrator.execute_command("/persona set business_leader")

# All resolve to: persona_id = "business_leader"

# Verify
state = orchestrator.get_current_state()
print(state["persona_id"])  # "business_leader"
```

---

## Example 8: Multi-Turn Conversation with Mixed Depths

```python
orchestrator = PersonaOrchestrator()
orchestrator.execute_command("/persona set engineer")

# Turn 1: Default full depth
response1 = "Detailed code explanation..."
styled1 = orchestrator.style_response(response1, {})
print(f"Turn 1 words: {len(styled1.split())}")  # Unlimited

orchestrator.consume_turn()

# Turn 2: Override to executive (100 words, TTL=2)
orchestrator.execute_command("/detail executive 2")
response2 = "More detailed explanation..."
styled2 = orchestrator.style_response(response2, {})
print(f"Turn 2 words: {len(styled2.split())}")  # ~100

orchestrator.consume_turn()  # TTL: 2 → 1

# Turn 3: Still executive (TTL=1)
response3 = "Even more details..."
styled3 = orchestrator.style_response(response3, {})
print(f"Turn 3 words: {len(styled3.split())}")  # ~100

orchestrator.consume_turn()  # TTL: 1 → 0, reverts

# Turn 4: Back to full depth
response4 = "Final explanation..."
styled4 = orchestrator.style_response(response4, {})
print(f"Turn 4 words: {len(styled4.split())}")  # Unlimited again
```

---

## Example 9: Error Handling

```python
orchestrator = PersonaOrchestrator()

# Invalid persona
result = orchestrator.execute_command("/persona set invalid_role")
print(result)
# {
#   "success": false,
#   "error": "Unknown persona: invalid_role",
#   "available": ["business_leader", "product_owner", ...]
# }

# Invalid depth
result = orchestrator.execute_command("/detail invalid_depth")
print(result)
# {
#   "success": false,
#   "error": "Unknown depth: invalid_depth",
#   "available": ["executive", "standard", "detailed", "full"]
# }

# Invalid command
result = orchestrator.execute_command("/persona invalid_subcommand")
print(result)
# {
#   "success": false,
#   "error": "Invalid persona command. Use: set, show, list"
# }
```

---

## Example 10: Real-World Integration (InteractionOrchestrator)

```python
from cortex.orchestrators.core.persona_orchestrator import PersonaOrchestrator
from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator

class EnhancedInteractionOrchestrator:
    """InteractionOrchestrator with persona awareness."""
    
    def __init__(self):
        self.interaction = InteractionOrchestrator()
        self.persona = PersonaOrchestrator()
        
    def process(self, query: str, context: dict, session_id: str) -> str:
        """Process request with persona-aware response styling."""
        
        # Step 1: Handle persona commands
        if query.startswith("/persona") or query.startswith("/detail"):
            result = self.persona.execute_command(query)
            return self._format_command_result(result)
        
        # Step 2: Infer persona from context
        persona_result = self.persona.process_request(query, context)
        
        # Step 3: Get response from interaction orchestrator
        raw_response = self.interaction.process(query, context)
        
        # Step 4: Style based on active persona
        styled_response = self.persona.style_response(
            response=raw_response,
            available_metrics=context.get("metrics")
        )
        
        # Step 5: Consume turn (TTL management)
        self.persona.consume_turn()
        
        # Step 6: Persist state
        state = self.persona.serialize_state()
        self._save_session(session_id, state)
        
        return styled_response
    
    def _format_command_result(self, result: dict) -> str:
        """Format command execution result."""
        if result.get("success"):
            return f"✅ {result['message']}"
        else:
            return f"❌ {result['error']}"
    
    def _save_session(self, session_id: str, state: dict):
        """Save session state to persistent storage."""
        # Implementation depends on storage backend
        pass


# Usage
enhanced = EnhancedInteractionOrchestrator()

# Turn 1: Set persona
response1 = enhanced.process(
    query="/persona set tech_lead",
    context={},
    session_id="user123"
)
# ✅ Persona set to tech_lead

# Turn 2: Process query with tech_lead formatting
response2 = enhanced.process(
    query="Show me the test coverage for authentication module",
    context={
        "file_path": "tests/auth/test_login.py",
        "metrics": {"coverage": 0.89, "complexity": 12}
    },
    session_id="user123"
)
# Response formatted with architecture + metrics (tech_lead persona)
```

---

## Example 11: Inference Signal Weights

```python
orchestrator = PersonaOrchestrator()

# High technical vocabulary + Python file + code question
context_engineer = {
    "query": "How should I implement async context managers with __aenter__?",
    "file_path": "cortex/core/async_manager.py",
    "vocabulary_complexity": 0.92,  # Very technical
    "session_history": []
}

result = orchestrator.process_request(
    query=context_engineer["query"],
    context=context_engineer
)
print(result["persona_id"])  # "engineer" (high confidence)

# Business vocabulary + metrics question
context_leader = {
    "query": "What's our quarterly ROI on the testing infrastructure investment?",
    "file_path": None,
    "vocabulary_complexity": 0.35,  # Simple vocabulary
    "session_history": []
}

result = orchestrator.process_request(
    query=context_leader["query"],
    context=context_leader
)
print(result["persona_id"])  # "business_leader" (high confidence)

# Mixed signals → lower confidence
context_mixed = {
    "query": "Tell me about async generators",
    "file_path": "presentation.pptx",  # Non-code file
    "vocabulary_complexity": 0.65,  # Medium
    "session_history": []
}

result = orchestrator.process_request(
    query=context_mixed["query"],
    context=context_mixed
)
print(result["confidence"])  # 0.55 (below 0.7 threshold)
# Falls back to discovery mode
```

---

## Example 12: Sticky vs Non-Sticky Depth

```python
orchestrator = PersonaOrchestrator()
orchestrator.execute_command("/persona set engineer")

# Non-sticky: Expires after 1 turn
orchestrator.execute_command("/detail executive")
state1 = orchestrator.get_current_state()
print(state1["depth_id"])  # "executive"

orchestrator.consume_turn()  # Expires
state2 = orchestrator.get_current_state()
print(state2["depth_id"])  # "full" (reverted to engineer default)

# Sticky: Persists until reset
orchestrator.execute_command("/detail executive sticky")
state3 = orchestrator.get_current_state()
print(state3["depth_id"])  # "executive"

orchestrator.consume_turn()  # Does NOT expire
orchestrator.consume_turn()  # Still active
orchestrator.consume_turn()  # Still active

state4 = orchestrator.get_current_state()
print(state4["depth_id"])  # "executive" (still active)

# Reset to default
orchestrator.execute_command("/detail reset")
state5 = orchestrator.get_current_state()
print(state5["depth_id"])  # "full" (engineer default)
```

---

**See also:**
- [README-PERSONAS.md](./README-PERSONAS.md) — Main documentation
- [API-REFERENCE.md](./API-REFERENCE.md) — Complete API documentation
- [INTEGRATION-GUIDE.md](./INTEGRATION-GUIDE.md) — Integration patterns
