# Hands-On Tutorial Video Prompts

These prompts are for **Google Gemini Video Generator** and **NotebookLM Video Editor** and cover the **practical, hands-on** phase of the CORTEX learning journey. They are separated from the concept videos in `../` because they serve a fundamentally different purpose — they are **screen-recording-style walkthroughs**, not architectural explainers.

## When to Use These

Watch concept Videos 1–8 first to understand *what* CORTEX is and *how* it works. Then come here to learn *how to use it*.

Alternatively: if you just want to get running immediately, Tutorial 01 requires no prior knowledge.

---

## Tutorial Index

| # | File | Title | Duration | Audience | Prerequisites |
|---|------|-------|----------|----------|---------------|
| T1 | `tutorial-01-getting-started-installation.md` | Getting Started: Installation | 5 min | Everyone | None |
| T2 | `tutorial-02-getting-started-first-commands.md` | Getting Started: Your First Commands | 7 min | Engineers, PO | Tutorial 01 |
| T3 | `tutorial-03-getting-started-customization.md` | Getting Started: Customizing CORTEX | 8 min | Leads, Platform | Tutorials 01-02, Concept Videos 04 + 08 |
| T4 | `tutorial-04-building-a-feature-end-to-end.md` | Building a Feature End-to-End | 10 min | Engineers | Tutorials 01-02, Concept Videos 02 + 05 |
| T5 | `tutorial-05-debugging-with-cortex.md` | Debugging with CORTEX | 9 min | Engineers | Tutorial 01, Concept Video 03 |
| T6 | `tutorial-06-onboarding-a-repository.md` | Onboarding a New Repository | 8 min | Tech Leads, Platform | Tutorial 01, Concept Videos 03 + 04 |

**Total Tutorial Runtime:** ~47 minutes

---

## Depth Progression

```
Tutorial 1  ██░░░░░░░░  20%  Installation — step-by-step (reset from concept depth)
Tutorial 2  ████░░░░░░  40%  First commands — practical with explanations
Tutorial 3  ███████░░░  70%  Customization — real code, real rules, real MCP tools
Tutorial 4  ██████████  100% Full feature build — ticket to governed commit
Tutorial 5  ████████░░  80%  Debugging — 5-phase diagnostic pipeline
Tutorial 6  ███████░░░  70%  Repository onboarding — LENS + security + dashboard
```

---

## Relationship to Concept Videos

Tutorials are **not** a replacement for concept videos. They deliberately avoid re-explaining architecture. Where relevant, they forward-reference concept videos:

| Tutorial Action | Concept Video Reference |
|-----------------|------------------------|
| Installing MCP server | Video 06 — MCP Tools Deep Dive (explains *why* it works) |
| Running `/audit fix` | Video 07 — Audit Fix Pipeline (explains what each stage does) |
| Adding a governance rule | Video 04 — Governance in Action |
| Creating a workflow template | Video 08 — Workflow Template Engine (explains interpreter vs data) |
| Building a feature with TDD | Video 05 — TDD Mastery (explains the red/green/blue philosophy) |
| Using `/challenge` before coding | Video 02 — The Request Lifecycle (explains intent routing) |
| Running `/debug` pipeline | Video 03 — Intelligence Engine (explains LENS analysis) |
| Onboarding with `/onboard` | Video 03 — Intelligence Engine + Video 04 — Governance |

---

## Visual Identity

All tutorials use the same glassmorphism palette and motion style as concept videos. See `../README.md` for the full mandatory visual identity specification.

The tutorial videos differ visually in one way: they show **real VS Code UI** (simulated) as a PiP (picture-in-picture) overlay in the bottom-left corner throughout, showing the actual commands being typed in a terminal or Copilot Chat panel. This grounds the animation in reality.

---

*Separated from concept videos per learning architecture — 27 February 2026*
