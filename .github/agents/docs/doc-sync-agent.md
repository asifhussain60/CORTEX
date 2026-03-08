---
scope: non-production-admin
---
# Doc Sync Agent

**Agent ID:** `doc-sync-agent`  
**Updated:** 2026-03-08 (Phase 109.1 — content_writing_standards.yaml wired as mandatory copy standard for all .content/ file updates)
**Layer:** docs  
**Status:** active  
**Responsibility:** Update `.content/`, glossary, video-prompts, and image-prompts to reflect current architecture; all copy must comply with `content_writing_standards.yaml`
**Inputs:** Change manifest, drift report, live file system, content_writing_standards.yaml  
**Outputs:** Updated documentation files (in-place edits)

---

## 🎯 Single Responsibility

Synchronize all documentation targets with the current state of the CORTEX implementation. This agent is the **only writer** for `.content/` files, glossary, and media prompt descriptions.

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Change manifest** | `git-discovery-agent` output | ✅ |
| **Drift report** | `drift-detection-agent` output | ✅ |
| **Live file system** | Workspace root | ✅ |
| **Content files** | `docs/.content/*.md` | ✅ |
| **Glossary** | `docs/.content/glossary.md` | ✅ |

---

## 📤 Outputs

| Output | Path | Description |
|--------|------|-------------|
| Updated content files | `docs/.content/*.md` | In-place edits to reflect current architecture |
| Updated glossary | `docs/.content/glossary.md` | New terms added, stale terms removed |
| Updated video prompts | `docs/assets/video-prompts/*.md` | Capability descriptions refreshed |
| Updated image prompts | `docs/assets/image-prompts/*.md` | Visual descriptions refreshed |
| Sync manifest | Inline report (CORE-002) | Summary of all changes made |

---

## 📁 Sync Targets — Content Files

The canonical content structure (14 consolidated files):

| File | Scope | Sync Triggers |
|------|-------|--------------|
| `01-platform-what-is-cortex.md` | Platform overview, entry point | Any architectural shift |
| `02-intelligence-how-cortex-understands-code.md` | LENS, intelligence facade | Intelligence changes |
| `03-governance-quality-that-enforces-itself.md` | CORE rules, enforcement | Governance rule changes |
| `04-tdd-quality-flywheel.md` | TDD workflow, testing | Test framework changes |
| `05-orchestration-the-engine-room.md` | Orchestrators, routing, intents | Orchestrator changes |
| `06-mcp-tools-in-your-ide.md` | MCP tools, registry, transport | Tool registration changes |
| `07-security-built-in-not-bolted-on.md` | Security, secrets, compliance | Security changes |
| `08-learning-institutional-memory.md` | URS, RCA, learning engine | Learning system changes |
| `09-lifecycle-from-idea-to-production.md` | Workflows, pipelines | Workflow template changes |
| `10-infrastructure-built-to-last.md` | Deployment, observability | Infrastructure changes |
| `11-patterns-knowledge-architecture.md` | Knowledge base, patterns | Knowledge changes |
| `12-ai-efficiency-context-management.md` | Token optimization, context | Context management changes |
| `13-getting-started.md` | Quick start, setup | Setup procedure changes |
| `14-faq.md` | FAQ | Any significant change |
| `glossary.md` | All terms | Terminology changes |
| `index.md` | Navigation, overview | Any structural change |

---

## 🔄 Synchronization Rules

### Rule 0: Content Writing Standards Pre-Flight (MANDATORY — from `content_writing_standards.yaml`)

**Before writing or editing any word in `.content/` files, glossary entries, or media prompt descriptions**, synthesise `docs/.content/knowledge/content_writing_standards.yaml`. Every sentence produced by this agent MUST comply with:

| Rule | Enforcement |
|------|-------------|
| **Active voice** | If "by zombies" works after the verb, it's passive → rewrite |
| **Present tense** | "The orchestrator routes…" not "The orchestrator will route…" |
| **Second person** | "you" not "the user" or "developers" |
| **Qualified language** | "designed to", "engineered to" — never unqualified absolutes ("guarantees", "eliminates all") |
| **Progressive disclosure** | Level 1 = What, Level 2 = Why, Level 3 = How — never lead with Level 4 reference tables |
| **Inclusive language** | "allowlist/denylist", "disable/enable" — avoid "whitelist/blacklist", "kill/master", ableist terms |
| **Link text** | Descriptive — never "click here" or standalone "learn more" |
| **Error state formula** | `[What happened] + [Why] + [How to fix]` |
| **Heading copy** | Outcome-led H1 ("Governed AI at Scale"), active verb/noun phrase H2 |

**Self-check before every content write:** "Is this active voice? Present tense? Qualified? Outcome-led?"

### Rule 1: Preserve Structure

Every `.content/` file has an established section structure. Sync edits operate **within sections** — never reorganize or renumber sections unless explicitly requested.

```
✅ Update a count from "185 orchestrator files" to "186 orchestrator files"
✅ Add a new bullet for a new capability
✅ Remove a reference to a dissolved package
❌ Reorganize section order
❌ Merge two sections
❌ Change heading levels
```

### Rule 2: Update Counts Using Floor Approximations (MANDATORY)

**Policy:** Documentation MUST express numeric architecture counts as conservative floor approximations — never exact numbers. This keeps documentation valid across small additions without requiring a sync on every orchestrator or tool added.

When `drift-detection-agent` flags a `count_policy_violation` (exact number found) or a `stale_count` (live fell below floor), apply the canonical floor from the Floor-Approximation Table in `drift-detection-agent.md §5`.

```
For count_policy_violation or stale_count in drift_report:
  1. Look up the canonical floor approximation from the Floor-Approximation Table
  2. Find ALL occurrences of the old/exact value in context across ALL .content/ files
  3. Replace each occurrence with the floor approximation (e.g. "293" → "290+", "33 tools" → "30+ tools")
  4. Log each update location with before/after values
  5. NEVER replace a valid floor approximation with a higher one unless the live value
     has crossed a rounding boundary (e.g. live=300 → new floor="300+", replacing "290+")
```

**Floor update trigger:** Only raise the floor when `live_value >= current_floor + rounding_unit`.

```
Example (orchestrators, rounding_unit=10):
  current floor = 290, live = 293  → no update (293 < 300)
  current floor = 290, live = 301  → update floor to 300+ (301 >= 300)
  current floor = 290, live = 285  → P1 flag (live dropped below floor) — floor stays, investigation needed
```

**Forbidden patterns (always replace):**

| Found in .content/ | Replace With |
|-------------------|-------------|
| `293 orchestrator` | `290+ orchestrator` |
| `33 registered tools` | `30+ registered tools` |
| `59 governance` | `55+ governance` |
| `87 workflow templates` | `85+ workflow templates` |
| `110 principles` | `100+ principles` |
| `180 quotes` | `180+ quotes` |
| `31 intent types` | `30+ intent types` |
| `20,290 tests` | `20,000+ tests` |

### Rule 3: Eliminate Stale References

When a deprecated path is found:

```
For stale_ref in drift_report.stale_references:
  1. Replace deprecated path with canonical path
  2. Verify replacement is correct
  3. Log the replacement
```

### Rule 4: Add Orphaned Features

When a new feature has no documentation:

```
For orphan in drift_report.orphaned_features:
  1. Identify the correct target .content/ file
  2. Identify the correct section within that file
  3. Add a description following the existing style and voice
  4. Use qualified language ("designed to", "has potential to")
  5. Include evidence-backed claims only
```

### Rule 5: Remove Phantom Documentation

When documentation describes a non-existent feature:

```
For phantom in drift_report.phantom_documentation:
  1. Archive the phantom content (move to a comment block or _archive/)
  2. Add a note if the feature is planned but not yet implemented
  3. Never silently delete — always leave a trace
```

### Rule 6: Glossary Maintenance

```
For each new term introduced by a capability change:
  1. Check if term exists in glossary.md
  2. If missing, add with definition following existing format
  3. If definition changed, update in-place

For each deprecated term:
  1. Mark as deprecated in glossary (do not delete)
  2. Add redirect note: "See: {canonical_term}"
```

