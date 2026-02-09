# Role-Adaptive Persona System

**Author:** Asif Hussain | **Phase:** 37 | **Version:** 1.0

---

## Overview

The **Role-Adaptive Persona System** intelligently adapts CORTEX responses based on user roles, providing tailored formatting, depth levels, and content filtering. The system supports 6 distinct personas (business_leader, product_owner, scrum_master, tech_lead, engineer, unknown) and 4 depth levels (executive, standard, detailed, full).

**Key Features:**
- 🎯 **Role Detection** — Infers user role from context signals (vocabulary, file type, query patterns)
- 📊 **Response Formatting** — BLUF for executives, full technical depth for engineers
- 🔄 **Dynamic Switching** — `/persona` and `/detail` commands for on-the-fly changes
- 💾 **Session Persistence** — Persona state retained across conversation turns
- ⏱️ **TTL Management** — Temporary depth overrides with automatic expiration
- 🔌 **MCP Integration** — Ready for MCP tool exposure (Stage 37.4)

---

## Quick Start

### Basic Usage

```python
from cortex.orchestrators.core.persona_orchestrator import PersonaOrchestrator

# Initialize orchestrator
orchestrator = PersonaOrchestrator()

# Process request with inference
result = orchestrator.process_request(
    query="How should I optimize this database query?",
    context={
        "file_path": "app/database/queries.py",
        "vocabulary_complexity": 0.85
    }
)

# Result: {'persona_id': 'engineer', 'depth_id': 'full', 'confidence': 0.88}
```

### Response Styling

```python
# Style response based on active persona
raw_response = "Query optimization requires indexing strategy and connection pooling."

styled = orchestrator.style_response(
    response=raw_response,
    available_metrics={"vocabulary_complexity": 0.85}
)

# Engineer persona: Full technical details
# Business Leader persona: High-level summary with BLUF
```

### Template Injection

```python
# Inject persona context into prompts
template = """
{{PERSONA_INJECTION_POINT}}

User Query: How can I improve performance?
"""

injected = orchestrator.inject_persona_context(template)

# Result includes persona guidance:
# 👔 **Business Leader Mode** (Executive Depth)
# You prefer: Bottom Line Up Front (BLUF), ROI metrics, business impact
# Word limit: 150 words
```

---

## Available Personas

### 1. Business Leader 👔
- **Audience:** C-suite, VPs, directors
- **Format:** BLUF (Bottom Line Up Front)
- **Depth:** Executive (100 words)
- **Content:** Outcomes, metrics, ROI, business impact
- **Code Visibility:** Hidden
- **Metrics:** ROI, KPIs, business_impact

**Example Response:**
```
**Bottom Line:** Query optimization will reduce page load time by 40% (2.5s → 1.5s), 
improving user retention by estimated 8%. Implementation cost: 2 engineering days.

**Key Actions:**
1. Add database indexes (1 day)
2. Implement connection pooling (1 day)

**ROI:** $15k annual infrastructure savings from reduced database load.
```

### 2. Product Owner 📋
- **Audience:** Product managers, product owners
- **Format:** Narrative with user focus
- **Depth:** Business (300 words)
- **Content:** Features, user value, velocity
- **Code Visibility:** Hidden
- **Metrics:** velocity, feature_progress, user_impact

**Example Response:**
```
Query optimization delivers direct user value through faster page loads:

**User Impact:**
- 40% faster dashboard rendering (2.5s → 1.5s)
- Reduced bounce rate (users wait for results)
- Better mobile experience on slow connections

**Feature Progress:**
- Sprint 12: Database indexing (5 story points)
- Sprint 12: Connection pooling (3 story points)

**Dependencies:** None (isolated optimization)
**Risks:** Minimal, non-breaking change
```

### 3. Scrum Master 🏃
- **Audience:** Agile coaches, scrum masters
- **Format:** Action-oriented with process focus
- **Depth:** Process (300 words)
- **Content:** Sprint metrics, velocity, blockers
- **Code Visibility:** Hidden
- **Metrics:** sprint_metrics, velocity, blockers

### 4. Tech Lead / Manager 🏗️
- **Audience:** Technical leaders, engineering managers
- **Format:** Architecture + metrics
- **Depth:** Technical-Business (500 words)
- **Content:** Architecture, health metrics, tech debt
- **Code Visibility:** Diagrams only
- **Metrics:** health_metrics, coverage, complexity, tech_debt

