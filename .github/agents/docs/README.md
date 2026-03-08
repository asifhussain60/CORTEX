# CORTEX Documentation Agents

**Updated:** 2026-03-08 | **Prompt:** `.github/prompts/cortex-doc.prompt.md`  
**Status:** ✅ Production Ready | **Agents:** 15  
**Durable State:** `cortex-registry/config/doc-orchestrator-state.yaml`

---

## Agent Registry

| # | Agent | File | Responsibility | I/O |
|---|-------|------|----------------|-----|
| 1 | **Git Discovery** | `git-discovery-agent.md` | Inspect Git history, classify changes | IN: Git repo, timestamp → OUT: Change manifest |
| 2 | **GitHub Issue Harvester** | `github-issue-harvester-agent.md` | Ingest GitHub issues (#14+), extract capabilities | IN: Durable state, GitHub pages → OUT: Issue manifest |
| 3 | **Drift Detection** | `drift-detection-agent.md` | Cross-reference implementation vs documentation | IN: Change manifest, issue manifest, file system → OUT: Drift report |
| 4 | **Doc Sync** | `doc-sync-agent.md` | Update `.content/`, glossary, media prompts | IN: Change manifest, drift report → OUT: Updated files |
| 5 | **Diagram Regeneration** | `diagram-regeneration-agent.md` | Regenerate D3.js SVG diagrams | IN: Architectural shifts, stale diagrams → OUT: Updated D3.js SVG diagrams |
| 6 | **Media Prompt** | `media-prompt-agent.md` | Maintain DALL-E image + video prompts | IN: Drift report, capabilities → OUT: Updated prompts |
| 7 | **Narrative Continuity** | `narrative-continuity-agent.md` | Guard Awakening of CORTEX story arc | IN: Narrative drift, new capabilities → OUT: Enhanced chapters |
| 8 | **Coverage Audit** | `coverage-audit-agent.md` | Validate completeness, produce certification | IN: All upstream reports → OUT: Certification verdict |
| 9 | **Release Notes** | `release-notes-agent.md` | Generate changelogs from Git diffs | IN: Change manifest, phase records → OUT: Structured changelogs |
| 10 | **HTML View Designer** | `html-view-designer.md` | Design + Implement mode — IA, layout, semantic HTML | IN: Target HTML, knowledge YAMLs → OUT: Design proposal + implementation |
| 11 | **Design System Enforcer** | `design-system-enforcer.md` | Token validation, CSS layer assignment, theme integrity | IN: Proposed CSS → OUT: Validation report (P0 block on violation) |
| 12 | **A11y + Perf Guardian** | `a11y-perf-guardian.md` | WCAG 2.1/2.2 AA gate + performance regression detection | IN: Proposed HTML/CSS → OUT: A11y/perf report |
| 13 | **Regression Sentinel** | `regression-sentinel.md` | Diff guard — no theme drift, no broken links, no ARIA regressions | IN: Before/after diffs → OUT: Regression report |
| 14 | **Knowledge Harvester** | `knowledge-harvester-agent.md` | Source → distilled notes → knowledge YAMLs | IN: Source URLs or session history → OUT: Updated YAMLs |
| 15 | **Comedy Enhancement** | `comedy-enhancement-agent.md` | Apply comedic writing principles to story chapters (internal only) | IN: Chapter files, comedy YAML → OUT: Enhanced chapters |

---

## Pipeline Flow

```
Discovery → Issue Harvest → Drift Detection → Sync → Narrative Update → Certification
    │              │              │              │            │               │
    ▼              ▼              ▼              ▼            ▼               ▼
 git-discovery  github-issue  drift-detection  doc-sync  narrative    coverage-audit
                 harvester                        │
                                            ┌─────┼─────┐
                                            ▼     ▼     ▼
                                        diagram  media  release-notes
```

**Design + Implement sub-pipeline** (triggered by `/doc-design {file}`):
```
html-view-designer → design-system-enforcer → a11y-perf-guardian → regression-sentinel
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
