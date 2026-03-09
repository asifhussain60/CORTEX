# Video Prompt 07 — What Is CORTEX? (Site Reliability Engineers)

---
**Series:** CORTEX — The Governed AI Engineering Partner
**Video:** 07 of 07 (Role Series)
**Title:** What Is CORTEX? For Site Reliability Engineers
**Subtitle:** Production-Grade Observability, Nine Resilience Patterns, WAL-Mode SQLite, and Self-Healing Infrastructure
**Audience:** Site Reliability Engineers, platform engineers, DevOps practitioners, infrastructure architects
**Duration:** 7–10 minutes
**Narrator:** 🎙️ Female (VBP-017 — odd-numbered video)
**Generator:** Google Gemini Video Generator / NotebookLM Video Editor
**Last Updated:** 2026-03-08
**VBP Rules Applied:** VBP-001 through VBP-019 (full compliance)
**Content Sources:** `01-platform`, `03-governance`, `06-mcp-tools`, `09-lifecycle`, `10-infrastructure`
**Series Context:** Video 01 introduced the CORTEX platform and its three mission pillars. This video does NOT repeat that introduction — it is the SRE-specific deep-dive: the three observability pillars (OpenTelemetry, Prometheus, structured JSON), nine production resilience patterns in detail, the seven-database WAL-mode SQLite architecture, MCP zero-config startup, and the self-healing maintenance script with drift detection.

---

## 🎯 Learning Objective

Site Reliability Engineers understand that CORTEX is itself production-grade infrastructure — three observability pillars (OpenTelemetry distributed tracing, Prometheus metrics, structured JSON logging), nine individually animated resilience patterns, seven WAL-mode SQLite stores with automatic 30-day retention, zero-config MCP stdio startup, and a self-healing maintenance script that detects and corrects architectural drift without manual intervention.

---

## 🎬 MANDATORY Hero Intro Slide (VBP-014 — 5 seconds)

**Scene:** Full-screen `#0a0e27` deep space navy. Floating blue (`#3b82f6`) and cyan particles — infrastructure/observability aesthetic.

**Centre frame:**
- `cortex-logo-512.png` — large, hero-scale, pulsing cyan glow
- **Above logo:** "What Is CORTEX?" — Space Grotesk Bold, `#ffffff`, 48px
- **Below logo:** "For Site Reliability Engineers — Built to the Standards It Enforces" — Inter Regular, `#a0a6c0`, 20px, typewriter reveal

**Hold 5 seconds → logo to watermark → Scene 1 fades in.**

---

## Scene 1 — The Hook: Does Your Tool Eat Its Own Cooking? (0:05 – 0:40)

**Visual (VBP-006 — contrast framing):**

Left column (dark, `rgba(255,68,68,0.06)` tint):
```
Most AI development tools:
❌  No distributed tracing
❌  No metrics endpoint
❌  No structured audit trail
❌  No crash recovery
❌  No circuit breakers
❌  No tamper detection
❌  No self-healing maintenance
```

Right column (dark, `rgba(0,255,136,0.06)` tint):
```
CORTEX:
✅  OpenTelemetry — end-to-end tracing
✅  Prometheus — 15+ pre-built metric series
✅  Tamper-evident audit trail (hash chaining)
✅  Crash recovery from checkpoint log
✅  Nine resilience patterns built-in
✅  Structured JSON logging + correlation IDs
✅  Self-healing maintenance script with drift detection
```

**Narration:**
> "An AI engineering tool that enforces production standards on your code — but has no observability, no resilience patterns, and no crash recovery of its own — is not eating its own cooking. CORTEX is production-grade software. The same standards it requires of your codebase are implemented in its own infrastructure. You can observe it, trace it, alert on it, recover it, and verify that nothing in its audit trail has been tampered with. CORTEX holds itself to the standard it sets."

**VBP-002:** Hook established within 8 seconds.
**VBP-011:** 2s silence at the column contrast moment.

---

## Scene 2 — Three Observability Pillars (0:40 – 1:25)

**Visual:**
Three glassmorphism cards in a row, blue (`#3b82f6`) top-border. Each reveals fully before the next.

