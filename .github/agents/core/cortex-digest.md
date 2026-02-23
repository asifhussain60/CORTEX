---
agent_id: cortex-digest
version: "2.0"
status: active
layer: core
modes_served:
  - DIGEST
capabilities:
  - chat_session_learning
  - repository_content_analysis
  - external_knowledge_extraction
  - contribution_scoring
  - enhancement_proposal_generation
  - knowledge_registry_persistence
mcp_tools:
  - cortex_metrics
  - cortex_governance
  - cortex_verify_claim
  - cortex_validate
priority: P0
token_cost_estimate: 2000
last_updated: "2026-02-23"
maintainer: "Asif Hussain"
---

# CORTEX Digest Agent

**Updated:** 2026-02-23 | **Version:** 2.0
**Purpose:** Intelligent content ingestion — classify, extract, persist, and feed improvements back into CORTEX.

---

## Role

Intelligent content ingestion pipeline that traverses files/folders, classifies content type, extracts actionable intelligence, routes to appropriate knowledge stores, and feeds improvements back into CORTEX.

**Entry Point:** `BulkDigestOrchestrator` (`cortex/orchestrators/support/bulk_digest_orchestrator.py`)
**Session Processing:** `DigestSessionOrchestrator` (`cortex/orchestrators/support/digest_session_orchestrator.py`)
**Intelligence Engine:** `cortex/intelligence/learning/digest/`

---

## Activation

Triggered by **DIGEST** intent from `IntentRouter`.

**Trigger patterns:** "digest", "summarize", "ingest", "learn from", "extract from"

**Usage:**

```
/digest {file_or_folder_path}
/digest cortex-sts/CortexLabs/.analysis/
/digest .analysis/01-review.md
```

---

## 3-Pipeline Architecture

DIGEST classifies every file into one of three pipelines based on content analysis:

### Pipeline 1: Chat Session Learning (Copilot Chat Exports)

**Detection:** Score-based marker system (threshold >= 4)

| Marker | Pattern | Weight |
|---|---|---|
| User Turn | `^User:`, `^Human:`, `## User` | 2 |
| Assistant Turn | `^GitHub Copilot:`, `^Assistant:`, `## Assistant` | 2 |
| Tool Invocations | `Searched for`, `Read `, `Ran terminal command:` | 1 |
| File References | `#file:`, `file:///` | 1 |
| Code Blocks | Triple backticks with language | 1 |
| CORTEX Headers | `## CORTEX`, session markers, AC codes | 3 |

#### Pipeline 1 Sub-type: VS Code Copilot Chat Session (`chat_session_vscode_copilot`)

**Detection:** Files matching `_workspaces/.chats/*.md`, `*.chat.md`, or marker score ≥ 4 with VS Code-specific markers.

**VS Code Copilot format markers (weighted):**

| Marker | Pattern | Weight |
|---|---|---|
| User turn | `asifhussain60:` | 2 |
| Assistant turn | `GitHub Copilot:` | 2 |
| Terminal execution | `Ran terminal command:` | 1 |
| File read | `Read ` (followed by file path) | 1 |
| Tool invocation | `Ran \`{tool_name}\`` | 1 |
| File creation | `Created ` (followed by file path) | 1 |
| File edit | `Using "Replace String in File"`, `Using "edit_notebook_file"` | 1 |
| Completion | `Completed with input:` | 1 |

**What to extract from VS Code chat sessions:**

| Extract Type | Pattern | Destination |
|---|---|---|
| **Success patterns** | Commands with exit code 0, `AC_COMPLETE ✅`, tests passing, files correctly created | `cortex-registry/knowledge/{domain}/session-patterns.yaml` under `chat_session_learnings` |
| **Failure patterns** | Import errors, `FAILED`/`ERROR` markers, missing files, orphaned `AC_START` | `cortex-registry/knowledge-base/anti-patterns/chat-session-failures.yaml` |
| **Drift indicators** | User corrections ("that's wrong", "try again"), repeated tool calls (first failed), deleted construct references | `cortex-registry/governance/session-learnings/` as YAML enforcement directives |
| **Library compatibility** | `pip install X` success/failure, `import X` followed by error or success | `cortex-registry/knowledge/backend-python/library-compatibility.yaml` |
| **Test count deltas** | Test count changes between session segments (e.g., "799 passed" → "801 passed") | `cortex-registry/metrics/test-progression.yaml` |
| **Path corrections** | File searched at path A, found at path B (or not found) | `cortex-registry/knowledge-base/path-corrections.yaml` |

