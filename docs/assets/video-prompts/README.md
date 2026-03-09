# CORTEX Video Prompts — NotebookLM Cinematic Video Overview
**Updated:** 2026-03-09 | **Format:** NotebookLM Cinematic Video Overview
**Architecture Verified:** 350+ orchestrators · 40+ MCP tools · 60+ governance rules

---

## ⚠️ Critical: How NotebookLM Cinematic Video Works

NotebookLM **does not execute scene-by-scene production scripts**. It synthesizes content from your uploaded source documents and uses a short **steering prompt** (~300–700 characters) to guide focus, tone, and structure. Gemini 3 + Veo 3 make all visual and narrative decisions from your content.

### What you provide to NotebookLM:
1. **Source document** (`.md` file uploaded as a notebook source) — rich content describing the subject
2. **Steering prompt** (pasted into Customize → Steering Prompt) — concise guidance on focus and tone
3. **Visual style** (Custom description) — colour palette and visual identity

### What NotebookLM generates:
- Fluid cinematic animations (Veo 3)
- Narration (Gemini 3 — auto-selected, not scripted)
- Visual storytelling — dynamic, not static slides

---

## 📂 Directory Structure

```
video-prompts/
├── sources/                    ← Upload these into NotebookLM as sources
│   ├── 01-cortex-overview-source.md          # All roles (Video 01)
│   ├── 02-leadership-delivery-source.md      # Business Leaders + POs (Video 02)
│   ├── 03-engineering-quality-source.md      # Engineers + QA (Video 03)
│   └── 04-security-sre-source.md             # Security + SRE (Video 04)
│
├── steering-prompts/           ← Paste these into NotebookLM → Customize
│   ├── 01-steering.md         # Steering prompt + setup checklist for Video 01
│   ├── 02-steering.md         # Steering prompt + setup checklist for Video 02
│   ├── 03-steering.md         # Steering prompt + setup checklist for Video 03
│   └── 04-steering.md         # Steering prompt + setup checklist for Video 04
│
├── production-scripts/         ← Archive: detailed scene scripts for manual production
│   ├── 01-video-prompt-what-is-cortex.md
│   ├── 02-video-prompt-what-is-cortex-business-leaders.md
│   ├── 03-video-prompt-what-is-cortex-product-owners.md
│   ├── 04-video-prompt-what-is-cortex-software-engineers.md
│   ├── 05-video-prompt-what-is-cortex-security-engineers.md
│   ├── 06-video-prompt-what-is-cortex-quality-engineers.md
│   └── 07-video-prompt-what-is-cortex-site-reliability-engineers.md
│
└── videos/                     ← Tutorial video prompts (existing, unchanged)
    └── tutorials/
```

---

## 🎬 Video Series: 4-Video Structure

| Video | Title | Audience | Source | Steering |
|-------|-------|----------|--------|---------|
| 01 | What Is CORTEX? | All roles | `01-cortex-overview-source.md` | `01-steering.md` |
| 02 | CORTEX for Leaders & Delivery | CTOs, VPs, POs | `02-leadership-delivery-source.md` | `02-steering.md` |
| 03 | CORTEX for Engineering & Quality | Engineers, QA | `03-engineering-quality-source.md` | `03-steering.md` |
| 04 | CORTEX for Security & SRE | SecEng, SRE | `04-security-sre-source.md` | `04-steering.md` |

**Why 4 videos instead of 7:**
- Roles 02+03 (Business Leaders + POs) share identical concerns: ROI, predictable delivery, traceability
- Roles 04+06 (Engineers + QA) share identical tools: TDD, convergence gate, LENS, quality scoring
- Roles 05+07 (Security + SRE) share identical philosophy: defence-in-depth, institutional memory, operational confidence
- Fewer videos → deeper per-video content → better NotebookLM synthesis quality

---

## 🚀 Step-by-Step: Generating a Video in NotebookLM

### Prerequisites
- Google account with NotebookLM access (Cinematic requires Google AI Ultra subscription, 18+)
- Source `.md` file from `sources/` directory
- Steering prompt from matching `steering-prompts/` file

### Steps
1. Go to [notebooklm.google.com](https://notebooklm.google.com)
2. Create a new notebook
3. Upload the source `.md` file (drag and drop or Add Source)
4. In the Studio panel, click **Video Overview**
5. Click **Customize**:
   - **Format:** Cinematic
   - **Visual Style:** Custom → paste the visual style description from the steering prompt file
   - **Steering Prompt:** paste the steering prompt text (the text inside the ``` code block)
6. Click **Generate**
7. Wait 15–30 minutes (Cinematic takes longer than Explainer or Brief)
8. Review output — if focus is off, use the Fallback steering prompt in the same file

### Tips
- NotebookLM synthesizes from the source document, not from your steering prompt — keep the source rich
- Steering prompt should guide *what to emphasise*, not describe every scene
- Cinematic format gives Gemini 3 creative latitude — trust it to choose transitions and pacing
- If the video is too generic, add one specific constraint to the steering prompt (e.g., "open with a 3 AM incident")
- Generation time: Brief ~5 min · Explainer ~10 min · Cinematic ~30 min

---

## 🎨 Domain Colour Reference

| Video | Domain | Accent | Secondary |
|-------|--------|--------|-----------|
| 01 | All roles | Cyan `#00d4ff` | Purple `#7b61ff` |
| 02 | Leadership + Delivery | Purple `#7b61ff` | Emerald `#10b981` |
| 03 | Engineering + Quality | Cyan `#00d4ff` | Gold `#FFD700` |
| 04 | Security + SRE | Red `#ff4757` | Amber `#f39c12` |

---

## 📁 Production Scripts (Archive)

The `production-scripts/` directory contains the original 7-video scene-by-scene scripts. These are useful as:
- Reference for detailed scene concepts if doing manual production
- Visual inspiration catalogue for the "Visual Anchors" sections in each source document
- Detail reference when writing more specific steering prompts

They are **not** used directly by NotebookLM.

---

## 📋 VBP Compliance Notes

These videos target NotebookLM Cinematic — visual production is handled by Veo 3. VBP rules still apply as authoring intent for source content:

| Rule | Enforcement Mechanism |
|------|-----------------------|
| VBP-001 One Idea Per Source Section | Each source section covers one concept |
| VBP-002 Hook in 8s | Steering prompts open with the pain/problem |
| VBP-003 Narration ≠ slide | Source doc is content-rich, not bullet-list |
| VBP-006 Contrast storytelling | All sources lead with the pain, then the solution |
| VBP-012 Consistent visuals | Colour reference table maintained here |
| VBP-017 Narrator voice | Specified per steering prompt (F/M alternating: 01F, 02M, 03M, 04F) |
| VBP-018 Acronyms | All acronyms expanded on first use in source docs |
| VBP-019 Colour intelligence | Domain colour specified in source + custom visual style |