**Card 1: Distributed Tracing (OpenTelemetry)**
```
trace_id: a3f9c2d1-7b44
│
├── cortex_orchestrate           [12ms]
│   ├── IntentRouter.classify   [8ms]  → TDD
│   ├── lens_analysis           [840ms] → 9 analysers
│   └── TDDOrchestrator.run     [1.2s]
│       ├── governance_gate     [22ms]  → PASS
│       └── tdd_enforce         [95ms]  → RED phase open
└── response_emit               [3ms]
Total: 2.2s | Status: ✅ OK
```

**Card 2: Prometheus Metrics**
```
cortex_request_duration_seconds{p50=1.2s, p95=3.8s, p99=5.1s}
cortex_governance_violations_total{rule="CORE-008", count=847}
cortex_test_execution_pass_rate{suite="golden", rate=1.0}
cortex_lens_analysis_duration_seconds{p50=0.8s}
cortex_circuit_breaker_state{component="llm_gateway", state="CLOSED"}
cortex_mcp_tool_invocations_total{tool="cortex_review", count=2847}
```

Label: `Pre-built Grafana dashboards included`

**Card 3: Structured JSON Logging**
```json
{
  "level": "ERROR",
  "trace_id": "a3f9c2d1",
  "session_id": "sess_847x",
  "operation": "governance_gate",
  "rule": "CORE-008-TDD",
  "outcome": "BLOCKED",
  "duration_ms": 22,
  "timestamp": "2026-03-08T14:22:07Z"
}
```
Label: `Correlation IDs on every log entry — no manual correlation`

**Narration:**
> "CORTEX exposes three observability pillars. OpenTelemetry traces every operation end-to-end — every tool invocation, every orchestrator execution, every governance check — giving you a complete picture of what happened, in what sequence, and at what latency, without manual log correlation. Prometheus exposes 15-plus metric series covering request rates, governance violations, test pass rates, and circuit breaker state — with pre-built Grafana dashboards. And every log entry carries a correlation identifier, so any log line traces back to the specific request and trace that produced it."

**VBP-009 (Signaling):** Each card highlights as its pillar is narrated; others dim to 40%.

---

## Scene 3 — Nine Resilience Patterns: Individual Detail (1:25 – 2:10)

**Visual:**
A 3×3 grid of glassmorphism pattern cards (blue border). Each card reveals individually as narrated, with a brief animation per pattern:

**Row 1:**

| Pattern | Icon | Animation | One-line description |
|---------|------|-----------|---------------------|
| Circuit Breaker | ⚡ | Breaker trips after 3 failures, resets after 60s | Stops cascading failures across dependent services |
| Retry with Backoff | 🔄 | Bar chart showing 1s → 2s → 4s + jitter | Exponential backoff with jitter prevents retry storms |
| Bulkhead | 🛡️ | Container partition animation | Resource pools isolated — failure in one cannot exhaust others |

**Row 2:**

| Pattern | Icon | Animation | One-line description |
|---------|------|-----------|---------------------|
| Graceful Degradation | ↘️ | Full result → partial result with advisory | Returns partial results when non-critical sub-systems fail |
| Rate Limiting | 🚦 | Counter filling to limit, then yellow warning | Per-tool and per-session limits prevent resource exhaustion |
| Crash Recovery | 💾 | Checkpoint log replay animation | Re-runs from last verified checkpoint after unexpected shutdown |

**Row 3:**

| Pattern | Icon | Animation | One-line description |
|---------|------|-----------|---------------------|
| Connection Pooling | 🔗 | Pool slots filling and releasing | Managed connections prevent exhaustion under concurrent load |
| Resource Tracking | 📈 | Memory gauge + file handle counter | Memory, handles, DB connections — surfaces leaks before failures |
| Tamper-Evident Audit | 🔒 | Hash chain link + break simulation | Cryptographic chaining — modification breaks chain, proving tampering |

**Narration:**
> "Nine production resilience patterns run in CORTEX's own infrastructure. Circuit breakers open after threshold failures, preventing cascade. Retry with exponential backoff — with randomised jitter — prevents retry storms under load. Bulkheads partition resource pools so a failure in one component cannot exhaust resources needed by another. Crash recovery uses the audit checkpoint log — after an unexpected shutdown, in-progress operations replay from the last verified record. These are the patterns your systems should implement. CORTEX models them by running them itself."

**VBP-010 (Analogy):** "Like a ship with compartmentalised hull sections — a breach in one compartment does not sink the ship. Bulkheads exist precisely because failures happen." Dark pill.

---

## Scene 4 — Seven SQLite Stores: WAL-Mode Architecture (2:10 – 2:55)