**Example Response:**
```
**Architecture Impact:**
Query optimization requires two infrastructure changes:

1. **Database Layer:**
   - Add composite indexes on user_id + created_at
   - Estimated query time: 2.5s → 0.8s (68% reduction)

2. **Connection Management:**
   - Implement connection pooling (max 20 connections)
   - Reduce connection overhead: 200ms → 5ms

**Metrics:**
- Coverage: Maintain 90%+ (new tests added)
- Complexity: No increase (refactoring only)
- Tech Debt: Reduces by 15% (removes N+1 queries)

**Timeline:** 2 days, no blockers
```

### 5. Engineer 🛠️
- **Audience:** Software developers, engineers
- **Format:** Full technical depth
- **Depth:** Full (unlimited)
- **Content:** Code, algorithms, implementation details
- **Code Visibility:** Full
- **Metrics:** coverage, complexity, test_results, performance

**Example Response:**
```python
# Query Optimization Implementation

# Before: N+1 query problem
users = User.query.all()
for user in users:
    posts = Post.query.filter_by(user_id=user.id).all()  # N queries!

# After: Single query with eager loading
users = User.query.options(
    db.joinedload(User.posts)
).all()

# Index creation
CREATE INDEX idx_posts_user_created 
ON posts(user_id, created_at DESC);

# Connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

# Performance metrics:
# - Query time: 2.5s → 0.8s (68% faster)
# - Connection overhead: 200ms → 5ms (97% faster)
# - Database load: -45% (fewer queries)

# Test coverage: 94% (added 12 tests)
```

### 6. Unknown (Discovery Mode) ❓
- **Trigger:** Role not yet determined
- **Behavior:** Initiates discovery flow
- **Purpose:** Ask user to specify role explicitly

---

## Commands

### `/persona` Command

Set or query active persona:

```
/persona set business_leader     # Switch to business leader mode
/persona set engineer            # Switch to engineer mode
/persona show                    # Display current persona
/persona list                    # List all available personas
```

**Aliases supported:**
- `ceo`, `executive`, `director` → business_leader
- `pm`, `po` → product_owner
- `sm`, `agile_coach` → scrum_master
- `tl`, `manager`, `em` → tech_lead
- `dev`, `developer`, `swe` → engineer

### `/detail` Command

Override depth level (temporary or sticky):

```
/detail executive               # Next 1 turn only (TTL=1)
/detail standard                # Next 1 turn only
/detail detailed                # Next 1 turn only
/detail full                    # Next 1 turn only

/detail executive 3             # Next 3 turns (TTL=3)
/detail standard sticky         # Persist for entire session

/detail show                    # Display current depth
/detail reset                   # Reset to persona default
```

**Depth Levels:**
- **executive:** 100 words, high-level only
- **standard:** 300 words, balanced detail
- **detailed:** 500 words, comprehensive
- **full:** Unlimited, complete technical depth

**TTL Behavior:**
- Default: TTL=1 (expires after 1 turn)
- Explicit TTL: `/detail executive 3` (expires after 3 turns)
- Sticky: `/detail standard sticky` (persists until reset)

---

## Examples

See **[PERSONA-EXAMPLES.md](./PERSONA-EXAMPLES.md)** for comprehensive examples including:
- Basic persona switching workflow
- Depth override with TTL
- Inference from context signals
- Session persistence and serialization
- Error handling
- Multi-turn conversations

---

## Architecture

### Component Overview

```
PersonaOrchestrator
├── RoleResolver         # Infers role from context signals
├── PersonaLoader        # Loads personas.yaml (cached)
├── DepthManager         # Manages depth overrides with TTL
├── ResponseStyler       # Formats responses per persona
├── PersonaInjector      # Injects context into templates
├── PersonaCommandHandler  # Handles /persona commands
└── DetailCommandHandler   # Handles /detail commands
```

### Configuration

All personas defined in **`cortex/config/personas.yaml`**:

```yaml
personas:
  business_leader:
    id: "business_leader"
    display_name: "Business Leader"
    format: "BLUF"
    depth: "executive"
    word_limit: 150
    show_code: false
    show_metrics: true
    metric_types: ["ROI", "KPIs", "business_impact"]
    
  # ... 5 more personas ...
  
depths:
  executive:
    id: "executive"
    display_name: "Executive"
    word_limit: 100
    description: "High-level overview only"
    
  # ... 3 more depths ...
```

---

## Integration

### With InteractionOrchestrator