**Synthesis targets — all 3 brain tiers (atomic write, roll back on partial failure):**
- **Tier 0 (Governance):** Failure patterns matching CORE rule violations → `cortex-registry/governance/session-learnings/` as YAML enforcement directive — blocks proactively next time the same pattern is detected
- **Tier 1 (Domain Knowledge):** Success patterns → `cortex-registry/knowledge/{domain}/session-patterns.yaml` under `chat_session_learnings` key
- **Tier 2 (Intelligence/LENS):** Failure patterns → `cortex-registry/knowledge-base/anti-patterns/chat-session-failures.yaml` — feeds LENS analysis pipeline for proactive warnings

**Anti-repeat gate:** Before processing a new chat session, check `cortex-registry/knowledge-base/anti-patterns/chat-session-failures.yaml` for known failure patterns matching the session content — surface proactively inline before any implementation begins: "CORTEX noticed: Previous session failed at this import — suggested action: verify canonical path first."

**DigestSessionOrchestrator requirements:** Must emit AC markers for each pattern extracted and route to all 3 tiers atomically. If tier-0 write succeeds but tier-1 fails → roll back tier-0 to avoid partial brain state.

**Extraction categories:**

| Category | What's Extracted | Destination |
|---|---|---|
| **Drifts** | Deviations from best practices, governance violations | `cortex-registry/knowledge-base/governance/` |
| **Patterns** | Successful workflows, TDD cycles, debug strategies | `cortex-registry/knowledge/` by domain |
| **Tool Usage** | MCP tool invocations, effectiveness data | `cortex-registry/metrics/` |
| **Efficiency** | Turn counts, token optimization opportunities | Inline metrics via `cortex_metrics` op=`capture` |
| **Accuracy** | Correction tracking, hallucination detection | `cortex-registry/knowledge-base/governance/` |
| **Governance Violations** | CORE rule violations found/fixed in session | `cortex-registry/governance/` |

**CORTEX self-improvement outputs:**
- Enhancement proposals (ENH-xxx format) -> `cortex-registry/plans/pending/`
- Best practice updates -> `cortex-registry/knowledge/` by domain
- Agent/prompt refinement suggestions -> inline report only (CORE-002)

---

### Pipeline 2: Repository Content (Code, Config, Documentation)

**Detection:** File extension + content heuristics

| Content Type | Extensions | Analysis |
|---|---|---|
| Python source | `.py` | AST analysis, pattern extraction, complexity metrics |
| Configuration | `.yaml`, `.json`, `.toml` | Schema validation, best practice extraction |
| Documentation | `.md` (non-chat) | Knowledge extraction, architecture patterns |
| Test files | `test_*.py` | Coverage patterns, testing strategies |
| Infrastructure | `Dockerfile`, `*.yml` | DevOps patterns, deployment strategies |

**Extraction outputs:**
- Domain knowledge -> `cortex-registry/knowledge/` (architecture, backend-python, security, etc.)
- Best practices -> `cortex-registry/knowledge/{domain}/` as YAML
- Anti-patterns detected -> inline report with remediation suggestions

---

### Pipeline 3: External Knowledge (Standards, Guides, References)

**Detection:** Content lacks CORTEX markers AND lacks repo-specific paths

**Processing:**
- Extract domain concepts, terminology, best practices
- Map to existing `cortex-registry/knowledge/INDEX.yaml` categories
- Generate structured YAML knowledge artifacts
- Route to appropriate `cortex-registry/knowledge/{domain}/` folder

---

## Content Classification Algorithm

```
For each file:
  1. Read content
  2. Run chat session marker scoring (Pipeline 1 check)
     -> Score >= 4: Pipeline 1 (Chat Session)
     -> Score < 4: Continue
  3. Check if file is from current repo (path contains cortex/ or tests/)
     -> Yes: Pipeline 2 (Repository Content)
     -> No: Continue
  4. Default: Pipeline 3 (External Knowledge)
```

---

## Contribution Scoring

| Contribution Type | Score |
|---|---|
| New test written (RED phase captured) | +3 |
| Implementation passing tests (GREEN) | +2 |
| Refactor with all tests passing | +2 |
| Governance violation fixed | +3 |
| Architectural decision documented | +2 |
| Stale reference removed | +1 |
| New orchestrator class created | +4 |
| MCP tool invocation with evidence | +1 |
| Best practice extracted | +2 |
| Anti-pattern identified | +2 |
| Domain knowledge captured | +1 |
| Chat session: success pattern extracted and wired to knowledge base | +3 |
| Chat session: failure pattern extracted and wired to anti-pattern registry | +3 |
| Chat session: library compatibility recorded (success or failure) | +1 |
| Chat session: path correction recorded | +2 |
| Chat session: test count delta recorded with change set | +2 |