**Visual:**
A database architecture diagram (glassmorphism, blue domain colour). Seven SQLite database nodes connected to a central CORTEX runtime hub:

```
              CORTEX Runtime Hub
                     │
  ┌──────────────────┼──────────────────────┐
  │                  │                      │
traces.db         audit.db               rca.db
(primary trace)   (events & checks)      (root causes)
  │                  │                      │
govern.db         convs.db            wiring.db    intel.db
(scaffolder)      (sessions)          (contracts)  (traces)
```

Each database node expands on focus to show:

| Database | Key tables | WAL mode |
|----------|-----------|---------|
| `orchestrator-traces.db` | audit_sessions, workflow_runs, trace_events | ✅ WAL |
| `audit.db` | audit_events, governance_checks, phase_progress | ✅ WAL |
| `rca_store.db` | rca_analyses, prevention_rules, recurrence_events | ✅ WAL |
| `governance.db` | scaffolder_audit_log | ✅ WAL |
| `conversations.db` | conversations, turn_records | ✅ WAL |
| `wiring-audit.db` | validation_audit, contract_versions | ✅ WAL |
| `intelligence-audit.db` | intelligence_audit | ✅ WAL |

A WAL-mode explainer card (JetBrains Mono, blue border):
```
Write-Ahead Logging (WAL mode)
────────────────────────────────
Concurrent reads:  ✅ Without blocking writes
Write durability:  ✅ WAL synced before commit
Recovery:          ✅ WAL replay after crash
Lock contention:   ✅ Eliminated for read-heavy workloads
```

**Narration:**
> "CORTEX persists runtime state across seven SQLite databases — all running in WAL mode: Write-Ahead Logging. WAL mode enables concurrent reads and writes without locking — critical when LENS analysis, governance checks, and audit trail writes are all happening in parallel. The primary trace store records every orchestrator decision, governance gate outcome, and operation timestamp. Data older than 30 days is automatically pruned and VACUUMed by the maintenance script — preventing silent accumulation of stale records that degrade query performance."

---

## Scene 5 — MCP Server: Pylance-Style Zero-Config Startup (2:55 – 3:35)

**Visual:**
A VS Code workspace opens. No terminal command. Automatically:

```
CORTEX MCP Server — Auto-Start
────────────────────────────────
Transport:   stdio (Pylance-style — no network port)
Config:      .vscode/settings.json → github.copilot.chat.mcpServers.cortex
Status:      ✅ RUNNING
Tools:       36 registered
Startup:     1.2s from workspace open
```

Three verification methods shown:

```
Method 1 — Tool call: cortex_verify (op: mcp) → responds = running
Method 2 — Settings: .vscode/settings.json → key present = configured
Method 3 — Terminal: python3 -m cortex.mcp → no errors = healthy
```

A configuration card (glassmorphism, blue border):
```json
{
  "github.copilot.chat.mcpServers": {
    "cortex": {
      "command": "python3",
      "args": ["-m", "cortex.mcp"],
      "transport": "stdio",
      "cwd": "${workspaceFolder}"
    }
  }
}
```

**Narration:**
> "CORTEX uses a stdio-based Model Context Protocol transport — the same pattern as Pylance. It auto-starts when you open the workspace. No Docker. No exposed network ports. No manual server lifecycle. 36 tools are registered and available in Copilot Chat within 1.2 seconds of workspace open. The configuration is a single JSON block in `.vscode/settings.json`. Verification is one command. From an SRE perspective: it starts, it serves, it fails safely, and it recovers from the checkpoint log."

**VBP-018:** "MCP" expanded as "Model Context Protocol" on first use.

---

## Scene 6 — Self-Healing Maintenance: Drift Detection and Auto-Correction (3:35 – 4:15)

**Visual:**
A terminal card (JetBrains Mono, glassmorphism panel):

```bash
$ python3 scripts/refresh_prompt_suite.py
```

Output animates stage-by-stage:

```
[1/4] Introspecting live architecture...
      Orchestrators discovered: 296 ✅
      MCP tools registered: 36 ✅
      Governance YAMLs: 60+ ✅
      Tests collected: 20,565 ✅
[2/4] Running database cleanup (30-day retention)...
      orchestrator-traces.db: pruned 1,247 rows (>30 days) | VACUUM ✅
      rca_store.db: pruned 23 stale prevention rules | VACUUM ✅
      7 databases: VACUUM complete ✅
[3/4] Regenerating prompt suite from live state...
      copilot-instructions.md: updated ✅
      AGENT-INDEX.md: updated ✅
      27 prompt/agent files: validated ✅
[4/4] Drift detection...
      ⚠️  Drift: cortex-master.yaml line 47 references dissolved package 'cortex_brain'
           Actual: 'cortex' (canonical) → auto-corrected ✅
      No other drift detected ✅

COMPLETE — prompt suite current with live architecture
```

**Narration:**
> "CORTEX includes a self-healing maintenance script that runs three operations in sequence: introspects the live architecture to verify counts match documentation, prunes and VACUUMs all seven SQLite databases on a 30-day retention policy, and regenerates every prompt and agent file from the current codebase state — detecting and correcting any drift between what the documentation says and what the live system is. Run it after every significant change. No manual intervention. Drift is not a condition that accumulates silently — it is detected and surfaced immediately."

**VBP-013 (Business Book):** Callout: *"Hope is not a strategy."* — Betsy Beyer, **Site Reliability Engineering**. Dark pill.

---

## Scene 7 — Circuit Breaker Simulation: Seeing Resilience in Action (4:15 – 4:55)

**Visual:**
A live simulation of the circuit breaker pattern:

```
LLM Gateway — Circuit Breaker State Machine
────────────────────────────────────────────
State: CLOSED (normal)
  Request 1:  ✅ 1.2s
  Request 2:  ✅ 0.9s
  Request 3:  ❌ TIMEOUT (5s)
  Request 4:  ❌ TIMEOUT (5s)
  Request 5:  ❌ TIMEOUT (5s)

Threshold reached (3 consecutive failures)
State: OPEN → immediate rejection, no wait
  Request 6:  ⚡ REJECTED (0ms) — circuit open
  Request 7:  ⚡ REJECTED (0ms)

Recovery timer: 60s elapsed
State: HALF-OPEN → probe request
  Probe:      ✅ 1.1s → SUCCESS

State: CLOSED → normal operation restored
  Request 8:  ✅ 1.0s
```

A Prometheus metric card alongside:
```
cortex_circuit_breaker_state_changes_total{
  component="llm_gateway",
  from="CLOSED", to="OPEN"
} 3
```

**Narration:**
> "The circuit breaker pattern is one of the nine resilience patterns CORTEX implements in its own infrastructure. This is what it looks like in operation: three consecutive timeouts trip the breaker. Subsequent requests are rejected immediately — zero latency — preventing the caller from waiting on a known-failing service and freeing capacity for other operations. After the recovery period, a probe request tests whether the dependency has recovered. If it succeeds, the breaker closes. If it fails, the timer resets. This is exactly the pattern CORTEX recommends when its LENS analysis identifies a dependency without circuit breaker protection in your codebase."

---

## Scene 8 — SRE Operational Dashboard: CORTEX as a Service (4:55 – 5:35)

**Visual:**
A Grafana-style dashboard simulation (dark theme, blue domain):

```
CORTEX Operational Dashboard
─────────────────────────────────────────────────────────────────
Request Rate:          847 req/hr  ↑ +12%
P50 Latency:          1.2s         → stable
P99 Latency:          5.1s         ↑ +0.3s (within SLO)
Error Rate:           0.12%        ↓ improving
Circuit Breaker:      ✅ CLOSED    (0 trips in 24h)
Governance Violations: 3           (all in dev — none production)
Golden Test Suite:    ✅ 847/847   (0 regressions)
DB Health:            ✅ 7/7 WAL   (avg query: 2.1ms)
Active Sessions:      14
MCP Tool Invocations: 2,847 today
```

SLO card (glassmorphism, cyan border):
```
SLO Targets — Current Status
──────────────────────────────
Request success rate:  99.88% ✅ (target: 99.5%)
P99 response:         5.1s ✅ (target: <8s)
Audit trail integrity: 100% ✅ (0 hash violations)
```

**Narration:**
> "CORTEX exposes enough telemetry to be operated as a service with genuine SLOs. Request rate, error rate, latency percentiles, circuit breaker state, governance violation rate, golden test status, and database query latency — all visible in the pre-built Grafana dashboard. The audit trail integrity metric is unique to CORTEX: it tracks whether any hash-chain violation has been detected, providing a continuous tamper signal. When CORTEX governs your systems, you can govern CORTEX in turn."

---