```python
from cortex.orchestrators.core.persona_orchestrator import PersonaOrchestrator
from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator

interaction = InteractionOrchestrator()
persona_orch = PersonaOrchestrator()

# Process user request with persona awareness
def handle_request(query: str, session_id: str):
    # Step 1: Check for persona commands
    if query.startswith("/persona") or query.startswith("/detail"):
        result = persona_orch.execute_command(query)
        return result
    
    # Step 2: Infer persona from context
    context = get_session_context(session_id)
    persona_result = persona_orch.process_request(query, context)
    
    # Step 3: Get response from interaction orchestrator
    response = interaction.process(query, context)
    
    # Step 4: Style response based on persona
    styled = persona_orch.style_response(response, context.get("metrics"))
    
    # Step 5: Consume turn (decrement TTL if override active)
    persona_orch.consume_turn()
    
    return styled
```

### With Prompt Templates

All CORTEX prompts can include persona context:

```markdown
{{PERSONA_INJECTION_POINT}}

Your task: [user request here]
```

PersonaInjector replaces marker with formatted guidance:

```markdown
👔 **Business Leader Mode** (Executive Depth)

**Your preferences:**
- Format: Bottom Line Up Front (BLUF)
- Focus: Business outcomes, ROI, metrics
- Word limit: 150 words
- Code visibility: Hidden

---

Your task: [user request here]
```

---

## Session Persistence

### Serialize State

```python
# Save state to JSON
state = orchestrator.serialize_state()
# {
#   "current_persona": "engineer",
#   "current_depth": "full",
#   "depth_override": null,
#   "switch_history": [...]
# }

save_to_session(session_id, state)
```

### Restore State

```python
# Restore from previous session
state = load_from_session(session_id)
orchestrator.restore_state(state)

# Persona and depth preserved
assert orchestrator.get_current_state() == {
    "persona_id": "engineer",
    "depth_id": "full"
}
```

---

## Testing

**Total Tests:** 19 integration + 45 unit = 64 tests  
**Coverage:** 95%+  
**Test Suites:**
- `tests/unit/orchestrators/test_role_resolver.py` (12 tests)
- `tests/unit/orchestrators/test_persona_loader.py` (8 tests)
- `tests/unit/orchestrators/test_depth_manager.py` (5 tests)
- `tests/unit/orchestrators/test_response_styler.py` (5 tests)
- `tests/unit/orchestrators/test_persona_injector.py` (5 tests)
- `tests/unit/orchestrators/test_persona_commands.py` (10 tests)
- `tests/integration/test_persona_integration.py` (19 tests)

Run tests:
```bash
pytest tests/integration/test_persona_integration.py -v  # 19/19 passing
```

---

## API Reference

See **[API-REFERENCE.md](./API-REFERENCE.md)** for complete method documentation.

---

## Troubleshooting

### Persona Not Detected

If inference fails (confidence < 0.7), system falls back to discovery mode:

```python
result = orchestrator.process_request(query, context)
if result["confidence"] < 0.7:
    # Trigger discovery: Ask user to specify role
    print("I'm not sure about your role. Use /persona set <role>")
```

### Depth Override Not Working

Ensure you call `consume_turn()` after each response:

```python
orchestrator.execute_command("/detail executive 3")  # TTL=3
orchestrator.consume_turn()  # TTL=2
orchestrator.consume_turn()  # TTL=1
orchestrator.consume_turn()  # TTL=0, reverts to default
```

### Word Limit Not Applied

Depth word limit overrides persona default:

```python
# Engineer persona has unlimited word_limit
# But executive depth has word_limit=100
# Result: 100 words (depth takes precedence)
```

---

## Future Enhancements (Phase 37.4+)

**MCP Tools (Stage 37.4):**
- `cortex_set_persona` — Set primary persona
- `cortex_get_persona` — Get current state
- `cortex_set_depth` — Override depth
- `cortex_infer_persona` — Context-based inference
- `cortex_persona_history` — View switch history

**Persistent Storage (Stage 37.4):**
- Cross-session persona recall
- User preferences stored in `cortex_brain/state/user_personas.yaml`
- Automatic role detection from history

---

## Contributing

When adding new personas:

1. Update `cortex/config/personas.yaml`
2. Add tests in `tests/unit/orchestrators/test_persona_loader.py`
3. Update this README with examples
4. Verify integration tests pass

---

**Last Updated:** 2026-02-07  
**Phase:** 37 (Role-Adaptive Personas)  
**Status:** Stage 4 Complete (19/19 tests passing)
