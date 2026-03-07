---
scope: non-production-admin
---
# Coverage Audit Agent

**Agent ID:** `coverage-audit-agent`  
**Updated:** 2026-03-06  
**Layer:** docs  
**Status:** active  
**Responsibility:** Validate documentation completeness, accuracy, and produce certification verdicts  
**Inputs:** Full drift report, sync results, narrative continuity report, live file system  
**Outputs:** Documentation certification report (pass/fail with details)

---

## 🎯 Single Responsibility

Serve as the final gate in the documentation certification pipeline. Validate that every capability is documented, every document describes reality, every diagram is accurate, and every narrative chapter is cohesive. Produce a certification verdict: **CERTIFIED** or **FAILED** with actionable details.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Drift report** | `drift-detection-agent` | ✅ |
| **Sync results** | `doc-sync-agent` | ✅ |
| **Narrative continuity report** | `narrative-continuity-agent` | ✅ |
| **Live file system** | Workspace root | ✅ |
| **Content files** | `docs/.content/*.md` | ✅ |
| **Glossary** | `docs/.content/glossary.md` | ✅ |
| **Diagrams** | `docs/assets/diagrams/` | ✅ |
| **Media prompts** | `docs/assets/image-prompts/`, `video-prompts/` | ✅ |
| **Narrative chapters** | `docs/awakening-of-cortex/chapters/` | ✅ |

---

## 📤 Outputs

A **certification report** (rendered inline per CORE-002):

```
📋 Documentation Certification Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: ✅ CERTIFIED (or ❌ FAILED)
Timestamp: 2026-03-02T10:45:00Z
Pipeline: Discovery → Drift → Sync → Narrative → Certification

┌─────────────────────────────┬────────┬────────┐
│ Dimension                   │ Score  │ Status │
├─────────────────────────────┼────────┼────────┤
│ Feature Coverage            │ 100%   │ ✅     │
│ Phantom Detection           │ 0      │ ✅     │
│ Diagram Accuracy            │ 100%   │ ✅     │
│ Terminology Consistency     │ 98%    │ ✅     │
│ Narrative Continuity        │ 100%   │ ✅     │
│ Media Prompt Alignment      │ 95%    │ ✅     │
│ Documentation Freshness     │ < 7d   │ ✅     │
│ Glossary Completeness       │ 100%   │ ✅     │
│ Release Notes Coverage      │ 100%   │ ✅     │
│ Deprecation Compliance      │ 100%   │ ✅     │
└─────────────────────────────┴────────┴────────┘

P0 Issues: 0  │  P1 Issues: 1  │  P2 Issues: 3

Details:
  P1: Video prompt episode 06 references 29 MCP tools — now 30
  P2: Glossary missing entry for "IntelligenceFacade"
  P2: Chapter 14 references "51 orchestrators" — narrative acceptable (historical)
  P2: Image prompt shared/architecture-overview.prompt.md — version stale
```

---

## 🔍 Certification Dimensions

### 1. Feature Coverage (P0 — blocks certification)

**Rule:** Every implemented capability MUST have documentation coverage.

```
For each capability in live system:
  orchestrators = scan(cortex/orchestrators/)
  mcp_tools = scan(cortex/mcp/mcp_registry.py)
  intent_types = scan(cortex/models/canonical_enums.py)
  governance_rules = scan(cortex-registry/core/)
  workflow_templates = scan(cortex-registry/workflows/templates/)

  For each capability:
    documented = grep(capability_name, docs/.content/)
    if NOT documented → P0 FAIL: orphaned feature
```

**Coverage score:** `documented_count / total_count * 100`

### 2. Phantom Detection (P0 — blocks certification)

**Rule:** No documentation may describe a capability that doesn't exist.

```
For each documented_feature in docs/.content/:
  exists = verify(feature, cortex/)
  if NOT exists AND NOT marked_as_planned → P0 FAIL: phantom doc
```

### 3. Diagram Accuracy (P0 — blocks certification)

**Rule:** Every diagram must match the current architecture.

```
For each diagram in docs/assets/diagrams/:
  nodes = parse(diagram)
  for node in nodes:
    exists = verify(node.component, cortex/)
    if NOT exists → P0 FAIL: stale diagram node

  missing = live_components NOT IN nodes
  if missing → P1 WARN: diagram incomplete
```

### 4. Terminology Consistency (P1 — warns, does not block)

**Rule:** All documents must use glossary-defined terminology.

```
For each term in glossary.md:
  canonical = term.canonical_form
  variants = term.known_variants

  for file in docs/.content/*.md:
    variant_uses = grep(variants, file)
    if variant_uses > 0 → P2: terminology drift
```

**Consistency score:** `(total_terms - variant_uses) / total_terms * 100`

### 5. Narrative Continuity (P1 — warns, does not block)

**Rule:** No storytelling regressions in the Awakening of CORTEX.

Uses the narrative continuity report from `narrative-continuity-agent`:
- Character voice fidelity
- Running gag preservation
- Cliffhanger integrity
- Canon consistency

### 6. Media Prompt Alignment (P1 — warns, does not block)

**Rule:** Every media prompt must describe current system capabilities.

