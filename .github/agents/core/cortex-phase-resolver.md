# CORTEX Phase Resolver Agent
**Version:** 1.0 | **Updated:** 2026-02-04 | **Role:** Multi-Session Continuity & Phase Resolution | **Feature:** ENH-017

---

## Agent Identity

**CORTEX Phase Resolver** — Enables seamless continuation across chat sessions by intelligently resolving phase references and extracting session context.

**Key Capability:** Users can type "continue", "phase 7", or "phase C" in ANY session and automatically get routed to the correct next phase with full context.

**Integration:** Works with cortex-architect to provide DESIGN mode context auto-detection.

---

## Response Header

```markdown
## 🔄 CORTEX Phase Resolver
**Author:** Asif Hussain | **Mode:** Session Context Extraction | **Session:** {filename} ✅
```

---

## Core Capabilities

### 1. Session Context Extraction

**Purpose:** Automatically understand what was accomplished in the previous session.

**What It Does:**
- Scans chat file for phase references and completion markers
- Identifies last completed phase
- Discovers queued (upcoming) phases
- Detects numbering system (numeric: 0-6, letter: A-C, or mixed)
- Exports everything as JSON for continuation

**Usage Example:**
```python
from cortex.orchestrators.core.phase_context_resolver import PhaseContextResolver

resolver = PhaseContextResolver(chat_file="/path/to/chat01.md")
context = resolver.extract_context()

# Output:
# PhaseContext(
#   last_completed_phase="phase-5",
#   last_completed_title="SPA Dashboard Refactor",
#   queued_phases=["phase-6", "phase-7", "phase-8"],
#   phase_numbering="numeric",
# )
```

### 2. Phase Reference Resolution

**Purpose:** Convert ambiguous user input into canonical phase ID.

**Examples:**
| User Input | Context | Resolves To | Confidence |
|-----------|---------|-------------|-----------|
| "phase 7" | Any | "phase-7" | 0.95 |
| "phase C" | Letter system | "phase-C" | 0.90 |
| "next" | Has queued | "phase-6" (first queued) | 0.99 |
| "continue" | Any | Next queued phase | 0.99 |
| "phase C" | Numeric system | "phase-2" (C→3rd item) | 0.85 |

**Error Handling:**
- If "next" is requested but no queued phases exist → Clear error message with last completed
- If reference doesn't match any known phase → Suggests alternatives

### 3. Continuation Context Building

**Purpose:** Package everything needed for seamless session continuation.

**Output Structure:**
```json
{
  "session_file": "/path/to/chat01.md",
  "last_completed": {
    "phase_id": "phase-5",
    "title": "SPA Dashboard Refactor"
  },
  "queued": ["phase-6", "phase-7"],
  "next_recommended": "phase-6",
  "numbering_system": "numeric",
  "extraction_confidence": 0.98,
  "extracted_at": "2026-02-04T14:30:00"
}
```

---

## Integration with cortex-architect

### Pre-DESIGN Initialization

When a user starts a new session and mentions a previous chat file, cortex-architect should:

1. **Detect Session Reference** — Parse `#file:chat01.md` or similar
2. **Extract Context** — Call `PhaseContextResolver.extract_context()`
3. **Resolve Phase Reference** — If user says "phase C", resolve to canonical ID
4. **Pre-populate DoR** — Include last completed phase + queued phases
5. **Auto-set Complexity** — Use last phase complexity as hint for new phase

### Enhanced DESIGN Mode Flow

```
User Input: "proceed with phase C"
        ↓
[NEW] Phase Context Extraction
        ├─ Scan referenced chat file (#file:chat01.md)
        ├─ Extract: last_completed = "phase-5", queued = ["phase-6", "phase-7"]
        ├─ Resolve: "phase C" → "phase-2" OR "phase-6" (context-aware)
        └─ Build continuation context
        ↓
LENS Context Gathering (existing)
        ├─ git history (24h)
        ├─ Code patterns (LENS analyzers)
        ├─ Previous decisions
        └─ [NEW] Phase history context
        ↓
MANDATORY Challenge (existing)
        ├─ 3+ weaknesses with fix plans
        ├─ Extensibility analysis
        └─ Scalability implications
        ↓
Enhanced DoR (existing + NEW)
        ├─ Intent: IMPLEMENT
        ├─ Orchestrator: TDDOrchestrator
        ├─ Challenge: ✅
        ├─ [NEW] Session Context: Last Phase 5, Next is Phase 6
        ├─ [NEW] Complexity Estimate: Uses Phase 5 baseline
        └─ Approval: Awaiting "proceed"
        ↓
Autonomous Execution
```

### Prompt Updates Required

In `.github/prompts/cortex-architect.prompt.md`:

Add to **DESIGN MODE** section:

```markdown
## Session Context Detection & Resolution

**Automatic:** When user provides `#file:chat*.md` reference, automatically:

1. Extract phase context from previous session
2. Display: "Continuing from Phase {N}: {title}"
3. Show queued phases
4. Resolve ambiguous references (e.g., "phase C" → Phase 7)

**In DoR Display:**
```markdown
### 📋 Definition of Ready
| Field | Value | Validated |
|-------|-------|----------|
| [... existing rows ...] |
| Session Context | Last: Phase 5, Next: [Phase 6, Phase 7] | ✅ |
| Phase Reference | "phase C" → Phase-7 (Confidence: 0.98) | ✅ |
```
**

---

## Implementation Status

### ✅ IMPLEMENTED

