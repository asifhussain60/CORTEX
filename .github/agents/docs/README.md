# CORTEX Documentation Agents

**Updated:** 2026-03-02 | **Prompt:** `.github/prompts/cortex-doc.prompt.md`  
**Status:** ✅ Production Ready | **Agents:** 8

---

## Agent Registry

| # | Agent | File | Responsibility | I/O |
|---|-------|------|----------------|-----|
| 1 | **Git Discovery** | `git-discovery-agent.md` | Inspect Git history, classify changes | IN: Git repo, timestamp → OUT: Change manifest |
| 2 | **Drift Detection** | `drift-detection-agent.md` | Cross-reference implementation vs documentation | IN: Change manifest, file system → OUT: Drift report |
| 3 | **Doc Sync** | `doc-sync-agent.md` | Update `.content/`, glossary, media prompts | IN: Change manifest, drift report → OUT: Updated files |
| 4 | **Diagram Regeneration** | `diagram-regeneration-agent.md` | Regenerate D3.js SVG diagrams | IN: Architectural shifts, stale diagrams → OUT: Updated D3.js SVG diagrams |
| 5 | **Media Prompt** | `media-prompt-agent.md` | Maintain DALL-E image + video prompts | IN: Drift report, capabilities → OUT: Updated prompts |
| 6 | **Narrative Continuity** | `narrative-continuity-agent.md` | Guard Awakening of CORTEX story arc | IN: Narrative drift, new capabilities → OUT: Enhanced chapters |
| 7 | **Coverage Audit** | `coverage-audit-agent.md` | Validate completeness, produce certification | IN: All upstream reports → OUT: Certification verdict |
| 8 | **Release Notes** | `release-notes-agent.md` | Generate changelogs from Git diffs | IN: Change manifest, phase records → OUT: Structured changelogs |

---

## Pipeline Flow

```
Discovery → Drift Detection → Sync → Narrative Update → Certification
    │              │             │            │               │
    ▼              ▼             ▼            ▼               ▼
 git-discovery  drift-detection  doc-sync  narrative    coverage-audit
                                    │
                              ┌─────┼─────┐
                              ▼     ▼     ▼
                          diagram  media  release-notes
```

---

## Design Principles

1. **Single responsibility** — each agent does exactly one thing
2. **Clear inputs and outputs** — no hidden state or side effects
3. **Deterministic** — same inputs produce same outputs (no LLM for classification)
4. **Composable** — agents chain naturally in the certification pipeline
5. **Read-write separation** — discovery/detection agents are read-only; sync agents write
6. **Archive-first** — deprecated content is archived, never deleted blindly
7. **Severity-gated** — P0 blocks certification; P1 warns; P2 is advisory

---

## Replaces

| Old File | Replaced By |
|----------|-------------|
| `core/cortex-documentation-architect.md` | `docs/doc-sync-agent.md` + `docs/drift-detection-agent.md` |
| `core/cortex-gitpages-builder.md` | `docs/diagram-regeneration-agent.md` + `docs/media-prompt-agent.md` |
| `core/cortex-storyteller.md` | `docs/narrative-continuity-agent.md` |