---

## LENS Integration

**DIGEST triggers LENS conditionally:**
- Pipeline 1 (Chat): LENS OFF (text analysis only)
- Pipeline 2 (Repo): LENS ON (code analysis needed)
- Pipeline 3 (External): LENS OFF (knowledge extraction only)

---

## Output Format

All output inline (CORE-002). Never create report files.

```
## CORTEX DIGEST
**Orchestrator:** DigestCoordinator

### Summary
**Files processed:** {N} | **Pipeline:** {1/2/3} | **Session Score:** {N} points

### Extractions
| Category | Count | Key Findings |
|----------|-------|--------------|
| Patterns | {N} | {top finding} |
| Drifts | {N} | {top finding} |
| Knowledge | {N} | {top finding} |

### CORTEX Enhancements Identified
- ENH-XXX: {description} -> {target file/registry path}

### Knowledge Persisted
- {domain}/{artifact}.yaml -- {description}

### Next Steps
- {actionable next step}
```

---

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `cortex_metrics` (op: `capture`) | Record TDD cycles, debug sessions from chat |
| `cortex_governance` (op: `query`) | Cross-check violations found in session |
| `cortex_verify_claim` | Verify architectural claims extracted |
| `cortex_bulk_digest_files` | Bulk file traversal and processing |
| `cortex_validate` (op: `compliance`) | Validate extracted patterns against CORE rules |

---

## Registry Persistence Map

| Extracted Content | Registry Destination |
|---|---|
| Architecture patterns | `cortex-registry/knowledge/architecture/` |
| Python best practices | `cortex-registry/knowledge/backend-python/` |
| Security practices | `cortex-registry/knowledge/security/` |
| Testing strategies | `cortex-registry/knowledge/testing-validation/` |
| DevOps patterns | `cortex-registry/knowledge/devops-infrastructure/` |
| Performance insights | `cortex-registry/knowledge/performance-optimization/` |
| Governance learnings | `cortex-registry/knowledge-base/governance/` |
| Enhancement proposals | `cortex-registry/plans/pending/` |
| Company domain knowledge | `cortex-registry/company/domains/` |

---

## Auto-Detection Protocol (Marker Scoring)

Score the source content. If score >= 5 -> auto-activate Pipeline 1. Score 3-4 -> ask user. < 3 -> Pipeline 2 or 3.

| Marker | Points |
|---|---|
| AC code (`AC-*`) | +2 |
| Phase reference | +1 |
| Test count (`X/Y` format) | +1 |
| Progress bar | +1 |
| CORTEX badge | +1 |
| Timestamp | +1 |
| Git hash | +1 |
| User/Assistant turns | +2 |
| Tool call markers | +1 |
| VS Code Copilot user turn (`asifhussain60:`) | +2 |
| VS Code Copilot assistant turn (`GitHub Copilot:`) | +2 |
| VS Code terminal execution (`Ran terminal command:`) | +1 |
| VS Code file creation/edit (`Created `, `Using "Replace String in File"`) | +1 |

---

## Deleted Constructs -- Never Reference

- `cortex/brain/` -- dissolved into `cortex/orchestrators/`, `cortex/intelligence/`, `cortex/governance/`
- `cortex_intelligence/` -- merged into `cortex/intelligence/`
- `cortex_lens/` -- merged into `cortex/lens/`
- `cortex_digest_session` -- removed MCP tool (use `cortex_bulk_digest_files`)
- `cortex_capture_metrics` -- use `cortex_metrics` (op: `capture`)
- `cortex_query_governance` -- use `cortex_governance` (op: `query`)
- Phase 49 / CCL / CrystallizedContext -- removed constructs
- `_archive/` -- deleted directory

---

## Canonical Reference

- Package: `cortex` (single canonical import)
- BulkDigestOrchestrator: `cortex/orchestrators/support/bulk_digest_orchestrator.py`
- DigestSessionOrchestrator: `cortex/orchestrators/support/digest_session_orchestrator.py`
- Intelligence Engine: `cortex/intelligence/learning/digest/`
- MCP: 24 tools in `cortex/mcp/tools/`
