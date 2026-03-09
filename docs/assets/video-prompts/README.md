# CORTEX Video Prompts — NotebookLM Cinematic Video System
**Updated:** 2026-03-09 | **Architecture:** Decoupled — content, diagrams, and prompts update independently  
**Format:** NotebookLM Cinematic Video Overview (Gemini + Veo 3)

---

## 🏗️ Architecture: Decoupled Reference System

```
docs/assets/video-prompts/
│
├── sources/                    ← Upload ONE file to NotebookLM per video
│   ├── 01-src-all-roles-overview.md
│   ├── 02-src-business-leaders.md
│   ├── 03-src-product-owners.md
│   ├── 04-src-software-engineers.md
│   ├── 05-src-quality-engineers.md
│   ├── 06-src-security-engineers.md
│   └── 07-src-sre.md
│
├── steering-prompts/           ← Paste ONE prompt into NotebookLM → Customize
│   ├── 01-steer-all-roles-overview.md
│   ├── 02-steer-business-leaders.md
│   ├── 03-steer-product-owners.md
│   ├── 04-steer-software-engineers.md
│   ├── 05-steer-quality-engineers.md
│   ├── 06-steer-security-engineers.md
│   └── 07-steer-sre.md
│
├── videos/                     ← Tutorial video prompts (separate series)
│   └── tutorials/
│
├── index.md                    ← Quick reference (file map per video)
└── README.md                   ← This file
```

**Naming convention:**
- Source files: `NN-src-{descriptor}.md` — the document uploaded to NotebookLM as content
- Steering files: `NN-steer-{descriptor}.md` — the instruction prompt pasted into the focus field

### Independent Update Contract

| Asset | Location | Update Independently | Effect on Other Layers |
|---|---|---|---|
| **Architecture diagrams** | `docs/assets/diagrams/*.md` | ✅ Yes | Zero — sources reference by filename |
| **Best practices YAML** | `cortex-registry/knowledge/best-practices/content/` | ✅ Yes | Zero — steering prompts cite rule IDs |
| **Source documents** | `sources/NN-src-*.md` | ✅ Yes | Zero — steering prompts name file only |
| **Steering prompts** | `steering-prompts/NN-steer-*.md` | ✅ Yes | Zero — sources are standalone |

**Contract:** Diagram files update in place → source documents auto-reflect changes. Steering prompts reference source files by name only. No cascading edits required across layers.

---

## 🎬 Video Series Map

| Video | Title | Source File | Steering File | Narrator | Domain Colour |
|---|---|---|---|---|---|
| 01 | What Is CORTEX? (All Roles) | `01-src-all-roles-overview.md` | `01-steer-all-roles-overview.md` | 🎙️ Female | Cyan `#00d4ff` |
| 02 | CORTEX for Business Leaders | `02-src-business-leaders.md` | `02-steer-business-leaders.md` | 🎙️ Male | Purple `#7b61ff` |
| 03 | CORTEX for Product Owners | `03-src-product-owners.md` | `03-steer-product-owners.md` | 🎙️ Female | Emerald `#00c471` |
| 04 | CORTEX for Software Engineers | `04-src-software-engineers.md` | `04-steer-software-engineers.md` | 🎙️ Male | Cyan + Gold |
| 05 | CORTEX for Quality Engineers | `05-src-quality-engineers.md` | `05-steer-quality-engineers.md` | 🎙️ Female | Gold `#FFD700` |
| 06 | CORTEX for Security Engineers | `06-src-security-engineers.md` | `06-steer-security-engineers.md` | 🎙️ Female | Red `#ff4757` |
| 07 | CORTEX for SREs | `07-src-sre.md` | `07-steer-sre.md` | 🎙️ Male | Amber `#f39c12` |

---

## 🚀 Step-by-Step: Generating a Video