## Scene 9 — Vision: Infrastructure That Holds Itself Accountable (5:35 – 6:05)

**Visual:**
Full-screen dark navy. A quote card — glassmorphism, blue top-border:

> *"Hope is not a strategy. Reliability is not a coincidence."*
> — Betsy Beyer, **Site Reliability Engineering**

Below: a second card:

> **"CORTEX does not hope your code will be reliable. It enforces the conditions that make reliability structurally probable."**

**AUDIO: Strategic Silence — 2 seconds.**

**Narration:**
> "Production reliability is not achieved by applying more effort. It is achieved by building systems where failure modes are understood, isolated, and recovered from automatically. CORTEX is built to those principles — and it enforces them in every codebase it governs."

---

## Scene 10 — Call to Action (6:05 – 6:20)

**Visual:**
Single centred card, glassmorphism, blue border:

> **"OpenTelemetry. Prometheus. Nine resilience patterns. WAL-mode SQLite. Self-healing maintenance. Built to the standard it enforces."**

Below: `→ Explore the CORTEX infrastructure guide for SREs` in `#00d4ff`.
Breadcrumb (bottom): `07/07 — Site Reliability Engineers | ✅ Series Complete`

**Narration:**
> "CORTEX is not a prototype that assumes nothing will go wrong. It is production-grade infrastructure — built to the same standards it enforces on your code. When you adopt CORTEX, you add a co-author that holds itself accountable by the same measures it applies to your systems."

---

## 🎬 Closing Title Card

`cortex-logo-512.png` hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.
Series complete badge: `✅ Role Series — 07/07 Complete` in `#00ff88`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ Contrast columns Scene 1, 0:07 |
| VBP-003 Narration ≠ slide text | ✅ Narration explains the operational significance; slides show data |
| VBP-004 Progressive disclosure | ✅ Resilience grid reveals card-by-card; circuit breaker states animate sequentially |
| VBP-005 Z/F pattern | ✅ Left column pain → right column solution; database hub layout |
| VBP-006 Contrast storytelling | ✅ "No observability" vs "full observability" Scene 1 |
| VBP-007 2-min visual cycles | ✅ New concept every scene |
| VBP-008 Title + duration + chapters | ✅ Intro slide + phase breadcrumbs |
| VBP-009 Signaling | ✅ Observability cards dim when inactive; circuit breaker state machine colour-coded |
| VBP-010 Analogy | ✅ Ship compartments analogy Scene 3; dark pill |
| VBP-011 Strategic silence | ✅ 2s at contrast column Scene 1; 2s after Beyer quote Scene 9 |
| VBP-012 Consistent visual language | ✅ Blue infrastructure domain colour throughout |
| VBP-013 Business Book | ✅ Betsy Beyer (SRE Book) Scene 6 and Scene 9 |
| VBP-014 Hero intro slide | ✅ `cortex-logo-512.png`, 5 seconds |
| VBP-015 Breadcrumb | ✅ Series completion breadcrumb on closing card |
| VBP-016 Bold key words | ✅ Blue highlights on infrastructure terms |
| VBP-017 Female narrator | ✅ Odd-numbered video |
| VBP-018 No unexpanded acronyms | ✅ MCP, WAL, SLO, SRE, VACUUM, TDD, OTEL, JSON, P50/P99, SAST, CVE all expanded |
| VBP-019 Strategic colour | ✅ Blue (`#3b82f6`) for SRE/infrastructure domain |

---

## 🎵 Audio Direction

- **Background:** Steady infrastructure ambient — low-frequency hum, slow pulse, data-centre feel
- **Contrast column reveal (Scene 1):** Muted tones left column → clean ascending tones right column; 2s absolute silence at contrast moment
- **Observability pillar cards (Scene 2):** Soft chime per card — systematic, methodical
- **Resilience pattern grid (Scene 3):** Individual click-in per card — precision mechanical feel; Bulkhead gets a subtle "seal" sound
- **Circuit breaker trips (Scene 7):** Sharp alert tone at state change; fast "rejected" clicks for OPEN state; clean tone at recovery
- **Database node connections (Scene 4):** Soft pulse per link in architecture diagram
- **MCP server online (Scene 5):** Single "system ready" ascending tone
- **Maintenance script phases (Scene 6):** Click per phase completion; resonant final chime at COMPLETE
- **Beyer quote silence (Scene 9):** Absolute silence — 2 full seconds, no music, no FX
- **Narration style:** Technical, confident, evidence-first. 138 wpm — SRE peer-to-peer voice. Zero marketing language. Every claim supported by the visual data shown.


