---
id: security-threat-model-stride-analysis
title: Threat Model Engine — STRIDE classification pipeline
purpose: Show how the Threat Model Engine maps entry points, data flows, and trust boundaries through STRIDE classification to produce a ranked threat catalogue.
audience:
  - Security Engineers
  - Software Developers
  - Business Leaders
source_of_truth:
  - cortex/orchestrators/domain/threat_model_engine.py
  - cortex-registry/workflows/templates/security/security-compliance-audit.yaml
last_verified: 2026-03-04
diagram_type: Security
render: ascii
render_html: true
d3_method: "d3.treemap() — STRIDE heatmap with DREAD colour encoding"
---

# Threat Model Engine — STRIDE Classification Pipeline

## From Codebase Surface to Ranked Threat Catalogue

```
 ═══════════════════════════════════════════════════════════════════════════════
  CORTEX THREAT MODEL ENGINE — AUTOMATED STRIDE ANALYSIS
 ═══════════════════════════════════════════════════════════════════════════════

  Target Codebase / API Surface
         │
         ├─── Entry Points (HTTP endpoints, CLI commands, message handlers)
         ├─── Data Flows (request→service→DB, external API calls)
         └─── Trust Boundaries (auth layers, network zones, privilege tiers)
                │
                ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │                     STRIDE CLASSIFICATION                            │
  │                                                                      │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                          │
  │  │    S     │  │    T     │  │    R     │                          │
  │  │ Spoofing │  │Tampering │  │Repudia- │                          │
  │  │          │  │          │  │  tion   │                          │
  │  │ Identity │  │  Data    │  │  Audit  │                          │
  │  │  fraud   │  │ modified │  │  trail  │                          │
  │  └────┬─────┘  └────┬─────┘  └────┬─────┘                          │
  │       │              │              │                                │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                          │
  │  │    I     │  │    D     │  │    E     │                          │
  │  │  Info    │  │ Denial   │  │Elevation │                          │
  │  │Disclo-  │  │   of     │  │   of     │                          │
  │  │  sure   │  │ Service  │  │Privilege │                          │
  │  │  Data   │  │ Resource │  │  Authz   │                          │
  │  │  leak   │  │ exhaust  │  │  bypass  │                          │
  │  └────┬─────┘  └────┬─────┘  └────┬─────┘                          │
  │       │              │              │                                │
  └───────┴──────────────┴──────────────┴────────────────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  DREAD SCORING (per threat)                                          │
  │                                                                      │
  │  D = Damage potential          (1–10)                                │
  │  R = Reproducibility           (1–10)                                │
  │  E = Exploitability            (1–10)                                │
  │  A = Affected users            (1–10)                                │
  │  D = Discoverability           (1–10)                                │
  │                                                                      │
  │  Composite DREAD score = mean(D,R,E,A,D)                            │
  └──────────────────────────────────┬───────────────────────────────────┘
                                     │
                                     ▼
  ┌──────────────────────────────────────────────────────────────────────┐
  │  RANKED THREAT CATALOGUE                                             │
  │                                                                      │
  │  CRITICAL (DREAD ≥ 8)  ████████████ → immediate mitigation           │
  │  HIGH     (DREAD ≥ 6)  ████████     → fix in current sprint          │
  │  MEDIUM   (DREAD ≥ 4)  █████        → schedule for next cycle        │
  │  LOW      (DREAD < 4)  ██           → accept or monitor              │
  │                                                                      │
  │  Each threat linked to OWASP reference + mitigation pattern          │
  └──────────────────────────────────────────────────────────────────────┘
```

## Integration Points

```
  Threat Model Engine
         │
         ├── Security Audit Workflow (Phase 6 — STRIDE gate)
         ├── Code Review Orchestrator (Pass 2 — security findings)
         ├── Governance Engine (CORE rules for security compliance)
         └── RCA Engine (post-incident threat model correlation)
```
