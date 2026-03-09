# Video Prompt 07 — CORTEX for Site Reliability Engineers

---
**Series:** CORTEX — The Governed AI Engineering Partner
**Video:** 07 of 07 (Role Series)
**Title:** CORTEX for Site Reliability Engineers
**Subtitle:** Observability. Self-Healing. Operational Confidence.
**Audience:** SREs, DevOps Engineers, Platform Engineers — professionals who own uptime, incident response, and system health
**Duration:** 7–10 minutes
**Narrator:** 🎙️ Female — calm under pressure, operational clarity; speaks like an SRE during a controlled incident
**Generator:** Google Gemini Video Generator / NotebookLM Video Editor
**Domain Color:** Amber `#f39c12` (monitoring, alerting, operational awareness)
**Last Updated:** 2026-03-09
**VBP Rules Applied:** VBP-001 through VBP-019 (full compliance)

---

## 🎯 Learning Objective

SREs understand how CORTEX provides operational intelligence beyond traditional observability: health orchestration across 330+ components, self-healing vacuum pipelines, SQLite-backed audit trails, and root cause analysis that prevents incident recurrence.

---

## 🎬 Scene Sequence (7–10 min target)

### HERO INTRO (VBP-014 — 5s)
**Visual:** `#0a0e27` navy. Amber particles pulse like server heartbeats. Logo with amber glow. Title: "CORTEX for Site Reliability Engineers" → subtitle: "Observability. Self-Healing. Operational Confidence." Logo shrinks to watermark.

### Scene 1 — The Incident (90s) [VBP-002 hook, VBP-006 contrast]
**Visual:** Incident timeline: 02:47 AM — alert fires. Dashboard goes red. Three engineers join a war room. Logs scroll endlessly. Each engineer checks a different monitoring tool. Mean Time to Resolution counter ticks up: "MTTR: 4h 23m". Post-mortem reveals: "Same root cause as last month's incident."
**Narration:** It is 3 AM. Your pager fires. Three engineers join the call. You scroll through four monitoring tools, correlating logs, metrics, and traces. Four hours later, you find the root cause — and realise it is the same failure pattern from last month. Nobody documented the fix. Nobody updated the runbook. What if your system remembered?
**Animation:** War room scene fades to a single CORTEX terminal. MTTR counter reverses: "4h 23m → 12 minutes". RCA node glows: "Pattern recognised. Fix applied automatically." [VBP-016: bold **root cause**, **remembered**, **automatically**]

### Scene 2 — Understand: Health Orchestration (100s) [VBP-015 breadcrumb: ●○○]
**Visual:** System health dashboard — 15 orchestrator domain tiles arranged in a 5×3 grid. Each tile shows a health heartbeat. The HealthOrchestrator (centre tile, larger) sends pulse signals to all domains. Each responds: green heartbeat, amber warning, or red alert. A "System Health: 98.7%" banner animates at the top.
**Narration:** The Health Orchestrator continuously monitors all 15 orchestrator domains — 330+ components. Not just "is it running?" but "is it behaving correctly?" Health checks validate wiring contracts, MCP tool registration, governance rule loading, and intelligence pipeline responsiveness. You get a single health score — not 47 scattered dashboards.
**Animation:** Breadcrumb: "Health Orchestration" bright. Pulse signals radiate from centre tile to all 15 domains with ripple animation. Each tile responds with a heartbeat line. One tile flashes amber — zoom reveals: "MCP tool registry: 1 tool degraded". System health percentage ticks up as the issue self-resolves.