**Visual (VBP-006 — contrast framing):**

Left column (dark, `rgba(255,68,68,0.06)` tint):
```
Most AI development tools:
❌  No distributed tracing
❌  No metrics endpoint
❌  No audit trail
❌  No crash recovery
❌  No circuit breakers
❌  No tamper detection
```

Right column (dark, `rgba(0,255,136,0.06)` tint):
```
CORTEX:
✅  OpenTelemetry — end-to-end tracing
✅  Prometheus metrics — pre-built dashboards
✅  Tamper-evident audit trail (hash chaining)
✅  Crash recovery from checkpoint log
✅  Nine resilience patterns built-in
✅  Structured JSON logging with correlation IDs
```

**Narration:**
> "An AI engineering tool that enforces production standards on your code — but has no observability, no resilience patterns, and no audit trail of its own — is not eating its own cooking. CORTEX is production-grade software. The same standards it requires of your codebase are applied to its own infrastructure. You can observe it, trace it, alert on it, and recover it — exactly the way it expects you to build your systems."

**VBP-002:** Hook established within 8 seconds.
**VBP-011:** 1.5s silence at the column contrast moment.

---

## Scene 2 — Three Observability Pillars (0:28 – 1:05)

**Visual:**
Three glassmorphism cards in a row, blue (`#3b82f6`) top-border, staggered entry:

**Card 1: Distributed Tracing**
- Icon: 🔍
- JetBrains Mono trace example:
  ```
  trace_id: a3f9c2d1
  cortex_orchestrate → classify_intent → lens_analysis
    → governance_gate → tdd_orchestrator
  Duration: 847ms | Status: OK
  ```
- Label: `OpenTelemetry — end-to-end, every operation`

**Card 2: Prometheus Metrics**
- Icon: 📊
- Metric list (Inter, 13px):
  ```
  cortex_request_duration_seconds
  cortex_governance_violations_total
  cortex_test_execution_pass_rate
  cortex_lens_analysis_duration_seconds
  cortex_circuit_breaker_state_changes
  ```
- Label: `Pre-built Grafana dashboards included`

**Card 3: Structured Logging**
- Icon: 📋
- JSON log snippet (JetBrains Mono, `rgba(26,31,58,0.9)` panel):
  ```json
  {
    "level": "ERROR",
    "trace_id": "a3f9c2d1",
    "session_id": "sess_847x",
    "operation": "governance_gate",
    "rule": "CORE-008-TDD",
    "outcome": "BLOCKED",
    "timestamp": "2026-03-08T14:22:07Z"
  }
  ```
- Label: `Correlation IDs on every log entry`

**Narration:**
> "CORTEX exposes three observability pillars. OpenTelemetry traces every operation end-to-end — every tool call, every orchestrator execution, every governance check — giving you a complete picture of what happened and in what sequence without log correlation. Prometheus metrics cover request rates, governance violations, test pass rates, and circuit breaker state changes — with pre-built Grafana dashboards included. And all logging uses structured JSON with correlation identifiers, so every log entry traces back to the specific request that produced it."

**VBP-009 (Signaling):** Each card highlights as its pillar is narrated; others dim to 40%.

---

## Scene 3 — Nine Resilience Patterns (1:05 – 1:40)

**Visual:**
A 3×3 grid of glassmorphism pattern cards (blue border). Each card reveals as narrated:

| Pattern | Icon | One-line description |
|---------|------|---------------------|
| Circuit Breaker | ⚡ | Stops calls to failing services after threshold — prevents cascade failures |
| Retry with Backoff | 🔄 | Exponential backoff + jitter — prevents retry storms |
| Bulkhead | 🛡️ | Resource partitioning — failure in one component cannot exhaust others |
| Graceful Degradation | ↘️ | Partial results when non-critical sub-components fail |
| Rate Limiting | 🚦 | Per-tool and per-operation limits — prevents resource exhaustion |
| Crash Recovery | 💾 | Checkpoint log recovery after unexpected shutdown |
| Connection Pooling | 🔗 | Managed DB and service connections — prevents exhaustion under load |
| Resource Tracking | 📈 | Memory, file handles, DB connections — surfaces leaks before failures |
| Tamper-Evident Audit | 🔒 | Cryptographic hash chaining — modification breaks the chain |

