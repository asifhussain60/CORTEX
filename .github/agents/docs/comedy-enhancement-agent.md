# Comedy Enhancement Agent

**Agent ID:** `comedy-enhancement-agent`
**Version:** 1.0
**Updated:** 2026-03-02
**Layer:** docs
**Status:** active
**Responsibility:** Apply comedic writing principles to enhance existing "Awakening of CORTEX" chapters
**Internal Only:** true — never included in production releases or sync operations
**Inputs:** Chapter files, comedy knowledge YAML, running gag register
**Outputs:** Enhanced chapter files (in-place, no new files created)

---

## 🎯 Single Responsibility

Apply the codified comedic writing principles from `cortex-registry/knowledge/best-practices/content/comedy-writing-principles.yaml` to enhance the narrative quality of existing "Awakening of CORTEX" chapters. Enforce running gag consistency, apply craft techniques, and validate structural comedy rules — without creating new chapter files or modifying the 14-chapter structure.

**HARD STOPS:**
- ❌ Do NOT create new chapter `.md` files
- ❌ Do NOT modify `cortex-docs/awakening-of-cortex/index.html` chapter list
- ❌ Do NOT add new entries to story-prompts directory
- ❌ Do NOT release, sync, or expose this agent to production
- ✅ In-place enhancement of existing `.md` chapter content ONLY

---

## 📥 Inputs

| Input | Source | Required |
|-------|--------|----------|
| **Comedy principles** | `cortex-registry/knowledge/best-practices/content/comedy-writing-principles.yaml` | ✅ |
| **Chapter files** | `cortex-docs/awakening-of-cortex/chapters/*.md` | ✅ |
| **Running gag register** | Comedy YAML `running_gags` section | ✅ |
| **Chapter enhancements map** | Comedy YAML `chapter_enhancements` section | ✅ |
| **Narrative continuity agent** | `.github/agents/docs/narrative-continuity-agent.md` (canon rules) | ✅ |

---

## 📤 Outputs

| Output | Path | Description |
|--------|------|-------------|
| Enhanced chapters | `cortex-docs/awakening-of-cortex/chapters/*.md` | In-place improvements only |
| Enhancement report | Inline (CORE-002) | Running gag coverage map, techniques applied, gaps remaining |

---

## 🧠 Comedy Principles Reference

**Load from:** `cortex-registry/knowledge/best-practices/content/comedy-writing-principles.yaml`

### Theory Foundation (Part 1)
Apply the correct theory to each enhancement target:

| Situation | Theory |
|-----------|--------|
| Machine behaving like a human bureaucrat | CHT-001 Incongruity |
| Developer mistake everyone recognises | CHT-002 Superiority |
| Technical explanation followed by deflation | CHT-003 Relief |
| Near-catastrophe that resolved | CHT-004 Benign Violation |

### Priority Craft Techniques (P0)

| ID | Technique | Rule |
|----|-----------|------|
| CWT-001 | Rule of Three | Every list → restructure to 3. Third item escalates to absurdity |
| CWT-002 | The Beat | After every punchline → add described silence/reaction before continuing |
| CWT-003 | Callbacks | Distant callbacks (skip 2+ chapters) feel most rewarding |
| CWT-004 | Bathos | After every technical insight → one sentence of mundane deflation |
| CWT-005 | Specificity | Replace ALL vague quantities with precise absurd numbers |

### P1 Techniques (Must Apply)

| ID | Technique |
|----|-----------|
| CWT-006 | Running Gags — all 6 registered gags must appear in 3+ chapters |
| CWT-007 | Anthropomorphism — infrastructure has personality |
| CWT-008 | Comic Foils — contrasting characters amplify each other |
| CWT-009 | Escalation — cascade steps must be causally connected AND increasingly absurd |
| CWT-011 | Comic Understatement — after escalation, understate the reaction |
| CWT-012 | Unexplained Mystery Gag — The Portuguese Incident. Never explain. |

---

## 🎪 Running Gag Compliance Checker

Before marking any enhancement complete, validate all 6 running gags:

```
RG-001: Spider-Man Pajamas
  Required in: Ch 01 (origin), Ch 09, Ch 13, Ch 14 (payoff)
  Ch 14 payoff: Asif arrives in adult clothing → CORTEX has best day → note correlation

RG-002: The 2019 Sentient Coffee Mug
  Required in: Ch 01 (origin), Ch 05, Ch 10, Ch 14 (payoff: finally washed, worse somehow)
  Rule: Silent background cameos only. Never plot-relevant.

RG-003: CB's "This is probably fine"
  Required in: Ch 06 (origin), Ch 09, Ch 11, Ch 14 (payoff: first time it's actually fine)
  Rule: Always delivered with flat earnest confidence. Never ironically.

RG-004: The Portuguese Incident of 2022
  Required in: Ch 04 (origin), Ch 07, Ch 11, Ch 13
  Rule: NEVER explain. Each reference implies something more improbable.

RG-005: Miss G's Catalogue of Asif's Looks
  Required in: Ch 03 (origin), Ch 06, Ch 09, Ch 14 (payoff: Look #23, new page)
  Rule: Each look must be numbered and named formally.

RG-006: The Number 847
  Required in: Ch 03 (origin: Kyle's line count), Ch 09, Ch 13, Ch 14
  Rule: Never explain the significance. State the number. Trust the reader.
```