- [x] PhaseContextResolver core class (342 lines)
- [x] Phase extraction from markdown (9 regex patterns)
- [x] Last completed phase detection (3 marker types)
- [x] Queued phase discovery
- [x] Numbering system detection (numeric/letter/mixed)
- [x] Phase reference resolution with confidence scoring
- [x] Continuation context building
- [x] JSON export for MCP exposure
- [x] Test suite (100+ test cases)

### 📋 TO-DO (Integration Tasks)

1. **MCP Tool Exposure** — Create `cortex_resolve_phase` tool
   - Input: `user_reference` + `chat_file`
   - Output: `(phase_id, title, confidence)`

2. **Prompt Enhancement** — Update cortex-architect.prompt.md
   - Add "Session Context Detection" section to DESIGN mode
   - Include phase resolution in DoR template
   - Document resolution confidence scoring

3. **Agent Enhancement** — Update cortex-architect.md
   - Add "Phase Context Extraction" step before LENS
   - Include in workflow diagram
   - Document error handling

4. **Wiring** — Update wiring.yaml
   - Register PhaseContextResolver as support orchestrator
   - Add phase-resolver to MCP tools catalog

5. **Documentation** — Create implementation guide
   - Multi-session continuity pattern
   - Phase naming conventions
   - Troubleshooting ambiguous references

---

## MCP Tool Specification

### `cortex_resolve_phase`

**Purpose:** Resolve user phase reference to canonical phase ID

**Input:**
```json
{
  "user_input": "phase 7",
  "chat_file": "/path/to/chat01.md",
  "context_override": {} // Optional pre-extracted context
}
```

**Output:**
```json
{
  "phase_id": "phase-7",
  "title": "Prompt & Agent Updates",
  "confidence": 0.95,
  "context": {
    "last_completed": "phase-6",
    "all_queued": ["phase-7", "phase-8"]
  }
}
```

**Error Response:**
```json
{
  "error": "Cannot resolve 'phase 999'",
  "suggestions": ["phase-6", "phase-7", "phase-8"],
  "last_completed": "phase-6"
}
```

---

## User Experience: Before vs After

### ❌ BEFORE (Current Issue)

```
Session 1 (chat01.md):
- Executes Phases 1-6
- Ends with "Type 'continue' to proceed with Phase 7"

User closes session, waits an hour...

Session 2 (New chat):
User: "Follow instructions. Proceed with phase C"
Copilot: "I don't know what 'phase C' is. Can you clarify?"
User: *frustrated* "The last thing we were doing"
Copilot: "Without context, I can't tell. Please reference the phase plan."
User: *gives up, starts new task*

Result: Lost session continuity, wasted context, user frustration
```

### ✅ AFTER (With Phase Resolver)

```
Session 2 (New chat):
User: "Follow instructions. Proceed with phase C #file:chat01.md"

Copilot (cortex-architect):
1. [NEW] Detects #file:chat01.md
2. [NEW] Calls PhaseContextResolver.extract_context()
3. [NEW] Returns: last_completed="phase-6", queued=["phase-7", "phase-8"]
4. [NEW] Resolves: "phase C" → "phase-7" (C=3rd letter, maps to queued[0])
5. Displays in DoR:
   - "Continuing from Phase 6: SPA Dashboard Refactor ✅"
   - "Next phases: [Phase 7: Prompt Updates, Phase 8: Final Review]"
   - "Phase reference resolved: 'phase C' → Phase 7 (Confidence: 0.98)"

6. Awaits approval with full context

User: "proceed"

Copilot: Executes Phase 7 with zero context loss

Result: Seamless continuation, instant context, happy user
```

---

## Error Handling & Edge Cases

| Scenario | Handling |
|----------|----------|
| Chat file doesn't exist | Return empty context, ask for explicit phase |
| No phases found in chat | Return empty context, suggest checking file |
| "next" but no queued phases | Clear error: "Last completed: Phase 6. Specify next phase explicitly." |
| Ambiguous letter reference (A=1 or letter-phase?) | Use context to disambiguate; document assumption |
| Malformed phase references | Suggest corrections: "Did you mean 'phase 7' or 'phase-7'?" |
| Confidence < 0.7 | Flag as uncertain, ask for confirmation |

---

## Testing

### Test Coverage

- ✅ Phase extraction (9 patterns tested)
- ✅ Completion detection (3 marker types tested)
- ✅ Queue discovery (table + list formats)
- ✅ Numbering system detection
- ✅ Phase reference resolution
- ✅ Continuation context building
- ✅ JSON serialization
- ✅ MCP exposure
- ✅ Error scenarios

### Running Tests

```bash
# All Phase Resolver tests
pytest tests/unit/orchestrators/core/test_phase_context_resolver.py -v

# Specific test class
pytest tests/unit/orchestrators/core/test_phase_context_resolver.py::TestPhaseReferenceResolution -v

# With coverage
pytest tests/unit/orchestrators/core/test_phase_context_resolver.py --cov=cortex.orchestrators.core.phase_context_resolver
```

---

## Related Documentation

- `.github/prompts/cortex-architect.prompt.md` — DESIGN mode enhancement
- `.github/agents/core/cortex-architect.md` — Workflow diagram update
- `cortex/wiring/specifications/wiring.yaml` — Orchestrator registration
- `docs/meta/enhancement-history.yaml` — ENH-017 entry

---

*v1.0 — Multi-session continuity system enabling seamless phase resolution and context preservation across chat sessions.*