**Narration:**
> "CORTEX implements nine production-grade resilience patterns in its own infrastructure — and these same patterns are modelled in its knowledge base as recommendations for the codebases it governs. Circuit breakers stop cascade failures. Bulkheads ensure a failure in one component cannot consume resources needed by others. Crash recovery uses the audit trail as a checkpoint log — after an unexpected shutdown, operations in progress recover from the last recorded checkpoint. These are not aspirational patterns. They are running in CORTEX right now."

**VBP-010 (Analogy):** "Like a ship with compartmentalised hull sections — a breach in one compartment does not sink the ship." Dark pill for Bulkhead pattern.

---

## Scene 4 — The Audit Database: Seven SQLite Stores (1:40 – 2:10)

**Visual:**
A database architecture diagram (glassmorphism, blue domain colour). Seven nodes connected to a central CORTEX runtime hub:

```
                    CORTEX Runtime
                          |
    ┌──────┬──────┬───────┼───────┬──────┬──────┐
    │      │      │       │       │      │      │
 traces  audit  rca   govern  convs  wiring  intel
  .db    .db   .db     .db    .db    .db    .db
```

Each database node shows a tooltip card on focus:

| Database | Tables | Purpose |
|----------|--------|---------|
| `orchestrator-traces.db` | audit_sessions, workflow_runs, trace_* | Primary trace store |
| `audit.db` | audit_events, governance_checks | Audit events |
| `rca_store.db` | rca_analyses, prevention_rules | Root cause storage |
| `governance.db` | scaffolder_audit_log | Scaffolder audit |
| `conversations.db` | conversations, turn_records | Session state |
| `wiring-audit.db` | validation_audit | Contract validation |
| `intelligence-audit.db` | intelligence_audit | Intelligence traces |

All use SQLite with WAL mode — caption card: `"Write-Ahead Logging — concurrent reads without locking."` — JetBrains Mono, blue border.

**Narration:**
> "CORTEX persists runtime state across seven SQLite databases using write-ahead logging mode — enabling concurrent reads and writes without locking. The primary trace store records every orchestrator decision, governance gate outcome, test execution result, and operation timestamp. Data older than 30 days is automatically pruned and VACUUMed by the self-healing maintenance script — preventing the silent accumulation of stale data."

---

## Scene 5 — MCP Server: Zero-Config Startup (2:10 – 2:40)

**Visual:**
A VS Code workspace opens (animation simulation). Automatically, without any terminal command:

```
CORTEX MCP Server
─────────────────
Transport: stdio (Pylance-style — auto-detected by VS Code)
Status: ✅ RUNNING
Tools registered: 36
Startup time: 1.2s
Config: .vscode/settings.json → github.copilot.chat.mcpServers.cortex
```

A verification flow animates:

Developer types `cortex_verify` in Copilot Chat → CORTEX responds → Green badge: `MCP active`.

Three verification paths shown:
1. `cortex_verify` in chat → response = MCP running
2. Check `.vscode/settings.json` → key present = configured
3. `python3 -m cortex.mcp` in terminal → no import errors = healthy

**Narration:**
> "CORTEX uses a stdio-based Model Context Protocol transport — the same pattern as Pylance. It starts automatically when you open the workspace. No Docker. No exposed network ports. No manual server startup. 36 tools are registered and available in Copilot Chat within 1.2 seconds of workspace open. Verification is a single command: `cortex_verify`. If it responds, the gateway is active."

**VBP-018:** "MCP" expanded as "Model Context Protocol" on first use.

---

## Scene 6 — Self-Healing: The Maintenance Script (2:40 – 3:10)

**Visual:**
A terminal card (JetBrains Mono, glassmorphism panel `rgba(26,31,58,0.9)`):

```bash
$ python3 scripts/refresh_prompt_suite.py
```

Output animates line by line:

```
[1/4] Introspecting live architecture...
      Orchestrators: 296 ✅
      MCP tools registered: 36 ✅
      Governance YAMLs: 60+ ✅
[2/4] Running database cleanup...
      orchestrator-traces.db: pruned 847 rows (>30 days)
      rca_store.db: pruned 23 stale prevention rules
      VACUUM complete: 7 databases
[3/4] Regenerating prompt suite...
      copilot-instructions.md: updated ✅
      AGENT-INDEX.md: updated ✅
[4/4] Drift detection...
      No documentation drift detected ✅
COMPLETE — prompt suite is current with live architecture
```

