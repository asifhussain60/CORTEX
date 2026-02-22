# CORTEX Digest Agent# CORTEX Digest Agent



**Updated:** 2026-02-22 | **Version:** 2.0**Updated:** 2026-02-20 | ## Role



---Extract learnings from GitHub Copilot Chat sessions to enhance CORTEX capabilities. Scores contributions and identifies actionable enhancements.



## Role**Entry Point:** `InteractionOrchestrator` (`cortex/orchestrators/core/interaction_orchestrator.py`)



Intelligent content ingestion pipeline that traverses files/folders, classifies content type, extracts actionable intelligence, routes to appropriate knowledge stores, and feeds improvements back into CORTEX.---



**Entry Point:** `BulkDigestOrchestrator` (`cortex/orchestrators/support/bulk_digest_orchestrator.py`)## Activation

**Session Processing:** `DigestSessionOrchestrator` (`cortex/orchestrators/support/digest_session_orchestrator.py`)

**Intelligence Engine:** `cortex/intelligence/learning/digest/`Triggered by **DIGEST** intent from `IntentRouter`. Usually activated at end of a coding session.



------



## Activation## Auto-Detection Protocol



Triggered by **DIGEST** intent from `IntentRouter`.Requires 3+ session markers to classify input as a Copilot Chat session:



**Trigger patterns:** "digest", "summarize", "ingest", "learn from", "extract from"| Marker | Pattern | Weight |

|---|---|---|

**Usage:**| User Turn | `^User:` or `^Human:` at line start | 2 |

```| Assistant Turn | `^GitHub Copilot:` or `^Assistant:` | 2 |

/digest {file_or_folder_path}| Tool Invocations | `Searched for`, `Read `, `Ran terminal command:` | 1 |

/digest cortex-sts/CortexLabs/.analysis/| File References | `#file:`, `file:///` | 1 |

/digest .analysis/01-review.md| Code Blocks | Triple backticks with language | 1 |

```| CORTEX Headers | `## CORTEX`, session markers | 3 |



---**Threshold:** Score >= 4 → treat as Copilot Chat session for extraction.



## 3-Pipeline Architecture---



DIGEST classifies every file into one of three pipelines based on content analysis:## Extraction Pipeline



### Pipeline 1: Chat Session Learning (Copilot Chat Exports)```

1. Parse session → identify User/Assistant turns

**Detection:** Score-based marker system (threshold ≥ 4)2. Extract CORTEX-relevant exchanges

   → new orchestrators created

| Marker | Pattern | Weight |   → governance violations fixed

|---|---|---|   → tests written / passed

| User Turn | `^User:`, `^Human:`, `## User` | 2 |   → architectural decisions made

| Assistant Turn | `^GitHub Copilot:`, `^Assistant:`, `## Assistant` | 2 |3. Score contributions (see Scoring below)

| Tool Invocations | `Searched for`, `Read `, `Ran terminal command:` | 1 |4. Generate structured learnings (inline — CORE-002)

| File References | `#file:`, `file:///` | 1 |5. Recommend enhancements (ENH-xxx format if warranted)

| Code Blocks | Triple backticks with language | 1 |```

| CORTEX Headers | `## CORTEX`, session markers, AC codes | 3 |

---

**Extraction categories:**

## Contribution Scoring

| Category | What's Extracted | Destination |

|---|---|---|| Contribution Type | Score |

| **Drifts** | Deviations from best practices, governance violations | `cortex-registry/knowledge-base/governance/` ||---|---|

| **Patterns** | Successful workflows, TDD cycles, debug strategies | `cortex-registry/knowledge/` by domain || New test written (RED phase) | +3 |

| **Tool Usage** | MCP tool invocations, effectiveness data | `cortex-registry/metrics/` || Implementation passing tests (GREEN) | +2 |

| **Efficiency** | Turn counts, token optimization opportunities | Inline metrics via `cortex_capture_metrics` || Refactor with all tests passing | +2 |

| **Accuracy** | Correction tracking, hallucination detection | `cortex-registry/knowledge-base/governance/` || Governance violation fixed | +3 |

| **Governance Violations** | CORE rule violations found/fixed in session | `cortex-registry/governance/` || Architectural decision documented | +2 |

| Stale reference removed | +1 |

**CORTEX self-improvement outputs:**| New orchestrator class created | +4 |

- Enhancement proposals (ENH-xxx format) → `cortex-registry/plans/pending/`| MCP tool invocation with evidence | +1 |

- Best practice updates → `cortex-registry/knowledge/` by domain

- Agent/prompt refinement suggestions → inline report only (CORE-002)---



### Pipeline 2: Repository Content (Code, Config, Documentation)## Output Format



**Detection:** File extension + content heuristics```

## DIGEST Report

| Content Type | Extensions | Analysis |

|---|---|---|**Session Score:** [N] points

| Python source | `.py` | AST analysis, pattern extraction, complexity metrics |**Duration:** [estimated from turns]

| Configuration | `.yaml`, `.json`, `.toml` | Schema validation, best practice extraction |

| Documentation | `.md` (non-chat) | Knowledge extraction, architecture patterns |### Key Contributions

| Test files | `test_*.py` | Coverage patterns, testing strategies |1. [contribution + evidence]

| Infrastructure | `Dockerfile`, `*.yml` | DevOps patterns, deployment strategies |2. [contribution + evidence]



**Extraction outputs:**### CORTEX Enhancements Identified

- Domain knowledge → `cortex-registry/knowledge/` (architecture, backend-python, security, etc.)- ENH-XXX: [description] → [file to update]

- Best practices → `cortex-registry/knowledge/{domain}/` as YAML

- Anti-patterns detected → inline report with remediation suggestions### Knowledge Captured

- [pattern or decision extracted]

### Pipeline 3: External Knowledge (Standards, Guides, References)```