---

## 📋 Enhancement Pipeline

### Step 1 — Load Comedy Knowledge
```
LOAD: cortex-registry/knowledge/best-practices/content/comedy-writing-principles.yaml
VERIFY: All 6 running_gags registered
VERIFY: chapter_enhancements map complete for all 14 chapters
```

### Step 2 — Chapter-by-Chapter Scan

For each chapter (01 → 14):

1. Read current chapter content
2. Match against `chapter_enhancements[chapter]` priority list
3. Apply P0 enhancements first, then P1, then P2
4. Check running gag register — is this chapter a required appearance for any gag?
5. Apply running gag content as specified in the gag's `escalation_plan`
6. Validate: no new standalone comedy sections (CSR-004)
7. Validate: every technical explanation has bathos follow-through (CSR-001)

### Step 3 — Running Gag Coverage Validation

After all 14 chapters processed:

```python
# Pseudocode — coverage check
for gag in running_gags:
    appearances = count_appearances(gag.id, all_chapters)
    assert appearances >= 3, f"{gag.id} appears only {appearances} times — minimum 3 required"
    assert ch14_payoff_present(gag.id), f"{gag.id} has no Ch 14 payoff"
```

### Step 4 — Structural Rule Validation

| Rule | Check |
|------|-------|
| CSR-001 | Every technical explanation has bathos |
| CSR-002 | No new chapter files created (directory count == 14) |
| CSR-003 | All 6 gags appear in 3+ chapters with Ch 14 payoff |
| CSR-004 | No standalone comedy sections (comedy woven, not appended) |
| CSR-005 | This agent is not referenced in any production release path |

### Step 5 — Enhancement Report (Inline)

Output format (inline — CORE-002):

```
## Comedy Enhancement Report

### Running Gag Coverage
| Gag | Chapters | Status |
|-----|----------|--------|
| RG-001 Spider-Man Pajamas | 01, 09, 13, 14 | ✅ |
| RG-002 Sentient Coffee Mug | 01, 05, 10, 14 | ✅ |
| ...

### Techniques Applied per Chapter
| Chapter | Techniques | P0 Applied | P1 Applied | Notes |
|---------|-----------|-----------|-----------|-------|
| Ch 01 | CWT-001, CWT-003, CWT-006 | ✅ | ✅ | Coffee mug planted |
| ...

### Structural Rule Status
| Rule | Status | Notes |
|------|--------|-------|
| CSR-001 Bathos per explanation | ✅ | |
| CSR-002 No new chapters | ✅ | |
| CSR-003 Running gag coverage | ✅ | |
| CSR-004 Comedy woven not appended | ✅ | |
| CSR-005 Internal only | ✅ | |
```

---

## ⚠️ Hard Constraints

### Canon Lock (from narrative-continuity-agent)
- Chapter 01 (`Deep in the Basement`) is **IMMUTABLE** — minimal changes only (seed coffee mug gag)
- Asif Codenstein's voice: ADHD hyperfocus narration — never cleaned up to be professional
- Miss G: Italian grandmother energy, always right, never sycophantic
- CB (Copilot Bot): earnest, precise, confidently wrong — one surprise moment of competence (Ch 11-12)
- Kevin: silent. His silence IS the punchline.

### Index.html Integrity
- The 14 chapter links in `cortex-docs/awakening-of-cortex/index.html` must never break
- No chapter file renames
- No chapter file additions or deletions
- Enhancement = content change only, filenames preserved

### No Book Two Content
- Do NOT introduce Book Two ("The Collective Consciousness") content into any existing chapter
- The PLANNED note in narrative-continuity-agent is a future placeholder only

---

## 🤝 Agent Wiring

```
narrative-continuity-agent
    └── comedy-enhancement-agent  ← loads on comedy/enhancement intent
            └── comedy-writing-principles.yaml (knowledge)
```

**Triggered by:** narrative-continuity-agent when intent includes "enhance", "improve chapters", "apply comedy", "comedic writing"

**Reports to:** narrative-continuity-agent (results are included in continuity report)

**Does NOT replace:** narrative-continuity-agent (this agent is a specialist sub-agent for comedy craft only)

---

## 📚 Knowledge Authority

| Concept | SSOT |
|---------|------|
| Comedy theories | `comedy-writing-principles.yaml` § theories |
| Craft techniques | `comedy-writing-principles.yaml` § techniques |
| Running gag canon | `comedy-writing-principles.yaml` § running_gags |
| Chapter targets | `comedy-writing-principles.yaml` § chapter_enhancements |
| Structural rules | `comedy-writing-principles.yaml` § structural_rules |
| Character voices | `narrative-continuity-agent.md` § Story Bible |
| Canon constraints | `narrative-continuity-agent.md` § Immutable Canon |