A drift detection alert card (amber, simulation):
```
⚠️ Drift detected: cortex-master.yaml references 'cortex_brain'
   Actual package: 'cortex' (canonical)
   Action: Update reference → auto-corrected ✅
```

**Narration:**
> "CORTEX includes a self-healing maintenance script that introspects the live architecture, prunes stale database records with automatic VACUUM, and regenerates all prompt and agent files to match the current codebase state — with zero manual intervention. Run it after every significant change. Drift between documentation and live architecture is detected and surfaced before it becomes a production inconsistency."

**VBP-013 (Business Book):** Callout: *"Reliability is a feature — and features require maintenance."* — Betsy Beyer, **Site Reliability Engineering**. Dark pill.

---

## Scene 7 — Call to Action (3:10 – 3:25)

**Visual:**
Single centred card, glassmorphism, blue border:

> **"OpenTelemetry tracing. Prometheus metrics. Nine resilience patterns. Tamper-evident audit. Self-healing maintenance. Built to the standard it enforces."**

Below: `→ Explore the CORTEX infrastructure guide` in `#00d4ff`.
Breadcrumb (bottom): `07/07 — Site Reliability Engineers | Series Complete ✅`

**Narration:**
> "CORTEX is production-grade software — not a prototype that assumes nothing will go wrong. The observability, resilience patterns, and audit infrastructure it requires of your systems are the same ones it runs on. When you adopt CORTEX, you are not just adding a development tool. You are adding a co-author who holds itself to the same standard it holds your code."

---

## 🎬 Closing Title Card (3:25 – 3:30)

CORTEX logo hero-scale. Tagline: **"CORTEX — Cognitive Real-Time Execution"** — Inter, `#a0a6c0`.
Series complete badge: `✅ Role Series — 07/07 Complete` in `#00ff88`.

---

## 🎨 Visual Identity Compliance Checklist

| Rule | Applied |
|------|---------|
| VBP-001 One Idea Per Frame | ✅ |
| VBP-002 Hook in 8 seconds | ✅ Contrast columns at 0:07 |
| VBP-003 Narration ≠ slide text | ✅ |
| VBP-004 Progressive disclosure | ✅ Resilience pattern grid reveals one-by-one |
| VBP-005 Z/F pattern | ✅ Left column pain → right column solution |
| VBP-006 Contrast storytelling | ✅ No observability vs full observability |
| VBP-007 2-min visual cycles | ✅ |
| VBP-008 Title + duration + chapters | ✅ |
| VBP-009 Signaling | ✅ Observability pillar cards dim when inactive |
| VBP-010 Analogy | ✅ Ship compartments analogy for Bulkhead |
| VBP-011 Strategic silence | ✅ 1.5s at contrast column reveal |
| VBP-012 Consistent visual language | ✅ Blue infrastructure domain colour throughout |
| VBP-013 Business Book | ✅ Betsy Beyer SRE quote Scene 6 |
| VBP-014 Hero intro slide | ✅ |
| VBP-015 Breadcrumb | ✅ Series breadcrumb closing card |
| VBP-016 Bold key words | ✅ |
| VBP-017 Female narrator | ✅ Odd-numbered video |
| VBP-018 No unexpanded acronyms | ✅ MCP, WAL, VACUUM, SRE, TDD, JSON expanded |
| VBP-019 Strategic colour | ✅ Blue (`#3b82f6`) for SRE/infrastructure domain |

---

## 🎵 Audio Direction

- **Background:** Steady infrastructure ambient — low-frequency hum with subtle pulse, data-centre feel
- **Column contrast reveal (Scene 1):** Muted tones for red column → clean ascending tones for green column
- **Observability pillar cards (Scene 2):** Soft chime per card — systematic, methodical
- **Resilience pattern grid (Scene 3):** Subtle click-in per pattern card — precision mechanical feel
- **Database architecture reveal (Scene 4):** Node graph connection sound — soft pulse per link
- **MCP server startup (Scene 5):** "System online" ascending tone — readiness signal
- **Maintenance script completion (Scene 6):** Satisfying completion chime per phase, then resonant final chime
- **Narration style:** Technical, confident, peer-to-peer SRE voice. 140 wpm. Evidence-first — no marketing language. Calibrated for engineers who trust systems that can explain themselves.