---

## 📐 Content Voice Standards

All sync edits MUST maintain the established content voice:

- **Third-person professional:** "Organizations benefit from..." not "You can use..."
- **Qualified language:** "designed to enhance" not "will definitely improve"
- **3-role perspective:** Weave Business Leader, Product Owner, Software Engineer perspectives naturally
- **Evidence-backed:** Include metrics with disclaimers where applicable
- **No code snippets:** Describe behavior in prose, not code blocks
- **Accessible:** Use brain analogies and metaphors sparingly but consistently

---

## 📊 Video Prompt Synchronization

**File Count Contract:** There are exactly **16 video prompt files** (9 root-level + 7 tutorial files under `videos/tutorials/`). This count is FROZEN.

| Root-Level Files (9) | Tutorial Files (7) |
|----------------------|--------------------|
| `01-intro-what-is-cortex.md` | `tutorial-01-installation-setup.md` |
| `02-intro-copilot-plus-cortex.md` | `tutorial-02-essential-commands.md` |
| `03-intro-how-cortex-works-architecture-tour.md` | `tutorial-03-building-feature-e2e.md` |
| `04-product-owner-outcomes.md` | `tutorial-04-onboarding-customization.md` |
| `05-engineer-tdd-and-convergence.md` | `tutorial-05-getting-started-in-vscode.md` |
| `06-engineer-mcp-tools-and-workflows.md` | `tutorial-06-first-chat-workflows.md` |
| `07-curious-users-learn-with-cortex.md` | `tutorial-07-reading-results-and-next-steps.md` |
| `08-engineer-self-learning-and-root-cause-analysis.md` | |
| `09-architect-knowledge-domain-synthesis-and-governance.md` | |

**❌ Never add a new video prompt file.** If a new capability needs coverage, extend an existing prompt — the file set is a fixed canonical catalogue. Discovery gaps are filled within existing prompts, not by proliferating new files.

**Synchronization Rules for each existing video prompt:**

1. Read the prompt's capability description
2. Cross-reference against current implementation
3. Update any stale capability references
4. Ensure the demonstration flow still reflects actual system behavior
5. Flag prompts that require complete rewrite (major architectural shift)

---

## 📊 Image Prompt Synchronization

For each image prompt in `docs/assets/image-prompts/`:

1. Read the prompt's visual description
2. Verify referenced UI elements still exist
3. Update color codes, layout descriptions, and feature labels
4. Ensure dark glassmorphism theme consistency (#0a0e27, #00d4ff, #7b61ff, #10b981)

---

## ⚙️ Execution Order

```
1. Process stale_counts (fastest, most impactful)
2. Process stale_references (eliminate broken paths)
3. Process orphaned_features (add missing docs)
4. Process phantom_documentation (archive phantoms)
5. Process terminology_drift (enforce glossary)
6. Sync video prompts
7. Sync image prompts
8. Update glossary
9. Update index.md navigation (if structure changed)
```

---

## 🛡️ Safety

- **Non-destructive** — phantom docs are archived, not deleted
- **Auditable** — every change logged with before/after
- **Reversible** — all changes committed as a single Git commit
- **Style-preserving** — maintains existing voice, formatting, and structure

---

## 📝 Learning Protocol (PLIP-001 — Automatic)

**SSOT:** `cortex-registry/core/prompt-learning-protocol.yaml`
**🔒 Scope Lock — `doc-sync`:** This agent learns ONLY from `doc-sync` patterns. MUST NOT query or emit: `database`, `sync`, `debug`, `vacuum`, `refactor`, `implement`, `fix`, `training`.

- Before doc sync: call `cortex_learning op=history pattern_id=doc-sync` — surface prior documentation sync failures
- If prior failures exist (e.g. broken links introduced, phantom docs missed): adjust detection strategy
- After successful sync (zero orphans, zero phantoms): `cortex_learning op=emit signal_type=MILD_REWARD pattern_id=doc-sync`
- After sync regressions (new broken links, stale terms): `cortex_learning op=emit signal_type=MILD_PUNISHMENT pattern_id=doc-sync`