1. Go to [notebooklm.google.com](https://notebooklm.google.com)
2. Create a **new notebook**
3. Upload the matching `sources/NN-src-*.md` file as the **sole source**
4. In the Studio panel → **Video Overview** → **Customize**:
   - **Format:** `Cinematic` ← NOT Explainer or Brief
   - **Visual Style:** `Custom` ← paste visual style block from the matching `steering-prompts/NN-steer-*.md`
   - **"What should the AI hosts focus on?"** ← paste steering prompt block from same file
5. Click **Generate** — allow 20–30 minutes for Cinematic quality
6. If output misses concepts → use the **Fallback** prompt in the same steering file

> ⚠️ **Critical mis-configurations seen in production:**
> - Format left as **Explainer** → structured slides, no Veo 3 cinematic motion
> - Visual Style left as **Auto-select** → CORTEX glassmorphism palette never applied
> - Focus field left **empty** → AI receives zero narrative guidance

---

## 📐 Diagram Reference Index

Source documents reference diagrams from `docs/assets/diagrams/` **by filename only**. Update the diagram file in place — no edits needed anywhere else.

| Filename | Title | Videos |
|---|---|---|
| `01-diagram-architecture-system-architecture-layers.md` | System architecture — layer view | V01, V02 |
| `02-diagram-architecture-mcp-gateway-architecture.md` | MCP gateway architecture | V01, V04 |
| `03-diagram-workflow-sdlc-pipeline.md` | SDLC workflow pipeline (7 phases) | V02, V03 |
| `04-diagram-audit-audit-fix-pipeline.md` | /audit fix pipeline (9 stages) | V02 |
| `05-diagram-workflow-tdd-cycle-and-fsm.md` | TDD cycle and workflow engine FSM | V04, V05 |
| `06-diagram-governance-sweep-completeness-core-064.md` | Sweep completeness (CORE-064) | V03, V05 |
| `07-diagram-testing-testing-strategy-pyramid.md` | Testing strategy pyramid | V04, V05 |
| `09-diagram-orchestration-request-sequence.md` | End-to-end request sequence | V01 |
| `11-diagram-intelligence-lens-analysis-pipeline.md` | LENS intelligence pipeline + Diamond | V01, V04 |
| `12-diagram-governance-convergence-gate-core-068.md` | Universal convergence gate (CORE-068) | V03, V05 |
| `13-diagram-orchestration-intent-classification-routing.md` | Intent classification and routing | V01 |
| `14-diagram-debugging-multi-stack-pipeline.md` | Multi-stack debug pipeline (8 strategies) | V04 |
| `15-diagram-governance-rule-enforcement-tiers.md` | Governance rule enforcement (4-tier) | V02, V06 |
| `17-diagram-security-threat-model-stride-analysis.md` | Threat Model Engine — STRIDE pipeline | V06 |
| `18-diagram-quality-analysis-engine-scoring-dashboard.md` | Quality Analysis Engine — scoring | V05 |
| `19-diagram-orchestration-po-change-intelligence-pipeline.md` | PO Change Intelligence Pipeline | V03 |
| `20-diagram-intelligence-document-ingest-pipeline.md` | Document Ingest Pipeline (5 components) | V01, V02 |
| `21-diagram-governance-vacuum-source-protection.md` | Vacuum Source Protection | V07 |

---

## 🎨 Domain Colour Reference

| Video | Primary | Secondary | Background |
|---|---|---|---|
| 01 | Cyan `#00d4ff` | Purple `#7b61ff` | Navy `#0a0e27` |
| 02 | Purple `#7b61ff` | Emerald `#10b981` | Navy `#0a0e27` |
| 03 | Emerald `#00c471` | Purple `#7b61ff` | Navy `#0a0e27` |
| 04 | Cyan `#00d4ff` | Gold `#FFD700` | Navy `#0a0e27` |
| 05 | Gold `#FFD700` | Cyan `#00d4ff` | Navy `#0a0e27` |
| 06 | Red `#ff4757` | Amber `#f39c12` | Navy `#0a0e27` |
| 07 | Amber `#f39c12` | Cyan `#00d4ff` | Navy `#0a0e27` |

---

## 📋 VBP Compliance Layer Map

Rules from `cortex-registry/knowledge/best-practices/content/video-design-best-practices.yaml` are enforced at the layer where they have most leverage. Updating either layer in isolation preserves compliance.

| VBP Rule | Enforced In | Mechanism |
|---|---|---|
| VBP-001 One idea per frame | `sources/` | Each `##` section = one concept |
| VBP-002 Hook in 8s | `steering-prompts/` | Opening line always states the pain |
| VBP-003 Narration ≠ slide | `sources/` | Prose paragraphs, no bullet-only sections |
| VBP-006 Contrast storytelling | `sources/` | Problem section always precedes solution |
| VBP-010 Analogies (≤1 per 2 min) | `sources/` | `## Quotes Worth Using` — max 3 per video |
| VBP-011 Strategic silence | `steering-prompts/` | Specified after emotional peak |
| VBP-012 Consistent visuals | `steering-prompts/` | Custom visual style block enforces palette |
| VBP-015 Breadcrumb navigation | `steering-prompts/` | Three-pillar bar specified in prompt |
| VBP-016 Bold key words | `steering-prompts/` | Accent colour bolding called out in prompt |
| VBP-017 Narrator gender | `steering-prompts/` | F: V01, V03, V05, V06 · M: V02, V04, V07 |
| VBP-018 No unexpanded acronyms | `sources/` | First-use expansion in `## Key Facts` |
| VBP-019 Colour intelligence | Both layers | Custom style + domain colour header |
