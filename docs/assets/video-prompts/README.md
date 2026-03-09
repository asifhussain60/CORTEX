# CORTEX Video Prompts — NotebookLM Cinematic Video System
**Updated:** 2026-03-09 | **Architecture:** Decoupled — content, diagrams, and prompts update independently
**Format:** NotebookLM Cinematic Video Overview (Gemini + Veo 3)

---

## 🏗️ Architecture: Decoupled Reference System

```
docs/assets/video-prompts/
│
├── sources/                    ← Upload ONE file to NotebookLM per video
│   ├── 01-cortex-overview-source.md          (Video 01 — All roles)
│   ├── 02-leadership-delivery-source.md      (Video 02 — Leaders + POs)
│   ├── 03-engineering-quality-source.md      (Video 03 — Engineers + QA)
│   └── 04-security-sre-source.md             (Video 04 — Security + SRE)
│
├── steering-prompts/           ← Paste ONE prompt into NotebookLM → Customize
│   ├── 01-steering.md
│   ├── 02-steering.md
│   ├── 03-steering.md
│   └── 04-steering.md
│
├── videos/                     ← Tutorial video prompts (separate series)
│   └── tutorials/
│
└── README.md                   ← This file
```

### Independent Update Contract

| Asset | Location | Update Independently | Effect on Other Layers |
|---|---|---|---|
| **Architecture diagrams** | `docs/assets/diagrams/*.md` | ✅ Yes | Zero — sources reference by filename |
| **Best practices YAML** | `cortex-registry/knowledge/best-practices/content/` | ✅ Yes | Zero — steering prompts cite rule IDs |
| **Source documents** | `sources/*.md` | ✅ Yes | Zero — steering prompts name file only |
| **Steering prompts** | `steering-prompts/*.md` | ✅ Yes | Zero — sources are standalone |

**Contract:** Diagram files update in place → source documents auto-reflect changes. Steering prompts reference source files by name only. No cascading edits required across layers.

---

## 🎬 Video Series Map

| Video | Title | Source File | Steering File | Narrator | Domain Colour |
|---|---|---|---|---|---|
| 01 | What Is CORTEX? | `01-cortex-overview-source.md` | `01-steering.md` | 🎙️ Female | Cyan `#00d4ff` |
| 02 | CORTEX for Leaders & Delivery | `02-leadership-delivery-source.md` | `02-steering.md` | 🎙️ Male | Purple `#7b61ff` |
| 03 | CORTEX for Engineering & Quality | `03-engineering-quality-source.md` | `03-steering.md` | 🎙️ Male | Cyan + Gold |
| 04 | CORTEX for Security & SRE | `04-security-sre-source.md` | `04-steering.md` | 🎙️ Female | Red + Amber |

---

## 🚀 Step-by-Step: Generating a Video

1. Go to [notebooklm.google.com](https://notebooklm.google.com)
2. Create a **new notebook**
3. Upload the matching `sources/0N-*.md` file as the sole source
4. In the Studio panel → **Video Overview** → **Customize**:
   - **Format:** `Cinematic` ← NOT Explainer or Brief
   - **Visual Style:** `Custom` ← paste visual style block from `steering-prompts/0N-steering.md`
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
| `02-diagram-architecture-mcp-gateway-architecture.md` | MCP gateway architecture | V01, V03 |
| `03-diagram-workflow-sdlc-pipeline.md` | SDLC workflow pipeline (7 phases) | V02, V04 |
| `04-diagram-audit-audit-fix-pipeline.md` | /audit fix pipeline (9 stages) | V02 |
| `05-diagram-workflow-tdd-cycle-and-fsm.md` | TDD cycle and workflow engine FSM | V03 |
| `06-diagram-governance-sweep-completeness-core-064.md` | Sweep completeness (CORE-064) | V02, V03 |
| `07-diagram-testing-testing-strategy-pyramid.md` | Testing strategy pyramid | V03 |
| `09-diagram-orchestration-request-sequence.md` | End-to-end request sequence | V01 |
| `11-diagram-intelligence-lens-analysis-pipeline.md` | LENS intelligence pipeline + Diamond | V01–V04 |
| `12-diagram-governance-convergence-gate-core-068.md` | Universal convergence gate (CORE-068) | V02, V03 |
| `13-diagram-orchestration-intent-classification-routing.md` | Intent classification and routing | V01 |
| `14-diagram-debugging-multi-stack-pipeline.md` | Multi-stack debug pipeline (8 strategies) | V03 |
| `15-diagram-governance-rule-enforcement-tiers.md` | Governance rule enforcement (4-tier) | V02, V04 |
| `17-diagram-security-threat-model-stride-analysis.md` | Threat Model Engine — STRIDE pipeline | V04 |
| `18-diagram-quality-analysis-engine-scoring-dashboard.md` | Quality Analysis Engine — scoring | V03 |
| `19-diagram-orchestration-po-change-intelligence-pipeline.md` | PO Change Intelligence Pipeline | V02 |
| `20-diagram-intelligence-document-ingest-pipeline.md` | Document Ingest Pipeline (5 components) | V01, V02, V04 |
| `21-diagram-governance-vacuum-source-protection.md` | Vacuum Source Protection | V04 |

---

## 🎨 Domain Colour Reference

| Video | Primary | Secondary | Background |
|---|---|---|---|
| 01 | Cyan `#00d4ff` | Purple `#7b61ff` | Navy `#0a0e27` |
| 02 | Purple `#7b61ff` | Emerald `#10b981` | Navy `#0a0e27` |
| 03 | Cyan `#00d4ff` | Gold `#FFD700` | Navy `#0a0e27` |
| 04 | Red `#ff4757` | Amber `#f39c12` | Navy `#0a0e27` |

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
| VBP-017 Narrator gender | `steering-prompts/` | F/M: V01=F, V02=M, V03=M, V04=F |
| VBP-018 No unexpanded acronyms | `sources/` | First-use expansion in `## Key Facts` |
| VBP-019 Colour intelligence | Both layers | Custom style + domain colour header |
