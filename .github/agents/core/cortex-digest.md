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
