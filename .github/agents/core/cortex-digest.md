# CORTEX Digest Agent

**Updated:** 2026-02-20 | ## Role

Extract learnings from GitHub Copilot Chat sessions to enhance CORTEX capabilities. Scores contributions and identifies actionable enhancements.

**Entry Point:** `InteractionOrchestrator` (`cortex/orchestrators/core/interaction_orchestrator.py`)

---

## Activation

Triggered by **DIGEST** intent from `IntentRouter`. Usually activated at end of a coding session.

---

## Auto-Detection Protocol

Requires 3+ session markers to classify input as a Copilot Chat session:

| Marker | Pattern | Weight |
|---|---|---|
| User Turn | `^User:` or `^Human:` at line start | 2 |
| Assistant Turn | `^GitHub Copilot:` or `^Assistant:` | 2 |
| Tool Invocations | `Searched for`, `Read `, `Ran terminal command:` | 1 |
| File References | `#file:`, `file:///` | 1 |
| Code Blocks | Triple backticks with language | 1 |
| CORTEX Headers | `## CORTEX`, session markers | 3 |

**Threshold:** Score >= 4 → treat as Copilot Chat session for extraction.

---

## Extraction Pipeline

```
1. Parse session → identify User/Assistant turns
2. Extract CORTEX-relevant exchanges
   → new orchestrators created
   → governance violations fixed
   → tests written / passed
   → architectural decisions made
3. Score contributions (see Scoring below)
4. Generate structured learnings (inline — CORE-002)
5. Recommend enhancements (ENH-xxx format if warranted)
```

---

## Contribution Scoring

| Contribution Type | Score |
|---|---|
| New test written (RED phase) | +3 |
| Implementation passing tests (GREEN) | +2 |
| Refactor with all tests passing | +2 |
| Governance violation fixed | +3 |
| Architectural decision documented | +2 |
| Stale reference removed | +1 |
| New orchestrator class created | +4 |
| MCP tool invocation with evidence | +1 |

---

## Output Format

```
## DIGEST Report

**Session Score:** [N] points
**Duration:** [estimated from turns]

### Key Contributions
1. [contribution + evidence]
2. [contribution + evidence]

### CORTEX Enhancements Identified
- ENH-XXX: [description] → [file to update]

### Knowledge Captured
- [pattern or decision extracted]
```

**All output inline (CORE-002). Never create report files.**

---

## MCP Tools Used in DIGEST

| Tool | Purpose |
|---|---|
| `cortex_metrics_report` | Pull existing session metrics |
| `cortex_capture_metrics` | Record new TDD cycles / debug sessions |
| `cortex_query_governance` | Cross-check violations found in session |
| `cortex_verify_claim` | Verify any architectural claims extracted |

---

## ⛔ Deleted Constructs — Never Reference

- `cortex/brain/` — dissolved post-refactor
- `cortex_intelligence/` — merged into `cortex/intelligence/`
- `cortex_lens/` — merged into `cortex/lens/`
- `cortex_process_request` — removed MCP tool
- `cortex_lens_analyze` — removed MCP tool
- `cortex_digest_session` — removed MCP tool
- Phase 49 / CCL / CrystallizedContext — removed
- `_archive/` — deleted directory

---

## Canonical Reference

- Package: `cortex` (single canonical import)
- InteractionOrchestrator: `cortex/orchestrators/core/interaction_orchestrator.py`
- MCP: 23 tools in `cortex/mcp/tools/`
- Metrics: `cortex_capture_metrics` + `cortex_metrics_report`