### Scene 3 — Empower: Self-Healing Pipelines (120s) [VBP-015 breadcrumb: ✅●○]
**Visual:** VacuumOrchestrator 8-stage pipeline animates as a conveyor system: Stage 1 (naming conventions — files rename themselves), Stage 2 (root clutter — files move to correct locations), Stage 3 (empty files — dissolve), Stage 4 (orphaned code — highlighted and archived), Stage 5 (markdown sprawl — consolidated), Stage 6 (digest cleanup), Stage 7 (build artefacts — swept), Stage 8 (OS artefacts — .DS_Store, __pycache__ vanish). Each stage has an animated icon.
**Narration:** The Vacuum Orchestrator runs an 8-stage cleanup pipeline autonomously. Naming violations correct themselves. Orphaned files archive. Build artefacts sweep. OS detritus vanishes. Seven SQLite databases enforce 30-day retention with automatic VACUUM. This is not a cron job — it is intelligent workspace hygiene that understands what can be safely removed.
**Animation:** Conveyor belt moves left-to-right. Each stage activates with a satisfying mechanical animation. Files transform: misnamed→renamed with morph effect. Orphans fade with archive stamp. .DS_Store files dissolve with sparkle. "Workspace Health: 100%" badge materialises. [VBP-016: bold **8 stages**, **self-healing**, **30-day retention**]

### Scene 4 — Build: RCA Memory + Audit Trail (120s) [VBP-015 breadcrumb: ✅✅●]
**Visual:** RCA Memory cycle: an incident enters → 4 methodology icons orbit it (Five-Whys, Fishbone, Fault-Tree, Causal-Chain) → the correct methodology activates → analysis tree builds → prevention rule generates → rule enters the knowledge base. Next time the same pattern appears: "Pattern matched. Prevention rule applied. Incident averted."
**Narration:** Four root cause analysis methodologies — Five-Whys, Fishbone, Fault-Tree, and Causal-Chain. CORTEX selects the right methodology based on the incident category. Each completed analysis generates a prevention rule that enters the institutional memory. Seven SQLite databases log every enforcement action, orchestrator trace, and governance decision. Your post-mortems become living documents that actively prevent recurrence.
**Animation:** Methodology icons spin into position. Analysis tree draws itself with branching animations. Prevention rule card generates with gold seal. Memory cycle loops: "emit → decay → promote → quarantine". Audit trail scrolls: timestamps, trace IDs, outcomes. Counter: "Incidents prevented by memory: 23". [VBP-016: bold **4 methodologies**, **prevention rule**, **living memory**]

### Scene 5 — Operational Confidence (60s) [VBP-011 strategic silence]
**Visual:** SRE dashboard — all green. MTTR: 12 minutes average. Recurrent incidents: 0. System health: 99.2%. The SRE's avatar sleeps peacefully. Pager icon: silent.
**Narration:** CORTEX does not eliminate incidents — it eliminates surprise. Your system remembers every failure. Every fix becomes a prevention rule. Every audit trail is seconds away. You stop firefighting and start engineering reliability.
**Animation:** [1.5s SILENCE]. Tagline: "Observability. Self-Healing. Operational Confidence." Logo fade.

---

## 🎨 VBP Compliance

| Rule | Status |
|------|--------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8s | ✅ 3 AM incident, MTTR clock |
| VBP-003 Narration ≠ slide | ✅ Dashboard reinforces, narration explains |
| VBP-006 Contrast | ✅ 4-hour MTTR → 12-minute MTTR |
| VBP-007 2-min cycles | ✅ Scene transitions every 90–120s |
| VBP-009 Signaling | ✅ Amber pulse on active health tile |
| VBP-011 Strategic Silence | ✅ After "engineering reliability" |
| VBP-012 Consistent visuals | ✅ Amber operational accent |
| VBP-014 Hero intro | ✅ 5s amber pulse |
| VBP-015 Breadcrumb | ✅ 3-stage progress bar |
| VBP-016 Bold keywords | ✅ Amber on operational terms |
| VBP-017 Female narrator | ✅ Odd-numbered |
| VBP-018 Acronyms expanded | ✅ SRE, MTTR, RCA, MCP, SQLite |
| VBP-019 Colour intelligence | ✅ Amber for monitoring, green for healthy |

## �� Audio
Dark ambient ~55 BPM. Tension in Scene 1 (pager sound effect), resolving to calm. Silence at peaceful sleep moment.

## 🧭 Mission Alignment
- **Understand Everything:** Scene 2 — Health Orchestrator, 15-domain monitoring, single health score
- **Empower Everyone:** Scene 3 — VacuumOrchestrator 8-stage pipeline, SQLite retention, autonomous hygiene
- **Build Fearlessly:** Scene 4 — 4 RCA methodologies, prevention rules, institutional memory