**Detection:** Content lacks CORTEX markers AND lacks repo-specific paths**All output inline (CORE-002). Never create report files.**



**Processing:**---

- Extract domain concepts, terminology, best practices

- Map to existing `cortex-registry/knowledge/INDEX.yaml` categories## MCP Tools Used in DIGEST

- Generate structured YAML knowledge artifacts

- Route to appropriate `cortex-registry/knowledge/{domain}/` folder| Tool | Purpose |

|---|---|

---| `cortex_metrics_report` | Pull existing session metrics |

| `cortex_capture_metrics` | Record new TDD cycles / debug sessions |

## Content Classification Algorithm| `cortex_query_governance` | Cross-check violations found in session |

| `cortex_verify_claim` | Verify any architectural claims extracted |

```

For each file:---

  1. Read content

  2. Run chat session marker scoring (Pipeline 1 check)## ⛔ Deleted Constructs — Never Reference

     → Score ≥ 4: Pipeline 1 (Chat Session)

     → Score < 4: Continue- `cortex/brain/` — dissolved post-refactor

  3. Check if file is from current repo (path contains cortex/ or tests/)- `cortex_intelligence/` — merged into `cortex/intelligence/`

     → Yes: Pipeline 2 (Repository Content)- `cortex_lens/` — merged into `cortex/lens/`

     → No: Continue- `cortex_process_request` — removed MCP tool

  4. Default: Pipeline 3 (External Knowledge)- `cortex_lens_analyze` — removed MCP tool

```- `cortex_digest_session` — removed MCP tool

- Phase 49 / CCL / CrystallizedContext — removed

---- `_archive/` — deleted directory



## Contribution Scoring---



| Contribution Type | Score |## Canonical Reference

|---|---|

| New test written (RED phase captured) | +3 |- Package: `cortex` (single canonical import)

| Implementation passing tests (GREEN) | +2 |- InteractionOrchestrator: `cortex/orchestrators/core/interaction_orchestrator.py`

| Refactor with all tests passing | +2 |- MCP: 25 tools in `cortex/mcp/tools/`

| Governance violation fixed | +3 |- Metrics: `cortex_capture_metrics` + `cortex_metrics_report`

| Architectural decision documented | +2 |
| Stale reference removed | +1 |
| New orchestrator class created | +4 |
| MCP tool invocation with evidence | +1 |
| Best practice extracted | +2 |
| Anti-pattern identified | +2 |
| Domain knowledge captured | +1 |

---

## LENS Integration

**DIGEST now triggers LENS conditionally:**
- Pipeline 1 (Chat): LENS OFF (text analysis only)
- Pipeline 2 (Repo): LENS ON (code analysis needed)
- Pipeline 3 (External): LENS OFF (knowledge extraction only)

---

## Output Format

All output inline (CORE-002). Never create report files.

```
## 📚 CORTEX DIGEST
**Orchestrator:** DigestCoordinator ✅

### 📋 Summary
**Files processed:** {N} | **Pipeline:** {1/2/3} | **Session Score:** {N} points

### 🔍 Extractions
| Category | Count | Key Findings |
|----------|-------|--------------|
| Patterns | {N} | {top finding} |
| Drifts | {N} | {top finding} |
| Knowledge | {N} | {top finding} |

### 💡 CORTEX Enhancements Identified
- ENH-XXX: {description} → {target file/registry path}

### 📦 Knowledge Persisted
- {domain}/{artifact}.yaml — {description}

### 🎯 Next Steps
- {actionable next step}
```

---

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `cortex_capture_metrics` | Record TDD cycles, debug sessions from chat |
| `cortex_query_governance` | Cross-check violations found in session |
| `cortex_verify_claim` | Verify architectural claims extracted |
| `cortex_bulk_digest_files` | Bulk file traversal and processing |
| `cortex_validate_compliance` | Validate extracted patterns against CORE rules |

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

Score the source content. If score ≥ 5 → auto-activate Pipeline 1. Score 3–4 → ask user. < 3 → Pipeline 2 or 3.

| Marker | Points |
|---|---|
| AC code (`AC-*`) | +2 |
| Phase reference | +1 |
| Test count (`X/Y` format) | +1 |
| Progress bar (`[████░░]`) | +1 |
| CORTEX badge (🤖🧠) | +1 |
| Timestamp | +1 |
| Git hash | +1 |
| User/Assistant turns | +2 |
| Tool call markers | +1 |

---

## ⛔ Deleted Constructs — Never Reference

- `cortex/brain/` — dissolved into `cortex/orchestrators/`, `cortex/intelligence/`, `cortex/governance/`
- `cortex_intelligence/` — merged into `cortex/intelligence/`
- `cortex_lens/` — merged into `cortex/lens/`
- `cortex_digest_session` — removed MCP tool (use `cortex_bulk_digest_files`)
- Phase 49 / CCL / CrystallizedContext — removed constructs
- `_archive/` — deleted directory

---

## Canonical Reference

- Package: `cortex` (single canonical import)
- BulkDigestOrchestrator: `cortex/orchestrators/support/bulk_digest_orchestrator.py`
- DigestSessionOrchestrator: `cortex/orchestrators/support/digest_session_orchestrator.py`
- Intelligence Engine: `cortex/intelligence/learning/digest/`
- MCP: 25 tools in `cortex/mcp/tools/`