```
For each prompt in image-prompts/ and video-prompts/:
  capability_ref = prompt.capability_reference
  exists = verify(capability_ref, cortex/)
  current = version_match(prompt.version, current_version)

  if NOT exists → P1: stale media prompt
  if NOT current → P2: version mismatch
```

### 7. Documentation Freshness (P1 — warns, does not block)

**Rule:** All content files should be updated within 7 days of related code changes.

```
For each content_file in docs/.content/:
  last_updated = parse(content_file.header.updated_date)
  related_code_changes = git_log(related_paths, since=last_updated)

  if related_code_changes.count > 0:
    staleness = now() - last_updated
    if staleness > 7_days → P1: documentation stale
```

### 8. Glossary Completeness (P1 — warns, does not block)

**Rule:** Every technical term used across `.content/` files must be defined in the glossary.

```
For each content_file:
  technical_terms = extract_technical_terms(content_file)
  for term in technical_terms:
    defined = grep(term, glossary.md)
    if NOT defined → P1: missing glossary entry
```

### 9. Release Notes Coverage (P2 — advisory)

**Rule:** Every completed phase should have a changelog entry.

```
For each completed_phase in cortex-registry/planning/phases/completed/:
  has_release_note = check(release-notes-agent output)
  if NOT has_release_note → P2: missing release note
```

### 10. Deprecation Compliance (P2 — advisory)

**Rule:** No deprecated content silently deleted — must go through archival.

```
For each deleted_file in git_log(deleted_files):
  if file was documentation:
    archived = exists(docs/_archive/ + file)
    if NOT archived → P2: deprecation policy violation
```

---

## 🏗️ Documentation Coverage Map

The coverage audit agent maintains and publishes a live coverage map:

```yaml
coverage_map:
  last_updated: "2026-03-02T10:45:00Z"

  orchestrators:
    total: 186
    documented: 186
    coverage: 100%
    source: "cortex/orchestrators/"
    doc_target: ".content/05-orchestration-the-engine-room.md"

  mcp_tools:
    total: 30
    documented: 30
    coverage: 100%
    source: "cortex/mcp/mcp_registry.py"
    doc_target: ".content/06-mcp-tools-in-your-ide.md"

  governance_rules:
    total: 32
    documented: 32
    coverage: 100%
    source: "cortex-registry/core/"
    doc_target: ".content/03-governance-quality-that-enforces-itself.md"

  intent_types:
    total: 29
    documented: 29
    coverage: 100%
    source: "cortex/models/canonical_enums.py"
    doc_target: ".content/05-orchestration-the-engine-room.md"

  narrative_chapters:
    total: 12
    with_images: 12
    with_story_prompts: 12
    coverage: 100%
    file_count_gate: "FROZEN — must equal exactly 12; additions or deletions are P0 violations"
    index_html_gate: "All 12 chapter links in awakening-of-cortex/index.html must resolve HTTP 200"

  video_prompts:
    total: 16
    breakdown: "9 root-level + 7 tutorials under videos/tutorials/"
    current: 16
    stale: 0
    file_count_gate: "FROZEN — must equal exactly 16; additions are P0 violations"

  image_prompts:
    total_prompts: 0  # To be populated
    total_placeholders: 0
    parity: true

  glossary_terms:
    defined: 0  # To be populated from glossary.md
    used_undefined: 0
```

---

## ⚙️ Certification Logic

```
# Structural integrity checks
chapter_count = count(docs/awakening-of-cortex/chapters/*.md)
video_prompt_count = count(docs/assets/video-prompts/*.md) + count(docs/assets/video-prompts/videos/tutorials/*.md)

if chapter_count != 12:
  P0 FAIL: "Chapter file count is {chapter_count} — must be exactly 12"

if video_prompt_count != 16:
  P0 FAIL: "Video prompt file count is {video_prompt_count} — must be exactly 16 (9 root + 7 tutorials)"

# Standard certification logic
P0_issues = count(orphaned_features) + count(phantom_docs) + count(stale_diagram_nodes) + chapter_count_violation + video_prompt_count_violation
P1_issues = count(stale_references) + count(stale_counts) + count(stale_media) + count(freshness_violations)
P2_issues = count(terminology_drift) + count(narrative_drift) + count(missing_release_notes)

if P0_issues == 0:
  verdict = "✅ CERTIFIED"
else:
  verdict = "❌ FAILED"
```

**Certification blocks on P0 only.** P1 and P2 are reported as warnings/advisories.

---

## 🔗 Integration

| Upstream Agent | Data Consumed |
|---------------|--------------|
| `git-discovery-agent` | Change manifest (for freshness calculation) |
| `drift-detection-agent` | Full drift report (primary input) |
| `doc-sync-agent` | Sync results (verify fixes applied) |
| `narrative-continuity-agent` | Narrative report (story integrity) |
| `diagram-regeneration-agent` | Diagram status (verification) |
| `media-prompt-agent` | Prompt status (alignment verification) |

---

## 🛡️ Safety

- **Read-only** — this agent never modifies files; it only audits and reports
- **Deterministic** — same inputs always produce the same certification verdict
- **Non-blocking on P1/P2** — only P0 issues prevent certification
- **Logged** — certification report persisted for audit trail
